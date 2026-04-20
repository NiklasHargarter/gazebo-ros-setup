---
title: Getting Started
layout: home
nav_order: 1
---

# Getting Started with ROS 2 & Gazebo

A reproducible, container-based ROS 2 + Gazebo environment. You don't install ROS or Gazebo on your host — everything runs inside Docker.

**Supported:** ROS 2 Humble + Gazebo Fortress · ROS 2 Jazzy + Gazebo Harmonic.
Pick your distro with `ROS_DISTRO=humble` or `ROS_DISTRO=jazzy` in `.env`. Jazzy is the recommended default unless a project explicitly requires Humble.

---

## Pick your path

| Goal | Start here |
|---|---|
| Run ROS 2 + Gazebo on my Linux machine for the first time | [Quickstart](quickstart) |
| I'm on macOS | [macOS Setup](macos-setup) |
| Write and run my own ROS 2 nodes in the container | [Writing Your Own Nodes](writing-your-own-nodes) |
| Split the GUI from the simulation across two machines | [Remote GUI Client](server-client) |
| Run Gazebo on a headless server (no display) | [Headless Rendering](headless-rendering) |
| See what's actually inside the `desktop-full` base image | [Desktop Full Contents](desktop-full-contents) |
| Minimal custom world + a Python node consuming a camera | [Example: Camera World](example-camera-world) |
| Off-the-shelf robot — full TurtleBot 4 sim on Jazzy | [Example: TurtleBot 4](example-turtlebot4) |

---

## How the repo is organised

The `docker-compose.yml` is the minimal base. Optional features are **overlay files** you layer on top — no commented-out blocks, no hidden flags:

```bash
# Base (CPU/Intel, local-only)
docker compose up

# With an NVIDIA GPU
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up

# Server-client networking (see server-client guide)
docker compose -f docker-compose.yml -f docker-compose.server.yml up

# NVIDIA + server-client combined
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml -f docker-compose.server.yml up
```

Each overlay is small enough to read in one sitting. Stack any combination.

---

## Distro cheat sheet

| Distro | Gazebo | Launch | Topic CLI |
|---|---|---|---|
| Humble | Fortress | `ign gazebo` | `ign topic` |
| Jazzy | Harmonic | `gz sim` | `gz topic` |

Commands in the guides that differ between distros are labeled **Humble** / **Jazzy**.
