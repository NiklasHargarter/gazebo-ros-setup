---
title: Getting Started
layout: home
nav_order: 1
---

# Getting Started with ROS 2 & Gazebo

A reproducible, container-based ROS 2 + Gazebo dev environment for projects where the core stack lives in a private repo. You don't install ROS or Gazebo on your host — everything runs inside Docker.

**Current distro:** ROS 2 Humble + Gazebo Fortress (Ignition).

---

## How the repo is organised

Two Docker image layers, both built locally on every machine (nothing with private code is ever published):

```
osrf/ros:humble-desktop-full         ← upstream, pulled once and cached
  └── project-core  (core.Dockerfile)
        ← core apt deps + entrypoint that auto-sources the workspace
        └── your consumer  (your own Dockerfile, FROM project-core)
              ← your deps (AI/CV libraries, custom apt packages, ...)
```

The core workspace source lives on the host under `core_ws/` and is bind-mounted at runtime — build artifacts are visible outside the container. Consumers inherit the entrypoint from `project-core` and only need to add their own dependencies.

Core and consumers run as **separate containers** in one compose stack. They communicate over ROS topics/services/actions via host network (DDS discovery handles the rest):

```bash
docker compose up -d                        # core only
docker compose --profile camera up -d       # core + consumer-camera
```

Optional compose overlay files add GPU or server-client support without touching the base file:

```bash
docker compose up                                                          # CPU / Mesa
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up      # NVIDIA GPU
docker compose -f docker-compose.yml -f docker-compose.server.yml up      # remote GUI server
```

---

## Pick your path

| Goal | Start here |
|---|---|
| Set up this project on a new machine | [Quickstart](quickstart) |
| I'm on macOS | [macOS Setup](macos-setup) |
| Understand the core / consumer image layers | [Architecture](architecture) |
| Build or rebuild the core image | [Core Stack](core-stack) |
| Add consumer packages | [Writing Your Own Nodes](writing-your-own-nodes) |
| Split the GUI from the simulation across two machines | [Remote GUI Client](server-client) |
| Run Gazebo on a headless server (no display) | [Headless Rendering](headless-rendering) |
| See what's inside the `desktop-full` base image | [Desktop Full Contents](desktop-full-contents) |

---

## Quick reference

| Distro | Gazebo | Launch | Topic CLI |
|---|---|---|---|
| Humble | Fortress | `ign gazebo` | `ign topic` |
