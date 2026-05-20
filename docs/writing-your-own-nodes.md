---
title: Writing Your Own Nodes
layout: default
nav_order: 4
---

# Writing your own nodes

`consumer-template/` is a working consumer with two example nodes
(`echo_camera`, `drive_square`) under
`workspace/src/consumer_template/`. Use it as your starting point.

```bash
ros-upd --profile template
ros-exec consumer-template "cd /workspace && colcon build --symlink-install"
ros-exec consumer-template ros2 run consumer_template echo_camera
ros-exec consumer-template "ros2 run consumer_template drive_square --ros-args -p start:=true"
```

## What `ros-core` publishes

Captured from a live `mobile_manipulation_gazebo.launch.py` session.

### Topics consumers subscribe to

| Topic | Type | QoS | Purpose |
| --- | --- | --- | --- |
| `/camera/rgb/image_raw` | `sensor_msgs/msg/Image` | `qos_profile_sensor_data` | RGB camera frame |
| `/camera/rgb/camera_info` | `sensor_msgs/msg/CameraInfo` | `qos_profile_sensor_data` | Camera intrinsics |
| `/scan` | `sensor_msgs/msg/LaserScan` | `qos_profile_sensor_data` | 2D lidar |
| `/scan/points` | `sensor_msgs/msg/PointCloud2` | `qos_profile_sensor_data` | 2D lidar as PointCloud2 |
| `/imu` | `sensor_msgs/msg/Imu` | `qos_profile_sensor_data` | IMU |
| `/joint_states` | `sensor_msgs/msg/JointState` | reliable, depth 10 | All joints, simulated |
| `/odom` | `nav_msgs/msg/Odometry` | reliable, depth 10 | Diff-drive odometry |
| `/tf` | `tf2_msgs/msg/TFMessage` | reliable, depth 100 | Dynamic transforms |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | reliable, **transient_local** | Static transforms — set durability or you'll miss them |
| `/map` | `nav_msgs/msg/OccupancyGrid` | reliable, **transient_local** | Nav2 static map |

### Topics consumers publish

| Topic | Type | QoS | Purpose |
| --- | --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | reliable, depth 10 | Base velocity command |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | reliable, depth 10 | Quick Nav2 goal (RViz-style) |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | reliable, depth 10 | Reset localization |

### Action servers

| Action | Type | Purpose |
| --- | --- | --- |
| `/move_action` | `moveit_msgs/action/MoveGroup` | Plan + execute via MoveIt (preferred for arm motion) |
| `/R_arm_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` | Direct right-arm trajectory (bypasses MoveIt) |
| `/L_arm_controller/follow_joint_trajectory` | same | Direct left-arm trajectory |
| `/Head_controller/follow_joint_trajectory` | same | Head pan/tilt |
| `/right_hand_controller/follow_joint_trajectory` | same | Right hand fingers |
| `/left_hand_controller/follow_joint_trajectory` | same | Left hand fingers |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Single Nav2 goal |
| `/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | Multi-waypoint Nav2 |

### Useful services

| Service | Type | Purpose |
| --- | --- | --- |
| `/compute_ik` | `moveit_msgs/srv/GetPositionIK` | Inverse kinematics |
| `/compute_fk` | `moveit_msgs/srv/GetPositionFK` | Forward kinematics |
| `/plan_kinematic_path` | `moveit_msgs/srv/GetMotionPlan` | Plan only, no execute |
| `/apply_planning_scene` | `moveit_msgs/srv/ApplyPlanningScene` | Add/remove collision objects |

Controllers are named the way MoveIt expects:
`R_arm_controller`, `L_arm_controller`, `Head_controller`,
`left_hand_controller`, `right_hand_controller`, plus
`diff_drive_controller` and `imu_broadcaster`.

## QoS conventions

- **Sensors** (camera, lidar, IMU): `qos_profile_sensor_data` —
  best-effort, depth 5. Required to match the publisher.
- **Control** (cmd_vel, goals): reliable, depth 10.
- **Latched-by-design** (`/tf_static`, `/map`): set
  `durability=TRANSIENT_LOCAL` on the subscription or you join too late
  and never get the value.

**QoS mismatch is the #1 reason a topic shows up in `ros2 topic list`
but your callback never fires.** If `ros2 topic echo` works but your
node sees nothing, check QoS first.

## Pattern: subscribe to a camera frame

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class FrameLogger(Node):
    def __init__(self):
        super().__init__('frame_logger')
        self.create_subscription(
            Image, '/camera/rgb/image_raw',
            lambda m: self.get_logger().info(f'{m.width}x{m.height} {m.encoding}'),
            qos_profile_sensor_data,
        )


def main():
    rclpy.init()
    rclpy.spin(FrameLogger())
```

Full version with frame-rate throttling:
[`workspace/src/consumer_template/consumer_template/echo_camera.py`](../workspace/src/consumer_template/consumer_template/echo_camera.py).

## Pattern: send a velocity command

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist


class Crawler(Node):
    def __init__(self):
        super().__init__('crawler')
        self.pub = self.create_publisher(
            Twist, '/cmd_vel',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE),
        )
        self.create_timer(0.1, self._tick)

    def _tick(self):
        msg = Twist()
        msg.linear.x = 0.1   # m/s
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(Crawler())
```

Open-loop square (state machine, default-off):
[`workspace/src/consumer_template/consumer_template/drive_square.py`](../workspace/src/consumer_template/consumer_template/drive_square.py).

## Pattern: send an arm goal via MoveIt

Prefer `/move_action` over the raw `*_controller/follow_joint_trajectory`
servers — MoveIt handles collision checking and IK for you.

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints, JointConstraint, MotionPlanRequest, PlanningOptions,
)


class ArmGoal(Node):
    def __init__(self):
        super().__init__('arm_goal')
        self.client = ActionClient(self, MoveGroup, '/move_action')

    def send(self):
        self.client.wait_for_server()

        joint_targets = {
            'R_joint_1': 0.0, 'R_joint_2': -0.5, 'R_joint_3': 0.0,
            'R_joint_4': -1.0, 'R_joint_5': 0.0, 'R_joint_6': 0.5,
            'R_joint_7': 0.0,
        }
        constraint = Constraints(joint_constraints=[
            JointConstraint(joint_name=n, position=p,
                            tolerance_above=0.01, tolerance_below=0.01,
                            weight=1.0)
            for n, p in joint_targets.items()
        ])

        req = MotionPlanRequest()
        req.group_name = 'arm_right'
        req.num_planning_attempts = 5
        req.allowed_planning_time = 5.0
        req.goal_constraints = [constraint]

        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options = PlanningOptions(plan_only=False)

        return self.client.send_goal_async(goal)


def main():
    rclpy.init()
    node = ArmGoal()
    future = node.send()
    rclpy.spin_until_future_complete(node, future)
    rclpy.shutdown()
```

Inspect available group names with
`ros2 topic echo /robot_description_semantic --once | grep group` (or
read `core_ws/src/hugo_moveit_config/config/*.srdf`).

## Source layout

Consumer packages live under `./workspace/src/`, bind-mounted into
`/workspace` inside the consumer container. Edits on the host are
visible immediately — no image rebuild.

```
host: ./workspace/        ↔   consumer: /workspace/
        src/                          src/
        install/          ←   colcon build writes here
        build/
        log/
```

Source layering inside the consumer container (auto-sourced in shells):

```
/opt/ros/${ROS_DISTRO}     base ROS
/core_ws/install           core workspace (sourced if built)
/workspace/install         your packages (sourced if built)
```

## Create a new package

Always scaffold with `ros2 pkg create` — never hand-write `package.xml` / `setup.py`.

```bash
ros-upd --profile template
ros-exec consumer-template
cd /workspace/src
ros2 pkg create --build-type ament_python my_package \
  --dependencies rclpy sensor_msgs \
  --node-name my_node
```

C++: `--build-type ament_cmake`. Add extra nodes by editing the
generated `setup.py` `entry_points` and dropping new files alongside
the generated one.

## Build

```bash
cd /workspace
colcon build --symlink-install
```

`--symlink-install` symlinks Python sources, so edits take effect
without rebuild. New entry points or `setup.py` changes still need a
rebuild.

Open a new shell to pick up the overlay, or `source install/setup.zsh`.

## Run

```bash
ros2 run my_package my_node
```

## Verify from another shell

```bash
ros-zsh
ros2 topic echo /my_topic
```
