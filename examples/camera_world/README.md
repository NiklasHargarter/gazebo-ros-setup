# Camera World

A minimal custom setup: one SDF world with a ground plane, a red box, and a static camera sensor. The camera's Gazebo image topic is bridged into ROS 2, and a small Python node subscribes and logs frame size + FPS.

Useful as a template when you want to **write your own world and your own node from scratch** without pulling in a whole robot stack.

Everything here works on the base `gazebo-ros-setup` image — no extra apt packages needed. Jazzy is assumed; the bridge type strings differ on Humble (see note at the end).

---

## Layout

```
examples/camera_world/
├── worlds/camera_world.sdf           # world + camera sensor
├── launch/camera_demo.launch.py      # starts gz sim + bridge + subscriber
└── src/camera_subscriber/            # ROS 2 python package
    └── camera_subscriber/image_consumer.py
```

---

## 1. Drop the package into your workspace

The container expects ROS 2 packages under `/workspace/src/`. Copy (or symlink) the subscriber package in:

From the host, in the repo root:

```bash
cp -r examples/camera_world/src/camera_subscriber workspace/src/
```

The world SDF and launch file don't need to live in `workspace/src/` — they're read by path. But if you prefer, copy them in too.

---

## 2. Build

Open a shell in the container:

```bash
docker compose exec ros-gazebo zsh
```

Build:

```bash
cd /workspace
colcon build --symlink-install
source install/setup.zsh   # new shells do this automatically
```

---

## 3. Launch everything

From the container (the repo is mounted at `/workspace` if you also mount the examples folder, otherwise point at the host path):

```bash
ros2 launch /workspace/../examples/camera_world/launch/camera_demo.launch.py
```

{: .note }
The `examples/` folder isn't mounted into the container by the default `docker-compose.yml` (only `./workspace` is). The easiest fix is to copy the launch file and world into `workspace/` too:
```bash
cp -r examples/camera_world/launch examples/camera_world/worlds workspace/
```
then launch with `ros2 launch /workspace/launch/camera_demo.launch.py`. Or add an `examples` bind-mount to `docker-compose.yml`.

What happens:

1. `gz sim` opens with the world — you should see a red box on a grey plane.
2. `ros_gz_bridge` bridges `/camera/image` (gz side) → `/camera/image` (ROS 2 side, `sensor_msgs/msg/Image`).
3. `image_consumer` subscribes and logs frame size once, then FPS every 2 seconds:

```
[image_consumer]: Subscribed to /camera/image
[image_consumer]: First frame: 640x480 encoding=rgb8 step=1920 bytes=921600
[image_consumer]: 58 frames in 2.00s (29.0 fps)
```

---

## 4. Run the pieces manually (for debugging)

Sometimes the single launch file hides what's going on. Each piece in its own shell:

```bash
# Shell 1 — simulator
gz sim -r /path/to/examples/camera_world/worlds/camera_world.sdf

# Shell 2 — bridge
ros2 run ros_gz_bridge parameter_bridge \
    /camera/image@sensor_msgs/msg/Image@gz.msgs.Image

# Shell 3 — verify topic and subscriber
ros2 topic list                # /camera/image should appear
ros2 topic hz /camera/image    # should show ~30 Hz
ros2 run camera_subscriber image_consumer
```

You can also view the image directly:

```bash
ros2 run rqt_image_view rqt_image_view /camera/image
```

---

## How the pieces connect

```
  ┌─────────────┐   gz topic          ┌──────────────┐   ROS 2 topic
  │  gz sim     │  /camera/image  →   │ parameter_   │  /camera/image  →  image_consumer
  │  (SDF world │  gz.msgs.Image      │ bridge       │  sensor_msgs/Image  (your node)
  │  + sensor)  │                     │ (ros_gz_     │
  └─────────────┘                     │  bridge)     │
                                      └──────────────┘
```

The bridge string `/camera/image@sensor_msgs/msg/Image@gz.msgs.Image` is `<topic>@<ROS type>@<gz type>`. Change the ROS side to whatever topic you want the node to subscribe to.

---

## Extending it

Things worth trying from this base:
- Add a second model with a different color — watch the frame change in real time.
- Swap the static camera for a camera mounted on a movable base and publish `cmd_vel`.
- Add a depth camera: `<sensor type="depth_camera">` and bridge `@sensor_msgs/msg/Image@gz.msgs.Image` on the depth topic.
- Replace the logging with OpenCV processing via `cv_bridge` (apt: `ros-jazzy-cv-bridge`).

---

## Humble note

On Humble the bridge type is `ignition.msgs.Image` (not `gz.msgs.Image`) and the simulator is Fortress — the SDF plugin names (`ignition-gazebo-*`) and `<render_engine>` interactions differ. This example is written for Jazzy + gz-harmonic and is not tested on Humble.
