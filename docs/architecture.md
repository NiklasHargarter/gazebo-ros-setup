---
title: Architecture
nav_order: 3
---

# Architecture

## What this repo is

A **base station** for a multi-team robotics project: it runs the container,
Gazebo simulation, robot description, and integrated launch. That's the scope —
it gets the robot + sim up. Other teams bring their own code in their own repos
and connect over ROS topics, services, and actions on the host network. How
they run that code — container or native, however built — is their call.

## Teams

| Contributor | Focus | Repo |
|---|---|---|
| **Sim team** (this repo) | Base container, Gazebo world, integrated launch | `gazebo-ros-setup` |
| **Robotics team** | Robot itself: URDF/Xacro, controllers, hardware drivers, ROS↔Gazebo bridge | `hugo_moveit_config` |
| **CAU Kiel** | Visual perception, gesture/object recognition, social navigation | own repo |
| **Uni Lübeck** | Cognition: situation understanding, task prediction, explainable plans | own repo |
| **DFKI Lübeck** | LLM-based decision framework; integrates other AI outputs into robot actions | own repo |

The robotics team did the initial Gazebo integration as a side-effect of their
own testing; the sim is now this team's responsibility. Patches to
`hugo_moveit_config` go upstream as branches/PRs there, not as local diffs here.

## How teams talk

Cross-team communication is ROS topics, services, and actions — all stock
message types (`sensor_msgs`, `geometry_msgs`, `nav_msgs`, `vision_msgs`, …).
No shared interfaces package; we'll add one if something genuinely cross-cutting
shows up. See [Topics](topics) for what the sim exposes.

A few loose conventions, not rules — they just keep us from gluing mismatched
topic names together at integration time. Ignore one if it gets in your way and
tell the sim team.

- **Prefer stock message types.** Custom types live in your own
  `<team>_interfaces` package; teams that subscribe pull your repo.
- **Namespace topics by function** so two teams don't both publish `/objects`:
  `/perception/...` (CAU Kiel), `/cognition/...` (Uni Lübeck),
  `/decision/...` (DFKI Lübeck). Suggestions, not assignments.
- **Mind QoS.** Sensor streams best-effort, commands reliable, latched topics
  `transient_local`. Mismatch = topic visible but callback never fires.

## The core image

Locally built; the private source is never published:

```
osrf/ros:${ROS_DISTRO}-desktop-full        upstream, pulled once
  └── project-core   (core.Dockerfile)     apt deps + entrypoint
```

The core image holds apt deps and a sourcing entrypoint. The core workspace
source is **not baked into the image** — it lives on the host under `core_ws/`
and is bind-mounted at runtime, so build artifacts stay visible on the host.
The entrypoint sources `/opt/ros/${ROS_DISTRO}/setup.bash` and, if present,
`/core_ws/install/setup.bash` on every container start — no manual `source`.

GPU access is layered on via `docker-compose.nvidia.yml`, enabled by default
through `COMPOSE_FILE` in `.env`.

### Connecting your code

`docker-compose.yml` runs `core` on the **host network**. Your nodes reach it
the same way — over ROS on the host network. Run them in a container with:

- `network_mode: host` — DDS discovery works across processes/containers.
- `ipc: host` — FastDDS shared-memory transport (`/dev/shm`) carries payloads.
  Without it, discovery succeeds but no data flows.

…or run them natively on the host. Either works; the sim doesn't care. You can
build `FROM project-core` to inherit the ROS + apt deps, but nothing requires
it. [`examples/perception-demo`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/perception-demo)
shows one container-based setup as reference.

## Per-machine setup

See [Quickstart](quickstart).
