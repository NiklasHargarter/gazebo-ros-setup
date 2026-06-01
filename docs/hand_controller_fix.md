# Hand Control — Problems & Ground-Up Fix Plan

Status: diagnosis complete. Partial patches applied (uncommitted). Right hand still
broken. Ground-up rework needed — do in fresh session, intensive changes OK.

Affected pkg: `core_ws/src/hugo_moveit_config`.

## Goal

Reliable position control of both hands (20 joints each) + arms + head in Gazebo
sim, so high-level skills (`close_hand`, `open_hand`, `point_at`, `grasp`) can be
built on top. Real-robot Dynamixel path must keep working too.

## Symptom history

- Hand joints accept `FollowJointTrajectory` goals, return `error_code=0`
  (SUCCESSFUL), but joints do not move in Gazebo.
- Arms + head + base drive work.
- After partial fixes (below): **left hand works reliably, right hand frozen** —
  reproducible this session, worked ~1 of 3 launches earlier. Ordering-dependent.

## Root cause (architectural)

`config/hugo_mobile_manipulation.ros2_control.xacro` declares **6 separate
`<ros2_control type="system">` blocks**:

| Block | Joints |
|-------|--------|
| `${name}` (HugoMobileManipulationSystem) | base / wheels |
| `L_arm_dxl` | 7 left arm |
| `R_arm_dxl` | 7 right arm |
| `Head_dxl` | 2 neck |
| `L_Hand` | 20 left fingers |
| `R_Hand` | 20 right fingers |

Each block, under `<xacro:if use_sim>`, instantiates its **own**
`gz_ros2_control/GazeboSimSystem` plugin instance. So sim runs **6 independent
GazeboSimSystem hardware interfaces** inside one Gazebo model.

This layout exists because on the **real robot** each block maps to a separate
Dynamixel USB bus (`/dev/ttyUSB*`, distinct baud/IDs) — `dynamixel_hardware_interface/DynamixelHardware`.
Correct for hardware. Wrong for sim.

gz_ros2_control's GazeboSimSystem expects (and is best-tested as) **one system per
model**. Multiple instances race on Gazebo's ECS joint write each update tick. Some
instances' position writes land, others get silently dropped. Which ones win is
ordering/timing dependent → flaky, per-launch-variable hand actuation. Left usually
wins, right usually loses (loaded last).

`ros2 control list_hardware_components` shows R_Hand `active`, joints `claimed`,
`SUCCESSFUL` init — framework layer is fine. Failure is at the Gazebo write layer.

## Secondary problems found (already patched, uncommitted)

These were real bugs on top of the architectural one. Fixes stand, but insufficient
alone.

1. **Dual command interface on finger joints.** Every finger joint declared both
   `<command_interface name="position"/>` and `name="effort"`. GazeboSimSystem
   claimed effort, leaving position writes orphaned. → Stripped all `effort`
   command+state interfaces from 40 finger joints. `.bak` left by sed.

2. **`is_async="true"`** on `<ros2_control name="L_Hand">` and `R_Hand`. Runs
   hardware read/write off the controller_manager update loop; races GazeboSimSystem
   ECS update. Arm blocks had no `is_async`. → Removed from both hand blocks.

3. **`right_hand_controller` used `command_interfaces: [effort]`** in
   `config/mobile_manipulation_controller_manager.yaml` while `left_hand_controller`
   used `position`. effort JTC needs per-joint PID gains (none declared) → zero
   torque output. → Changed right to `position`.

## Why effort "worked" in debug but position didn't

`JointGroupEffortController` writing the effort interface directly DID move joints
(tested left hand → fingers slammed to limits). Proves Gazebo physics + joint
articulation are fine. So problem is specifically **position-command writes from
GazeboSimSystem not reaching some joints**, not dead joints.

## Other latent issues (lower priority)

- **elb_tilt limits asymmetric/one-sided.** `l_elb_tilt` URDF limit `[0, 1.57]`,
  `r_elb_tilt` `[-1.57, 0]`. Bend sign must mirror per arm. Some `joint_limits.yaml`
  arm entries lack position limits while URDF has them.
- **`l_sh_pan`, `l_elb_tilt` did not reach commanded targets** in arm test — clipped.
  Verify URDF vs `joint_limits.yaml` vs SRDF consistency.
- **SRDF end-effector warning:** move_group logs `Could not identify parent group for
  end-effector 'L_hand' / 'R_Hand'`. SRDF end-effector `parent_group` not set. Blocks
  MoveIt grasp/attach later.
- **No `open`/`closed` named hand poses** in `hugo_v2_mobile_manipulation.srdf`. Only
  per-finger `init`. Needed for clean MoveIt grasp API.
- **20 DOF per hand, fully independent.** Heavy to command + plan. Consider coupling
  (mimic joints) PIP/DIP per finger, or a reduced grasp synergy, once actuation solid.

## Recommended fix — ground up

### 1. Split sim vs real hardware cleanly (primary fix)

Restructure the xacro so **sim emits ONE GazeboSimSystem** owning all joints, while
**real hardware keeps the 6 Dynamixel blocks**.

```xml
<xacro:if value="${use_sim}">
  <ros2_control name="HugoSim" type="system">
    <hardware>
      <plugin>gz_ros2_control/GazeboSimSystem</plugin>
    </hardware>
    <!-- ALL joints here: wheels, both arms, head, both hands -->
    <!-- position command + position/velocity state, no effort -->
  </ros2_control>
</xacro:if>
<xacro:unless value="${use_sim}">
  <!-- existing 6 Dynamixel blocks unchanged -->
</xacro:unless>
```

Factor joint lists into xacro macros so they are written once and reused by both
branches (avoid 2× duplication of 56 joints). One macro per chain emitting just the
`<joint>` interface entries; call them inside the sim block and inside each real block.

This removes the multi-system race entirely. Single writer → deterministic.

### 2. Confirm position control mode in gz_ros2_control

With one system, verify position commands actuate without PID tuning. If joints
sluggish/soft, add `gz_ros2_control` position PID via the controller_manager
parameter file or per-joint `<param>` in the sim block. Test, do not add preemptively
([[feedback_minimal_patches]]).

### 3. Keep controllers as-is

`joint_trajectory_controller` per chain (`L_arm`, `R_arm`, `Head`, `left_hand`,
`right_hand`) with `position` command interface is correct. No change needed once the
hardware layer is single-system. Drop the unused `left_effort_controller` /
`right_effort_controller` from the YAML unless a torque demo is wanted.

### 4. Fix SRDF end-effectors + add named poses

Set `parent_group` on each `<end_effector>`. Add `open` and `closed`
`<group_state>` for each hand group (or one combined hand group per side instead of 5
per-finger groups). Enables `move_group.set_named_target("closed")`.

### 5. Audit joint limits

Reconcile URDF `<limit>` vs `joint_limits.yaml` vs SRDF. Document bend directions.
Decide neutral/home pose that is collision-free and not at a limit.

### 6. Then build the SDK layer

Once both hands actuate deterministically: `HugoClient.open_hand/close_hand/
point_at/grasp` on top of FollowJointTrajectory action clients (see
[[project_demo_roadmap]] session 3).

## Verification checklist for the rework

Run after each change, fresh launch each time (sim state degrades across long runs):

```bash
# both hands must move, every launch, not 1-in-3
ros2 control list_hardware_components          # all active, single sim system
ros2 control list_hardware_interfaces | grep finger   # position claimed, no effort
# action goal both hands, check /joint_states delta > 0 for all 40 finger joints
```

Repeat launch 5×. Pass = both hands actuate all 5.

## Repro / debug recipes

```bash
# send hand goal
ros2 action send_goal /right_hand_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [finger_r_joint6], points: [{positions: [1.0], time_from_start: {sec: 2}}]}}"

# prove physics OK via direct effort (debug only)
ros2 control set_controller_state right_hand_controller inactive
ros2 service call /controller_manager/configure_controller \
  controller_manager_msgs/srv/ConfigureController "{name: right_effort_controller}"
ros2 control set_controller_state right_effort_controller active
ros2 topic pub --once /right_effort_controller/commands \
  std_msgs/msg/Float64MultiArray "{data: [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]}"
```

## Demo loop script

`core_ws/motion_loop.py` — bends both elbows, closes/opens both hands (incl. thumb),
straightens, loops. Works for left hand + both elbows now; right hand blocked until
rework. Keep for post-fix video.

## Files touched (uncommitted, partial)

- `config/hugo_mobile_manipulation.ros2_control.xacro` — stripped finger effort
  interfaces, removed `is_async`.
- `config/mobile_manipulation_controller_manager.yaml` — right hand effort→position.
- `core_ws/motion_loop.py` — demo loop (new).

Decide: keep partial patches as base for rework, or revert and start the single-system
restructure clean. Recommend keep — they are correct and reduce noise.
