---
title: "Example: Camera World"
layout: default
nav_order: 5
---

# Example: Camera World

A minimal custom setup — one SDF world with a ground plane, a red box, and a static camera sensor. The camera's Gazebo image topic is bridged into ROS 2, and a small Python node subscribes and logs frame size + FPS.

Use it as a template when you want to **write your own world and your own node from scratch** without pulling in a whole robot stack.

Source: [`examples/camera_world/`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/camera_world){:target="_blank"}. Jazzy only (the bridge type strings differ on Humble — see the bottom of this page).

---

## Layout

```
examples/camera_world/
├── worlds/camera_world.sdf           # world + camera sensor
├── launch/camera_demo.launch.py      # gz sim + bridge + subscriber
└── src/camera_subscriber/            # ROS 2 python package
    └── camera_subscriber/image_consumer.py
```

Runs on the base `gazebo-ros-setup` image — no extra apt packages needed.

---

## 1. Drop the package into the workspace

The container mounts `./workspace` → `/workspace`. The `examples/` folder is **not** mounted by default, so copy what you need in:

```bash
cp -r examples/camera_world/src/camera_subscriber workspace/src/
cp -r examples/camera_world/launch examples/camera_world/worlds workspace/
```

---

## 2. Build

```bash
docker compose up -d
docker compose exec ros-gazebo zsh
# inside:
cd /workspace && colcon build --symlink-install
```

New shells auto-source `install/setup.zsh`; for the current shell run it manually.

---

## 3. Launch

```bash
ros2 launch /workspace/launch/camera_demo.launch.py
```

A Gazebo window opens with a red box on a grey plane, and the subscriber logs frame info to the terminal.

---

## Running the pieces manually

```bash
# shell 1 — simulator
gz sim -r /workspace/worlds/camera_world.sdf

# shell 2 — bridge
ros2 run ros_gz_bridge parameter_bridge \
    /camera/image@sensor_msgs/msg/Image@gz.msgs.Image

# shell 3 — verify
ros2 topic list
ros2 topic hz /camera/image
ros2 run rqt_image_view rqt_image_view /camera/image
```

The bridge argument format is `<topic>@<ROS type>@<gz type>`.

---

## How the pieces connect

```
  ┌─────────────┐   gz topic          ┌──────────────┐   ROS 2 topic
  │  gz sim     │  /camera/image  →   │ parameter_   │  /camera/image  →  image_consumer
  │  (SDF world │  gz.msgs.Image      │ bridge       │  sensor_msgs/Image
  │  + sensor)  │                     └──────────────┘
  └─────────────┘
```

---

## Humble note

On Humble, the bridge gz type is `ignition.msgs.Image` (not `gz.msgs.Image`), the simulator is Fortress, and the SDF plugin names (`ignition-gazebo-*`) differ. This example is only tested on Jazzy + gz-harmonic.
