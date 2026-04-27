# Tutorial: A Sim-Swappable Robot (Gazebo ↔ Isaac Sim ↔ Real)

A follow-along learning project. You will build a tiny "camera on a stick with
wheels" robot, drive it in **Gazebo Harmonic**, prove the abstraction by
swapping in **Isaac Sim**, and end with a trivial autonomous behavior that
doesn't know which simulator it's running against.

Target stack: **ROS 2 Jazzy + Gazebo Harmonic** (officially paired, least
pain), optional Isaac Sim 4.x later.

---

## Ground rules for yourself

Read these once. Refer back when you get stuck.

1. **Consumers never import simulator code.** No `gz_*`, no `isaacsim_*` in any
   node that runs the robot. Only standard ROS 2 messages.
2. **The contract is a written doc, not a vibe.** Topic names, message types,
   frame ids, and QoS go in `CONTRACT.md`. If you want to change them, change
   the doc first, then the code.
3. **`use_sim_time` is always on in sim.** Mixing wall clock and sim clock is
   the #1 source of "mysterious" bugs.
4. **One xacro, many providers.** The robot description is shared. Only the
   `<hardware>` plugin tag changes between Gazebo / Isaac / real.
5. **When something breaks on swap, it's a leak in the abstraction**, not a
   sim bug. Fix the leak.

---

## Phase 0 — Environment

**Goal:** a working ROS 2 Jazzy + Gazebo Harmonic dev container with a colcon
workspace.

### 0.1 Switch the Dockerfile to Jazzy

In `Dockerfile`, change `ARG ROS_DISTRO=humble` → `ARG ROS_DISTRO=jazzy`. The
base image `osrf/ros:jazzy-desktop-full` already bundles Gazebo Harmonic and
`ros_gz`. Rebuild:

```bash
docker compose build
docker compose run --rm ros   # or whatever your service is called
```

### 0.2 Sanity check

Inside the container:

```bash
ros2 doctor            # nothing critical red
gz sim --versions      # should report Harmonic (8.x)
ros2 pkg list | grep ros_gz
```

### 0.3 Workspace skeleton

```bash
cd /workspace
mkdir -p src
cd src
ros2 pkg create --build-type ament_cmake stick_bot_description
ros2 pkg create --build-type ament_cmake stick_bot_bringup
ros2 pkg create --build-type ament_python stick_bot_consumers
```

Build and source:

```bash
cd /workspace
colcon build --symlink-install
source install/setup.zsh
```

**Resources**
- ROS 2 Jazzy docs: https://docs.ros.org/en/jazzy/
- Gazebo Harmonic + ROS 2 install matrix: https://gazebosim.org/docs/harmonic/ros_installation
- `ros_gz` repo: https://github.com/gazebosim/ros_gz

---

## Phase 1 — The Robot Description

**Goal:** a xacro file describing the robot, with a swappable `<hardware>`
block via a xacro arg.

### 1.1 What to model

Keep it boring:

- `base_link` — box, 0.3 × 0.2 × 0.1 m.
- `left_wheel`, `right_wheel` — cylinders, continuous joints off `base_link`.
- `caster_link` — sphere, fixed joint, no controller (stops the robot falling
  over).
- `stick_link` — a vertical cylinder off `base_link`, fixed joint.
- `camera_link` — small box on top of the stick, fixed joint.
- `camera_optical_link` — child of `camera_link`, rotated per REP-103
  (x-forward → z-forward optical convention). Images will be published in this
  frame.

### 1.2 ros2_control block

In the xacro, add:

```xml
<ros2_control name="StickBotSystem" type="system">
  <hardware>
    <xacro:if value="${sim_mode == 'gazebo'}">
      <plugin>gz_ros2_control/GazeboSimSystem</plugin>
    </xacro:if>
    <xacro:if value="${sim_mode == 'isaac'}">
      <plugin>isaac_ros2_control/IsaacSystem</plugin>
    </xacro:if>
    <xacro:if value="${sim_mode == 'real'}">
      <plugin>stick_bot_hw/StickBotHardware</plugin>
    </xacro:if>
  </hardware>
  <joint name="left_wheel_joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
  <joint name="right_wheel_joint"> ... same ... </joint>
</ros2_control>
```

The xacro arg `sim_mode` is the one knob that switches providers.

### 1.3 Gazebo sensor + ros2_control plugins

Still inside the xacro, add the Gazebo-specific bits (they're a no-op when
loaded anywhere else because `gz_ros2_control` reads them):

```xml
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlSystem">
    <parameters>$(find stick_bot_bringup)/config/controllers.yaml</parameters>
  </plugin>
</gazebo>

<gazebo reference="camera_link">
  <sensor name="rgb_camera" type="camera">
    <topic>camera/image_raw</topic>
    <gz_frame_id>camera_optical_link</gz_frame_id>
    <camera> ... intrinsics ... </camera>
    <always_on>1</always_on>
    <update_rate>30</update_rate>
  </sensor>
</gazebo>
```

### 1.4 Try it

```bash
xacro src/stick_bot_description/urdf/stick_bot.urdf.xacro sim_mode:=gazebo > /tmp/bot.urdf
check_urdf /tmp/bot.urdf
ros2 launch urdf_tutorial display.launch.py model:=/tmp/bot.urdf  # optional, visual check in RViz
```

**Resources**
- URDF tutorial: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html
- xacro cheatsheet: http://wiki.ros.org/xacro
- `ros2_control` URDF guide: https://control.ros.org/jazzy/doc/ros2_control/doc/index.html
- REP-103 (coordinate frames): https://ros.org/reps/rep-0103.html
- REP-105 (frames for mobile robots): https://ros.org/reps/rep-0105.html

---

## Phase 2 — Write the Contract

**Goal:** a one-page `CONTRACT.md` at repo root. Do this *before* writing any
consumer code.

Include:

| Purpose | Topic | Type | Frame | QoS |
| --- | --- | --- | --- | --- |
| Velocity command in | `/cmd_vel` | `geometry_msgs/Twist` | `base_link` | reliable, depth 10 |
| Joint states out | `/joint_states` | `sensor_msgs/JointState` | — | reliable, depth 10 |
| Odometry | `/odom` | `nav_msgs/Odometry` | `odom` → `base_link` | reliable, depth 10 |
| TF tree | `/tf`, `/tf_static` | standard | — | standard |
| RGB image | `/camera/image_raw` | `sensor_msgs/Image` | `camera_optical_link` | **sensor_data** (best-effort) |
| Camera info | `/camera/camera_info` | `sensor_msgs/CameraInfo` | `camera_optical_link` | reliable, transient local |
| Reset (sim only) | `/sim/reset` | `std_srvs/Empty` | — | — |

Also state: **`use_sim_time` = true in every node when a sim is the provider.**

This file is the only thing consumers are allowed to depend on.

---

## Phase 3 — Drive the Robot in Gazebo

**Goal:** teleop a spawned robot in Gazebo, see camera images in RViz.

### 3.1 Controller config

`stick_bot_bringup/config/controllers.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names:  ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    wheel_separation: 0.22
    wheel_radius: 0.05
    base_frame_id: base_link
    odom_frame_id: odom
    publish_rate: 50.0
    use_stamped_vel: false   # so /cmd_vel stays a plain Twist
```

### 3.2 Launch file

`stick_bot_bringup/launch/gazebo.launch.py` should:

1. Process the xacro with `sim_mode:=gazebo`, publish `/robot_description`.
2. Start `robot_state_publisher` with `use_sim_time:=true`.
3. Start Gazebo Harmonic with an empty world: `gz sim -r empty.sdf`.
4. Spawn the robot into Gazebo via `ros_gz_sim create -topic /robot_description`.
5. Bridge Gazebo ↔ ROS topics with `ros_gz_bridge parameter_bridge`. At
   minimum: `/clock`, camera image, camera info.
6. `ros2 run controller_manager spawner joint_state_broadcaster`.
7. `ros2 run controller_manager spawner diff_drive_controller`.

### 3.3 Smoke test

```bash
ros2 launch stick_bot_bringup gazebo.launch.py
# in another shell:
ros2 run teleop_twist_keyboard teleop_twist_keyboard
rviz2   # add RobotModel, TF, Image (/camera/image_raw), Odometry
```

Drive around. The wheels should turn, `/odom` should integrate, the camera
image should update.

**Common gotchas**
- Camera topic empty → image QoS mismatch. RViz's default for Image is
  best-effort *on*, but check with `ros2 topic info -v`.
- `/cmd_vel` ignored → `use_stamped_vel: true` mismatch, or you forgot the
  spawner for `diff_drive_controller`.
- TF warning "odom → base_link" missing → `diff_drive_controller` didn't load.
- Robot falls through the floor → caster collision geometry missing or
  friction zero in the SDF/URDF.

**Resources**
- `gz_ros2_control`: https://github.com/ros-controls/gz_ros2_control
- `ros_gz` bridge types: https://github.com/gazebosim/ros_gz/blob/main/ros_gz_bridge/README.md
- `diff_drive_controller` docs: https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html
- Gazebo sensors reference: https://gazebosim.org/docs/harmonic/sensors

---

## Phase 4 — The First Consumer

**Goal:** a node that depends only on the contract. Swap-readiness test.

Write `stick_bot_consumers/blob_follower.py`: subscribe to
`/camera/image_raw`, find the centroid of red pixels with OpenCV, publish
`/cmd_vel` to turn toward it and drive forward. ~60 lines.

Add a red cube to the Gazebo world. Launch, watch the robot chase it.

**Acceptance criterion for this phase:** grep your consumer package for
`gz`, `gazebo`, `ignition`, `isaac`. Zero hits. If any, move them out.

---

## Phase 5 — Swap in Isaac Sim

**Goal:** identical consumer, different provider. This is the payoff phase
and also where the abstraction gets stress-tested.

### 5.1 Prerequisites

- NVIDIA RTX GPU, recent driver.
- Isaac Sim 4.x installed (native or container — the container is ~30 GB).
- Isaac Sim's ROS 2 bridge extension enabled, pointed at ROS 2 Jazzy.

### 5.2 Import the robot

1. In Isaac Sim, use the **URDF Importer** on your xacro-rendered URDF
   (`xacro ... sim_mode:=isaac > /tmp/bot.urdf`).
2. Save the resulting stage as `stick_bot.usd`.
3. Verify joint drives exist on both wheels and are in velocity mode.

### 5.3 Publishing on the contract topics

Isaac Sim publishes via **Action Graphs** (OmniGraph). Build a graph that:

- Reads wheel joint states → publishes `sensor_msgs/JointState` on `/joint_states`.
- Reads `/cmd_vel` → differential drive node → writes wheel velocity commands.
- Publishes the RTX camera to `/camera/image_raw` and `/camera/camera_info`
  with the same frame id (`camera_optical_link`) as Gazebo.
- Publishes `/clock` and the TF tree (or let `robot_state_publisher` handle TF
  from `/joint_states`, which is cleaner).

### 5.4 Launch file

`stick_bot_bringup/launch/isaac.launch.py`: launches Isaac Sim with the USD
stage, starts `robot_state_publisher` with `use_sim_time:=true`. That's it —
no `controller_manager` for now (the Action Graph plays that role). Later you
can switch to the Isaac `ros2_control` hardware interface for true parity.

### 5.5 Run the same consumer

```bash
ros2 launch stick_bot_bringup isaac.launch.py
ros2 run stick_bot_consumers blob_follower
```

Everything the consumer sees should be identical. What breaks teaches you
where your contract leaks.

**Expected leaks (fix them, don't work around them)**
- Camera optical frame orientation differs → fix the USD camera prim
  orientation, not the consumer.
- Image encoding `rgb8` vs `bgr8` → pick one in the contract.
- QoS mismatch (Isaac bridge defaults differ) → set explicitly.
- `/clock` not published → enable in the Action Graph.

**Resources**
- Isaac Sim ROS 2 docs: https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/index.html
- URDF importer: https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/import_urdf.html
- OmniGraph ROS 2 nodes reference: https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_camera.html

---

## Phase 6 — Containerization

**Goal:** one `docker compose up <provider>` swaps the sim without touching
consumers.

Structure:

```
docker/
  base.Dockerfile            # ROS 2 Jazzy + workspace build
  gazebo.Dockerfile          # FROM base, adds ros_gz, Harmonic is already there
  isaac.Dockerfile           # FROM nvcr.io/nvidia/isaac-sim:4.x, adds ROS 2 bridge
  consumers.Dockerfile       # FROM base, just the consumer packages
docker-compose.gazebo.yml
docker-compose.isaac.yml
```

All containers share `ROS_DOMAIN_ID` and a Docker network so DDS discovery
works. Consumer container is identical in both compose files — that's the
whole point.

Gotchas: Isaac needs `--gpus all` + NVIDIA container toolkit; host networking
is the easiest way to get DDS discovery working across containers until you
know you need something fancier.

---

## Phase 7 — Optional: Stretch Goals

Pick any that interest you. Each teaches something specific.

- **IMU sensor.** Adds sensor QoS discipline and TF timing bugs to debug.
- **Depth camera.** Exposes the sim-fidelity gap between Gazebo and Isaac.
- **Nav2 stack.** Your robot becomes navigable with zero changes to the sim
  side — the ultimate contract test.
- **Real hardware.** ESP32 + micro-ROS driving two hobby motors, same
  `/cmd_vel`, same `/joint_states`. Now you've closed the loop.
- **RL policy in Isaac Lab.** Train in Isaac, deploy the trained policy
  against Gazebo or real, unchanged.

---

## How to use this tutorial

- Treat each Phase as a session. Don't skip Phase 2 (the contract) — it's the
  cheapest phase and prevents the most pain.
- When something breaks, ask: *is this a contract violation, a URDF bug, or a
  sim bug?* Almost always it's one of the first two.
- Keep a `LEARNINGS.md` as you go. Every non-obvious fix is worth one line.

## Meta-resources

- The Construct (ROS 2 Jazzy courses): https://app.theconstruct.ai/
- Articulated Robotics (YouTube) — the best intro to URDF + ros2_control +
  Gazebo for a diff-drive robot, episode by episode.
- `ros2_control` demos repo: https://github.com/ros-controls/ros2_control_demos
- Nav2 tutorials (once you get to Phase 7): https://docs.nav2.org/
- Isaac Lab (for the RL stretch goal): https://isaac-sim.github.io/IsaacLab/
