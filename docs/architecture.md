---
title: Architecture
nav_order: 2
---

# Architecture

This repo provides the dev-container infrastructure for a ROS 2 + Gazebo
project where:

- The **core** stack (robot description, ROS nodes, Gazebo sim layer) lives
  in a private GitLab repo. Partners get guest read access; no container
  with that code is ever published.
- Multiple **consumers** (VLA models, perception, planning, ...) each live
  in their own repo and integrate with the core via ROS topics.

Because the core repo is private and not publishable as an image, every
machine builds its container stack locally.

## The four pieces

```
base image (this repo, Dockerfile)
  │   ROS + zsh + dev shell. Generic, published to GHCR.
  │
project-core (this repo, core.Dockerfile)
  │   FROM base. Adds core's apt/rosdep deps (MoveIt, nav2, ros2-control,
  │   gz-ros2-control, ...). Built locally on each machine. Not published.
  │
your consumer (consumer repo, Dockerfile)
  │   FROM project-core. Adds the consumer's AI/CV/Python deps. Built
  │   locally on each machine. Not published.
  │
docker compose (this repo)
      Orchestrates the runtime: bind-mounts core source + workspace,
      X11 socket, history, optional GPU/server overlays.
```

Each piece is loosely coupled: base knows nothing about core, core knows
nothing about consumers, consumers only pin `FROM project-core:${ROS_DISTRO}`.

## Source vs deps

- **Deps** are baked into images at build time (apt, pip, rosdep).
- **Source** is bind-mounted at runtime. Editing core or consumer code does
  not require an image rebuild — only `colcon build` inside the container.

This means an image only rebuilds when *dependencies* change, not when code
changes.

## Per-machine setup

A new partner machine needs:

1. This repo cloned.
2. The core repo cloned into `core_ws/src/core` (private GitLab; guest
   access required).
3. Their consumer repo cloned somewhere (their code lives in
   `workspace/src/<pkg>/`, see [Core stack](core-stack.md)).
4. Build the core image locally:
   ```bash
   docker build -f core.Dockerfile -t project-core:${ROS_DISTRO} \
                --build-arg ROS_DISTRO=${ROS_DISTRO} .
   ```
5. Build their consumer image (see `consumer-template/`).
6. Set `CONSUMER_IMAGE=...` in `.env`, run `docker compose up`.
