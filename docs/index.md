---
title: Getting Started
layout: home
nav_order: 1
---

# Getting Started with ROS 2 & Gazebo

This repo runs the robot and Gazebo sim (ROS 2 Humble + Fortress) in Docker —
no ROS on your host. That's its whole job. Your code talks to it over ROS on
the host network, however you want to run that code.

---

## How it works

The core image is built locally on every machine (the private source is never
published):

```
osrf/ros:humble-desktop-full         ← upstream, pulled once and cached
  └── project-core  (core.Dockerfile)
        ← core apt deps + entrypoint that auto-sources the workspace
```

The core workspace source lives on the host under `core_ws/` and is
bind-mounted at runtime — build artifacts stay visible outside the container.

```bash
ros-upd            # start the robot + sim
```

The NVIDIA overlay is enabled by default via `COMPOSE_FILE` in `.env`; drop
`docker-compose.nvidia.yml` from that line if you have no GPU.

## Talking to it

Anything that speaks ROS on the **host network** can drive the robot. Run your
nodes in a container with host networking (and `ipc: host` for shared-memory
transport) from anywhere on your machine, or run them natively — your choice.
How your code gets built or containerised is up to you. The
[`examples/`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples)
are reference, not a required pattern.

---

## Pick your path

| Goal | Start here |
|---|---|
| Get the robot + sim running on a new machine | [Quickstart](quickstart) |
| Understand the setup and how teams connect | [Architecture](architecture) |
| See what the running sim exposes | [Topics](topics) |
| A reference consumer | [`examples/perception-demo`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/perception-demo) |
