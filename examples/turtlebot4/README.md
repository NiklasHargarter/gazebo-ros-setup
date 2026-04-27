# TurtleBot 4 — core stand-in (Jazzy)

This example plays the role of the **core image** in the project's
[architecture](../../docs/architecture.md), using the TurtleBot 4
simulator stack as a stand-in for the real (private) core repo. It
exists so the consumer workflow can be exercised end-to-end without
GitLab access.

When the real core repo is wired in, you'll build `core.Dockerfile`
at the repo root instead of this one. The image tag (`project-core:jazzy`)
and everything downstream stays identical.

**Jazzy only.** TB4's simulator stack on Humble uses Ignition Fortress
and different package names; this example doesn't cover it.

---

## 1. Build the core stand-in image

From the repo root, with `.env`'s `ROS_DISTRO=jazzy`:

```bash
docker build -f examples/turtlebot4/Dockerfile \
             -t project-core:jazzy \
             --build-arg ROS_DISTRO=jazzy \
             .
```

Installs `turtlebot4-desktop`, `turtlebot4-simulator`,
`turtlebot4-navigation`, `slam-toolbox`, `nav2-bringup` on top of the
public base image. Tagged `project-core:jazzy` so consumer images can
`FROM project-core:jazzy`.

---

## 2. Pick a runtime image

You can either run the core image directly (no consumer) or build a
consumer image on top of it:

- **Core only** — for poking at TB4 by itself:
  ```bash
  echo "CONSUMER_IMAGE=project-core:jazzy" >> .env
  ```
- **With the example consumer** — see [`../consumer-camera/`](../consumer-camera/).

---

## 3. Launch the simulation

```bash
docker compose up -d
docker compose exec ros-gazebo zsh

# inside the container:
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
```

Gazebo opens with a TurtleBot 4 on the `depot` world. Create 3 bringup,
RPLIDAR, camera, and EKF nodes spin up automatically.

{: .note }
If that launch file isn't found, check which launch your installed
version ships:
`ros2 pkg prefix turtlebot4_gz_bringup && ls $(ros2 pkg prefix turtlebot4_gz_bringup)/share/turtlebot4_gz_bringup/launch`.
The package was renamed from `turtlebot4_ignition_bringup` when TB4
moved to gz-sim.

---

## 4. Verify topics

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

---

## 5. Drive it manually

```bash
docker compose exec ros-gazebo zsh
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`i` / `,` / `j` / `l` to drive.

---

## 6. Optional: Nav2 + SLAM

```bash
ros2 launch turtlebot4_navigation slam.launch.py
ros2 launch turtlebot4_navigation nav2.launch.py
ros2 launch turtlebot4_viz view_robot.launch.py
```

---

## Shut down

```bash
docker compose down
```
