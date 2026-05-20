# Consumer template

Working example of a consumer service that runs against `project-core`.
Includes a Dockerfile, a compose profile, and a ROS 2 Python package
(`workspace/src/consumer_template/`) with two example nodes you can copy
when writing your own.

```
osrf/ros:${ROS_DISTRO}-desktop-full
  └── project-core      (this repo, core.Dockerfile)
        └── consumer-template  (this Dockerfile, FROM project-core)
```

## Run the examples

Sim must be up — start it from `ros-core` per the repo README.

```bash
# 1. Bring up the template container (builds the image on first run)
ros-upd --profile template

# 2. Build the workspace inside the container
ros-exec consumer-template "cd /workspace && colcon build --symlink-install"

# 3a. Stream camera frame dimensions
ros-exec consumer-template ros2 run consumer_template echo_camera

# 3b. Drive an open-loop square on /cmd_vel (default: idle)
ros-exec consumer-template "ros2 run consumer_template drive_square --ros-args -p start:=true"
```

See [`docs/writing-your-own-nodes.md`](../docs/writing-your-own-nodes.md)
for the full topic/action surface and copy-pasteable snippets.

## Copy this for a new consumer

1. Duplicate this directory into your consumer repo (or work in place).
2. Edit `Dockerfile` to add apt / pip deps. The opinionated zsh block is
   enabled by default — strip it for minimal/headless consumers and
   switch the compose `command:` to `/bin/bash`.
3. Add a service block in `docker-compose.yml` (copy `consumer-template`),
   point it at your image, give it a unique `profiles:` name.
4. Put your ROS 2 package(s) under `workspace/src/<your-pkg>/` — they're
   bind-mounted into the container at `/workspace`.
