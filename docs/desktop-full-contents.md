---
title: Desktop Full Image Contents
layout: default
nav_order: 4
---

# ROS 2 Humble `desktop-full` — Package Contents

> **This is the version used by the robotics team** (ROS 2 Humble + Gazebo Fortress).

This document details what is included in the `osrf/ros:humble-desktop-full` Docker image, broken down by metapackage layer.

## Layer hierarchy

```
ros-humble-desktop-full
├── ros-humble-desktop
│   └── ros-humble-ros-base
│       └── ros-humble-ros-core
├── ros-humble-perception
├── ros-humble-simulation
└── ros-humble-ros-ign-gazebo-demos
```

---

## `ros-core`

**Dockerfile:** `osrf/docker_images` → `ros/humble/ubuntu/jammy/ros-core/Dockerfile`
**Package definition:** `ros2/variants` → `ros_core/package.xml`

Base image: `ubuntu:jammy`. Installs `ros-humble-ros-core` via apt.

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

**Dockerfile:** `osrf/docker_images` → `ros/humble/ubuntu/jammy/ros-base/Dockerfile`
**Package definition:** `ros2/variants` → `ros_base/package.xml`

Base image: `ros:humble-ros-core-jammy`. Adds developer tooling via apt (not in `package.xml`) then installs `ros-humble-ros-base`.

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

**Dockerfile:** `osrf/docker_images` → `ros/humble/ubuntu/jammy/desktop/Dockerfile`
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

- **`ros_ign_bridge`** — bidirectional ROS 2 ↔ Gazebo topic/service bridge
- **`ros_ign_gazebo`** — launch integration for Gazebo Fortress from ROS 2
- **`ros_ign_image`** — image transport between ROS 2 and Gazebo
- **`ros_ign_interfaces`** — shared custom message/service types
- All of the above vendor **Gazebo Fortress** (`ign-gazebo` 6.x)

---

## `ros_ign_gazebo_demos`

Added directly by `desktop_full/package.xml` (not via a named variant layer).

- Example launch files and worlds demonstrating `ros_ign_gazebo` integration

---

## What is NOT included

These are commonly needed but must be installed separately:

| Package | Install |
|---|---|
| Navigation stack | `ros-humble-navigation2` |
| MoveIt2 | `ros-humble-moveit` |
| SLAM Toolbox | `ros-humble-slam-toolbox` |
| Hardware drivers (cameras, lidars) | vendor-specific packages |

---

## Where this information is recorded

| Source | URL | What it contains |
|---|---|---|
| OSRF Docker image definitions | `github.com/osrf/docker_images` → `ros/humble/ubuntu/jammy/*/Dockerfile` | Exact apt packages installed per layer |
| ROS 2 variant metapackage definitions | `github.com/ros2/variants` → `humble` branch, `*/package.xml` | Declared exec dependencies per variant |
| Gazebo vendor package | `github.com/gazebosim/ros_gz` → `humble` branch | Confirms Gazebo Fortress (ign-gazebo 6.x) is the vendored version |
| Docker Hub image tags | `hub.docker.com/r/osrf/ros` | Compressed image sizes per tag |
| REP-2001 | `ros.org/reps/rep-2001.html` | Normative definition of what each variant must include |
