---
title: Core stack
nav_order: 6
---

# Core ROS / Gazebo stack

The container mounts two workspaces on top of the `project-core` image:

1. `/core_ws` — the shared core stack (this repo's `core_ws/`)
2. `/workspace` — the consumer's own packages (this repo's `workspace/`)

Both overlay `/opt/ros/${ROS_DISTRO}` and are auto-sourced in new shells.

For the bigger picture (base / core / consumer image layers), see
[Architecture](architecture.md).

## Clone the core source

The core stack consists of three repos. From the repo root on the host:

```bash
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
cd core_ws/src/turtlebot3_manipulation && git checkout humble && cd -
```

`core_ws/src/` is gitignored, so these clones won't pollute this repo.

## Build the core image

Core's apt/rosdep deps are baked into a local image via `core.Dockerfile`
(no published image — partners build it themselves):

```bash
docker build -f core.Dockerfile \
             -t project-core:${ROS_DISTRO:-humble} \
             --build-arg ROS_DISTRO=${ROS_DISTRO:-humble} .
```

Rerun this only when core deps change.

## Build the core workspace

Inside the container:

```bash
cd /core_ws
rosdep update
rosdep install --from-paths src --ignore-src -y
colcon build --merge-install
```

Open a new shell (or `source /core_ws/install/setup.zsh`) to pick it up.
