---
title: Topics
nav_order: 4
---

# Topics the sim exposes

A reminder of what a running `mobile_manipulation_gazebo.launch.py` puts on the
graph, so consumers know what to subscribe to and command. Not a frozen
contract — run `ros2 topic list` / `ros2 action list` against the live sim for
the current truth. Everything here is stock ROS message types; no shared
interfaces package.

## Subscribe to

| Topic | Type | Purpose |
| --- | --- | --- |
| `/camera/rgb/image_raw` | `sensor_msgs/Image` | RGB camera frame |
| `/camera/rgb/camera_info` | `sensor_msgs/CameraInfo` | Camera intrinsics |
| `/scan` | `sensor_msgs/LaserScan` | 2D lidar |
| `/scan/points` | `sensor_msgs/PointCloud2` | 2D lidar as PointCloud2 |
| `/imu` | `sensor_msgs/Imu` | IMU |
| `/joint_states` | `sensor_msgs/JointState` | All joints |
| `/odom` | `nav_msgs/Odometry` | Diff-drive odometry |
| `/tf`, `/tf_static` | `tf2_msgs/TFMessage` | Transforms (`/tf_static` is latched) |
| `/map` | `nav_msgs/OccupancyGrid` | Nav2 static map (latched) |

## Publish to

| Topic | Type | Purpose |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/Twist` | Base velocity command |
| `/goal_pose` | `geometry_msgs/PoseStamped` | Quick Nav2 goal |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | Reset localization |

## Actions

| Action | Type | Purpose |
| --- | --- | --- |
| `/move_action` | `moveit_msgs/MoveGroup` | Plan + execute via MoveIt (preferred for arm motion) |
| `/<part>_controller/follow_joint_trajectory` | `control_msgs/FollowJointTrajectory` | Direct trajectory per controller |
| `/navigate_to_pose` | `nav2_msgs/NavigateToPose` | Single Nav2 goal |
| `/navigate_through_poses` | `nav2_msgs/NavigateThroughPoses` | Multi-waypoint Nav2 |

Controllers are named the way MoveIt expects: `R_arm_controller`,
`L_arm_controller`, `Head_controller`, `left_hand_controller`,
`right_hand_controller`, plus `diff_drive_controller` and `imu_broadcaster`.
MoveIt services `/compute_ik`, `/compute_fk`, `/plan_kinematic_path`,
`/apply_planning_scene` are also up.

## QoS gotcha

Sensor streams are best-effort (`qos_profile_sensor_data`); commands are
reliable; latched topics (`/tf_static`, `/map`) are `transient_local`. A QoS
mismatch is the usual reason a topic appears in `ros2 topic list` but your
callback never fires.

See [`examples/perception-demo`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/perception-demo)
for a consumer that uses several of these.
