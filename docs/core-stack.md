---
title: Core stack
nav_order: 6
---

# Core stack

Core ROS packages are baked into `project-core` at image-build time. No
runtime bind-mount of core source.

## Clone core source

```bash
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
```

`core_ws/src/*` is gitignored.

## Build the core image

```bash
docker build -f core.Dockerfile \
             -t project-core:${ROS_DISTRO:-humble} \
             --build-arg ROS_DISTRO=${ROS_DISTRO:-humble} .
```

Build steps inside the image:

1. Install apt deps from `core.Dockerfile`.
2. `COPY core_ws/src → /tmp/core_build/src`.
3. `rosdep install` for any package.xml found.
4. `colcon build --merge-install --install-base /opt/ros_overlay`.

Result: `/opt/ros_overlay/setup.bash` (auto-sourced in shells).

## Rebuild triggers

Rebuild the core image when:

- core apt deps change (`core.Dockerfile`)
- core source under `core_ws/src/` changes
- ROS distro changes

Editing core source on the host has **no runtime effect** without a rebuild.
