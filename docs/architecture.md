---
title: Architecture
nav_order: 2
---

# Architecture

Two locally-built image layers, no published artefact.

```
osrf/ros:${ROS_DISTRO}-desktop-full        upstream, pulled once
  └── project-core   (core.Dockerfile)     core apt deps + core source baked in
        └── your consumer  (Dockerfile)    your AI/CV deps, FROM project-core
```

Core source is `COPY`'d and `colcon build`'d at image-build time into
`/opt/ros_overlay`. Rebuild the core image when core source or deps change.

## Runtime layout

| Path | Origin | Mounted? |
|---|---|---|
| `/opt/ros/${ROS_DISTRO}` | upstream image | no |
| `/opt/ros_overlay` | baked into `project-core` (colcon merge-install) | no |
| `/workspace` | host `./workspace/`, bind-mount in compose | yes (consumer only) |

Both `setup.bash` / `setup.zsh` overlays auto-source from `~/.bashrc` / `~/.zshrc`.

## Containers

`docker-compose.yml` runs `core` plus opt-in consumers via compose profiles.
Both share the host network so DDS discovery just works.

## Per-machine setup

1. Clone this repo.
2. Clone core source into `core_ws/src/` (see [Core Stack](core-stack)).
3. `docker build -f core.Dockerfile -t project-core:humble --build-arg ROS_DISTRO=humble .`
4. Build consumer image (`consumer-template/`).
5. `docker compose up -d`.
