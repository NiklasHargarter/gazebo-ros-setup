---
title: Core stack
nav_order: 6
---

# Core stack

The core image contains apt dependencies and a sourcing entrypoint. The workspace source lives on the host under `core_ws/src/` and is bind-mounted into `/core_ws` at runtime — build artifacts stay on the host and are visible outside the container.

## Clone core source

```bash
git clone --branch 0.0.3 https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git -C core_ws/src/hugo_moveit_config checkout 3eb7c8d5c756bfa08947a4466f68e6737e1d368d
```

`core_ws/src/*` is gitignored. `robotis_hand` must be pinned to `0.0.3` — newer versions have a broken dependency chain.

## Build the core image

```bash
ros-build
```

This installs apt dependencies and sets up the entrypoint. It does **not** run `colcon build` — that happens inside the running container (see below).

## Build the workspace (first time)

```bash
ros-upd          # start the container
ros-zsh          # open a shell
cd /core_ws && colcon build
exit
ros-restart      # restart so the entrypoint picks up install/
```

After this, `core_ws/build/` and `core_ws/install/` exist on the host. Every subsequent `ros-upd` sources the workspace automatically.

## Rebuild triggers

| What changed | Action |
|---|---|
| apt deps in `core.Dockerfile` | `ros-build` |
| Core source under `core_ws/src/` | `ros-zsh` → `colcon build` |
| ROS distro | Update `.env`, then `ros-build` + rebuild workspace |
