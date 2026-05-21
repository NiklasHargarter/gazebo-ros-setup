---
title: Architecture
nav_order: 3
---

# Architecture

## What this repo is

A **base station** for a multi-team robotics project: container, Gazebo simulation, robot description, and one working consumer as reference. Other teams bring their own code in their own repos and connect over ROS topics, services, and actions.

## Teams

| Contributor | Focus | Repo |
|---|---|---|
| **Sim team** (this repo) | Base container, Gazebo world, integrated launch, contract surface | `gazebo-ros-setup` |
| **Robotics team** | Robot itself: URDF/Xacro, controllers, hardware drivers, ROS↔Gazebo bridge | `hugo_moveit_config` |
| **CAU Kiel** | Visual perception, gesture/object recognition, social navigation | own repo |
| **Uni Lübeck** | Cognition: situation understanding, task prediction, explainable plans | own repo |
| **DFKI Lübeck** | LLM-based decision framework; integrates other AI outputs into robot actions | own repo |

The robotics team did the initial Gazebo integration as a side-effect of their own testing; the sim is now this team's responsibility. Patches to `hugo_moveit_config` go upstream as branches/PRs there, not as local diffs in this repo.

## The interface contract

Cross-team communication is ROS topics, services, and actions. The current contract is in [Writing Your Own Nodes](writing-your-own-nodes#what-ros-core-publishes) — name, type, QoS, purpose. If a topic isn't in that table, it isn't part of the contract yet.

All cross-team types today are stock ROS messages (`sensor_msgs`, `geometry_msgs`, `nav_msgs`, `tf2_msgs`, `moveit_msgs`, `vision_msgs`). There is **no shared interfaces package** — nothing yet needs one. We'll create one if and when something genuinely cross-cutting appears.

## Conventions

Recommendations, not rules. They exist so we don't have to glue mismatched topic names together at integration time. If a convention gets in the way of a team's work, ignore it and tell the sim team — guidelines that nobody follows are worse than no guidelines.

**Prefer stock ROS message types.** `sensor_msgs/Image`, `vision_msgs/Detection3DArray`, `geometry_msgs/PoseStamped`, `nav_msgs/Odometry`, etc. cover almost every cross-team payload. Reach for a custom type only when nothing fits.

**Custom types live in your own repo.** Put them in a `<team>_interfaces` package alongside your nodes. Other teams that subscribe pull your repo. Don't try to push types into this base repo unless multiple teams produce compatible payloads — then we promote into a small shared package.

**Namespace topics by function.** Avoids accidental collisions:

| Prefix | Producer | Examples |
|---|---|---|
| `/camera/...`, `/scan`, `/imu`, `/tf`, `/joint_states`, `/odom` | Sim | Sensor streams (established) |
| `/cmd_vel`, `/move_action`, `/<part>_controller/...` | Consumer → robot | Robot commands (established) |
| `/perception/...` | CAU Kiel (suggested) | Detections, gestures, faces |
| `/cognition/...` | Uni Lübeck (suggested) | Situation labels, task predictions |
| `/decision/...` | DFKI Lübeck (suggested) | High-level commands, action choices |

The AI-team prefixes are suggestions, not assignments — pick what fits your nodes. They exist so two teams don't both publish on `/objects`.

**QoS defaults.**
- Sensor streams: `qos_profile_sensor_data` (best-effort, depth 5).
- Commands: reliable, depth 10.
- Latched-by-design (`/tf_static`, `/map`, anything published once): `transient_local`.

QoS mismatch is the #1 reason a topic shows up in `ros2 topic list` but your callback never fires.

**Document your topics.** When a new topic goes live, append one row to the contract table in [Writing Your Own Nodes](writing-your-own-nodes#what-ros-core-publishes): name, type, QoS, purpose. That table *is* the central registry.

## How each team plugs in

Every consumer follows the same pattern:

1. Team repo sits alongside `gazebo-ros-setup` on the host.
2. Their Dockerfile is `FROM project-core:${ROS_DISTRO}` — inherits ROS + apt deps.
3. Compose declares `network_mode: host` and `ipc: host` — DDS discovery and FastDDS shared-memory transport work across containers.
4. Nodes subscribe/publish against the contract.

`consumer-template/` is a working starting point. Two patterns for dev without the live sim:

## Runtime architecture

Two locally-built image layers; nothing private is ever published:

```
osrf/ros:${ROS_DISTRO}-desktop-full        upstream, pulled once
  └── project-core   (core.Dockerfile)     apt deps + entrypoint
        └── your consumer  (your Dockerfile, FROM project-core)
```

The core image holds apt deps and a sourcing entrypoint. The core workspace source is **not baked into the image** — it lives on the host under `core_ws/` and is bind-mounted at runtime. Build artifacts stay visible on the host.

| Path | Origin | Mounted into |
|---|---|---|
| `/opt/ros/${ROS_DISTRO}` | upstream image | core, consumers |
| `/core_ws` | host `./core_ws/` | core |
| `/workspace` | host `./workspace/` | consumers |

The entrypoint sources `/opt/ros/${ROS_DISTRO}/setup.bash` and, if present, `/core_ws/install/setup.bash` on every container start. No manual `source` call needed.

### Containers and networking

`docker-compose.yml` runs `core` plus opt-in consumers via compose profiles. All containers use:

- `network_mode: host` — DDS discovery works across containers without extra config.
- `ipc: host` — FastDDS's shared-memory transport (`/dev/shm`) actually carries payloads between containers. Without it, discovery succeeds but no data flows.

GPU access is layered on via `docker-compose.nvidia.yml` (or `ros-profile nvidia` with the shortcuts).

## Per-machine setup

See [Quickstart](quickstart).
