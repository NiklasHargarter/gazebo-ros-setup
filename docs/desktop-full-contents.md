---
title: Desktop Full Image Contents
layout: default
nav_order: 4
---

# ROS 2 Jazzy `desktop-full` — Package Contents

This document details what is included in the `osrf/ros:jazzy-desktop-full` Docker image, broken down by metapackage layer.

## Layer hierarchy

```
ros-jazzy-desktop-full
├── ros-jazzy-desktop
│   └── ros-jazzy-ros-base
│       └── ros-jazzy-ros-core
├── ros-jazzy-perception
├── ros-jazzy-simulation
└── ros-jazzy-ros-gz-sim-demos
```

---

## `ros-core`

**Dockerfile:** `osrf/docker_images` → `ros/jazzy/ubuntu/noble/ros-core/Dockerfile`
**Package definition:** `ros2/variants` → `ros_core/package.xml`

Base image: `ubuntu:noble`. Installs `ros-jazzy-ros-core` via apt.

- **Build system:** `ament_cmake`, `ament_cmake_auto`, `ament_cmake_ros`, `ament_cmake_gtest`, `ament_cmake_gmock`, `ament_cmake_pytest`, `ament_index_cpp`, `ament_index_python`, `ament_lint_auto`, `ament_lint_common`
- **Client libraries:** `rclcpp`, `rclcpp_action`, `rclcpp_lifecycle`, `rclpy`, `rcl_lifecycle`
- **Interface generation:** `rosidl_default_generators`, `rosidl_default_runtime`, `common_interfaces`
- **Launch system:** `launch`, `launch_ros`, `launch_testing`, `launch_testing_ament_cmake`, `launch_testing_ros`, `launch_xml`, `launch_yaml`, `ros2launch`
- **CLI:** `ros2cli_common_extensions`
- **Plugins:** `class_loader`, `pluginlib`
- **Security:** `sros2`, `sros2_cmake`
- **Environment:** `ros_environment`

---

## `ros-base`

**Dockerfile:** `osrf/docker_images` → `ros/jazzy/ubuntu/noble/ros-base/Dockerfile`
**Package definition:** `ros2/variants` → `ros_base/package.xml`

Base image: `ros:jazzy-ros-core-noble`. Adds developer tooling via apt (not in `package.xml`) then installs `ros-jazzy-ros-base`.

**Extra tooling installed by the Dockerfile (not in package.xml):**
- `build-essential`, `git`
- `python3-colcon-common-extensions`, `python3-colcon-mixin`
- `python3-rosdep`, `python3-vcstool`
- `rosdep` initialized, colcon mixin/metadata configured

**Package.xml exec_depends (adds on top of `ros-core`):**
- `rosbag2` — bag recording and playback
- `geometry2` — tf2, tf2_ros, tf2_geometry_msgs, tf2_sensor_msgs
- `kdl_parser` — URDF to KDL kinematic tree parser
- `urdf` — URDF parser
- `robot_state_publisher` — publishes TF from URDF + joint states

---

## `desktop`

**Dockerfile:** `osrf/docker_images` → `ros/jazzy/ubuntu/noble/desktop/Dockerfile`
**Package definition:** `ros2/variants` → `desktop/package.xml`

Adds on top of `ros-base`:

- **Visualization:** `rviz2`, `rviz_default_plugins`, `rviz_common`
- **GUI tools:** `rqt`, `rqt_common_plugins` (graph, topic monitor, console, image viewer, etc.)
- **Simulation toy:** `turtlesim`
- **Teleoperation:** `teleop_twist_keyboard`, `teleop_twist_joy`, `joy`
- **Utilities:** `angles`, `depthimage_to_laserscan`, `pcl_conversions`, `tlsf`, `tlsf_cpp`
- **Demo and example nodes:**
  - `demo_nodes_cpp`, `demo_nodes_py`
  - `action_tutorials_cpp`, `action_tutorials_py`, `action_tutorials_interfaces`
  - `composition`, `lifecycle`
  - `examples_rclcpp_*`, `examples_rclpy_*`

---

## `perception`

**Package definition:** `ros2/variants` → `perception/package.xml`

Adds on top of `ros-base`:

- **Image stack:** `image_common`, `image_pipeline`, `image_transport_plugins`
- **Laser processing:** `laser_filters`, `laser_geometry`
- **Point cloud:** `perception_pcl`
- **Computer vision:** `vision_opencv` (cv_bridge + image_geometry, wrapping OpenCV)

---

## `simulation`

**Package definition:** `ros2/variants` → `simulation/package.xml`

Adds on top of `ros-base`:

- **`ros_gz_bridge`** — bidirectional ROS 2 ↔ Gazebo topic/service bridge
- **`ros_gz_sim`** — launch integration for Gazebo from ROS 2
- **`ros_gz_image`** — image transport between ROS 2 and Gazebo
- **`ros_gz_interfaces`** — shared custom message/service types
- All of the above vendor **Gazebo Harmonic** (`gz-sim` 8.x) via `gz_sim_vendor`

---

## `ros_gz_sim_demos`

Added directly by `desktop_full/package.xml` (not via a named variant layer).

- Example launch files and worlds demonstrating `ros_gz_sim` integration

---

## What is NOT included

These are commonly needed but must be installed separately:

| Package | Install |
|---|---|
| Navigation stack | `ros-jazzy-navigation2` |
| MoveIt2 | `ros-jazzy-moveit` |
| SLAM Toolbox | `ros-jazzy-slam-toolbox` |
| Hardware drivers (cameras, lidars) | vendor-specific packages |

---

## Where this information is recorded

| Source | URL | What it contains |
|---|---|---|
| OSRF Docker image definitions | `github.com/osrf/docker_images` → `ros/jazzy/ubuntu/noble/*/Dockerfile` | Exact apt packages installed per layer |
| ROS 2 variant metapackage definitions | `github.com/ros2/variants` → `jazzy` branch, `*/package.xml` | Declared exec dependencies per variant |
| Gazebo vendor package | `github.com/gazebo-release/gz_sim_vendor` → `jazzy` branch | Confirms Gazebo Harmonic (gz-sim 8.x) is the vendored version |
| Docker Hub image tags | `hub.docker.com/r/osrf/ros` | Compressed image sizes per tag |
| REP-2001 | `ros.org/reps/rep-2001.html` | Normative definition of what each variant must include |
