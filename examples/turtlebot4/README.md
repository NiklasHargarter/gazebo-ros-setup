# TurtleBot 4 — Jazzy

Runs the full TurtleBot 4 simulator (iRobot Create 3 base + RPLIDAR + OAK-D camera) in Gazebo Harmonic with all the ROS 2 nodes that ship for the real robot.

**Jazzy only.** TB4's simulator stack on Humble uses Ignition Fortress and different package names; this example doesn't cover it.

---

## 1. Build the extended image

From the repo root (make sure `.env` has `ROS_DISTRO=jazzy`):

```bash
docker compose -f docker-compose.yml -f examples/turtlebot4/docker-compose.yml up -d --build
```

Add `-f docker-compose.nvidia.yml` before `up` if you have an NVIDIA GPU.

The build installs `turtlebot4-desktop`, `turtlebot4-simulator`, `turtlebot4-navigation`, plus `slam-toolbox` and `nav2-bringup` on top of the base image. First build takes several minutes; afterwards it's cached.

---

## 2. Launch the simulation

Open a shell:

```bash
docker compose exec ros-gazebo zsh
```

Start Gazebo + all TB4 nodes:

```bash
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
```

You should see Gazebo open with a TurtleBot 4 on the `depot` world. The Create 3 bringup, RPLIDAR, camera, and EKF nodes all spin up automatically.

{: .note }
If that launch file isn't found, check which launch your installed version ships: `ros2 pkg prefix turtlebot4_gz_bringup && ls $(ros2 pkg prefix turtlebot4_gz_bringup)/share/turtlebot4_gz_bringup/launch`. The package was renamed from `turtlebot4_ignition_bringup` when TB4 moved to gz-sim.

---

## 3. Verify topics

In a second shell:

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
/tf_static
/joint_states
/battery_state
```

Stream the lidar:

```bash
ros2 topic echo /scan --once
```

---

## 4. Drive it around

Teleop from a third shell:

```bash
docker compose exec ros-gazebo zsh
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`i` / `,` / `j` / `l` to drive.

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
