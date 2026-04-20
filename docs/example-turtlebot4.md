---
title: "Example: TurtleBot 4 (Jazzy)"
layout: default
nav_order: 6
---

# Example: TurtleBot 4 (Jazzy)

Runs the full TurtleBot 4 simulator (iRobot Create 3 base + RPLIDAR + OAK-D camera) in Gazebo Harmonic with all the ROS 2 nodes that ship for the real robot.

Source: [`examples/turtlebot4/`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/turtlebot4){:target="_blank"}. **Jazzy only** — TB4's simulator stack on Humble uses Ignition Fortress and different package names; this example doesn't cover it.

---

## 1. Build the extended image

From the repo root (with `ROS_DISTRO=jazzy` in `.env`):

```bash
docker compose -f docker-compose.yml -f examples/turtlebot4/docker-compose.yml up -d --build
```

Add `-f docker-compose.nvidia.yml` before `up` if you have an NVIDIA GPU — the TB4 sim is heavy, you want it.

The build installs `turtlebot4-desktop`, `turtlebot4-simulator`, `turtlebot4-navigation`, plus `slam-toolbox` and `nav2-bringup` on top of the base image. First build takes several minutes; afterwards it's cached.

---

## 2. Launch the simulator

```bash
docker compose exec ros-gazebo zsh
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
```

Gazebo opens with a TurtleBot 4 on the `depot` world. The Create 3 bringup, RPLIDAR, camera, and EKF nodes all spin up automatically.

{: .note }
If that launch file isn't found, check which launch your installed version ships:
`ros2 pkg prefix turtlebot4_gz_bringup && ls $(ros2 pkg prefix turtlebot4_gz_bringup)/share/turtlebot4_gz_bringup/launch`.
The package was renamed from `turtlebot4_ignition_bringup` when TB4 moved to gz-sim.

---

## 3. Verify topics

Second shell:

```bash
docker compose exec ros-gazebo zsh
ros2 topic list
```

Expected (abridged):

```
/cmd_vel
/odom
/scan
/oakd/rgb/preview/image_raw
/tf
/battery_state
```

```bash
ros2 topic echo /scan --once
ros2 topic hz /odom
```

---

## 4. Drive it from the CLI

On Jazzy, TurtleBot 4's `/cmd_vel` is **`geometry_msgs/msg/TwistStamped`**, not the plain `Twist` you may be used to. Check first:

```bash
ros2 topic info /cmd_vel
```

Drive forward continuously (Ctrl-C to stop — Create 3 safety-stops within ~0.5s after the publish stream ends):

```bash
ros2 topic pub -r 20 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{header: {frame_id: "base_link"}, twist: {linear: {x: 0.2}, angular: {z: 0.0}}}'
```

Spin in place:

```bash
ros2 topic pub -r 20 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {angular: {z: 0.5}}}'
```

One-shot (robot moves briefly, then safety-stops):

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.2}}}'
```

{: .note }
**Zsh quoting gotcha:** keep the whole command on one line. Zsh mangles backslash-newlines mid-YAML, which splits the message into multiple shell words and produces an unhelpful `unrecognized arguments` error. Single-quote the YAML so `{`, `}`, and `:` aren't interpreted by the shell.

### Why `teleop_twist_keyboard` doesn't move the robot

`teleop_twist_keyboard` publishes plain `geometry_msgs/msg/Twist`. TB4 on Jazzy subscribes to `TwistStamped`. The topic name matches, so `ros2 topic list` looks fine, but no message gets through. Either use `ros2 topic pub` as above, or run a twist-to-twist-stamped relay, or use `turtlebot4_teleop` if available.

---

## 5. Optional: Nav2 + SLAM

With the sim still running:

```bash
ros2 launch turtlebot4_navigation slam.launch.py
ros2 launch turtlebot4_navigation nav2.launch.py
ros2 launch turtlebot4_viz view_robot.launch.py
```

RViz opens with the live map and Nav2 goal tools.

---

## Shut down

```bash
docker compose -f docker-compose.yml -f examples/turtlebot4/docker-compose.yml down
```
