# Example consumer — camera-driven brightness driver

A minimal consumer that demonstrates the full architecture end-to-end:

- `Dockerfile` builds an image `FROM project-core:jazzy` (the TB4 stand-in)
- `src/consumer_camera/` is a ROS 2 Python package that subscribes to
  the TB4 camera and publishes `/cmd_vel`

The driver does the cheapest possible "AI": mean pixel brightness. If the
scene is bright, it drives forward; if dark, it spins. Real consumers
would swap this for a VLA model, perception pipeline, etc.

---

## Prerequisites

The TB4 core stand-in image must already be built:

```bash
docker build -f examples/turtlebot4/Dockerfile \
             -t project-core:jazzy \
             --build-arg ROS_DISTRO=jazzy \
             .
```

See [`../turtlebot4/`](../turtlebot4/).

---

## 1. Build the consumer image

From the repo root:

```bash
docker build -f examples/consumer-camera/Dockerfile \
             -t consumer-camera:jazzy \
             --build-arg ROS_DISTRO=jazzy \
             .
```

---

## 2. Drop the package into the workspace

The container expects ROS 2 packages under `/workspace/src/`. Copy (or
symlink) the consumer package in:

```bash
cp -r examples/consumer-camera/src/consumer_camera workspace/src/
```

---

## 3. Run

Set `.env`:

```
ROS_DISTRO=jazzy
CONSUMER_IMAGE=consumer-camera:jazzy
```

Up:

```bash
docker compose up -d
docker compose exec ros-gazebo zsh
```

Inside the container, build the workspace:

```bash
cd /workspace
colcon build --symlink-install
source install/setup.zsh
```

Start the TB4 sim in one shell:

```bash
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
```

In a second shell (`docker compose exec ros-gazebo zsh`):

```bash
ros2 run consumer_camera brightness_driver
```

You should see log lines like:

```
[brightness_driver]: mean= 84.31  ->  lin=0.00 ang=0.50
[brightness_driver]: mean=132.10  ->  lin=0.20 ang=0.00
```

…and the TB4 in Gazebo will spin or drive forward depending on what its
camera sees.

---

## What this demonstrates

- **Source is mounted, not baked.** Editing `brightness_driver.py` on the
  host and re-running `colcon build` inside the container is the
  development loop. No image rebuild.
- **Image rebuild only for deps.** Adding torch/opencv/etc. to the
  consumer's `Dockerfile` is what triggers a rebuild.
- **Consumer doesn't know how core is built.** It only relies on
  `project-core:jazzy` existing and exposing the TB4 camera topic. When
  the real (private) core replaces the TB4 stand-in, this consumer keeps
  working as long as the topic contract holds.
