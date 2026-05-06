---
title: Architecture
nav_order: 2
---

# Architecture

Two locally-built image layers, no published artefact.

```
osrf/ros:${ROS_DISTRO}-desktop-full        upstream, pulled once
  └── project-core   (core.Dockerfile)     apt deps + entrypoint
        └── your consumer  (Dockerfile)    your AI/CV deps, FROM project-core
```

The core image contains apt dependencies and a sourcing entrypoint. The core workspace source is **not baked into the image** — it lives on the host under `core_ws/` and is bind-mounted at runtime. This means you can inspect and rebuild artifacts outside the container without a full image rebuild.

## Runtime layout

| Path | Origin | Mounted? |
|---|---|---|
| `/opt/ros/${ROS_DISTRO}` | upstream image | no |
| `/core_ws` | host `./core_ws/`, bind-mount in compose | yes (core) |
| `/workspace` | host `./workspace/`, bind-mount in compose | yes (consumer) |

The entrypoint sources `/opt/ros/${ROS_DISTRO}/setup.bash` and, if present, `/core_ws/install/setup.bash` on every container start — so no manual `source` call is needed.

## Containers

`docker-compose.yml` runs `core` plus opt-in consumers via compose profiles.
Both share the host network so DDS discovery just works.

## Per-machine setup

1. Clone this repo and source the shell shortcuts (see [Quickstart](quickstart)).
2. Clone core source into `core_ws/src/`.
3. `ros-build` — builds the core image.
4. `ros-upd` — starts the container.
5. First time: `ros-zsh` → `colcon build` inside the container → `ros-restart`.
