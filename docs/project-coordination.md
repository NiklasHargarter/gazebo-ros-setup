---
title: Project Coordination
layout: default
nav_order: 5
---

# Project Coordination

This is the living project state document. It tracks what has been decided, what is still unknown, and who owns what. Update it as answers arrive from team meetings.

For the technical architecture behind these decisions, see [Integration Architecture & Team Workflow](ros2-gazebo-integration).

---

## Decisions

| Decision | Detail |
|---|---|
| **Repo purpose** | Reproducible base environment + shared world. Teams bring their own code in separate repos. |
| **World ownership** | Shared Gazebo world lives in this repo, maintained by the TZ6. |
| **Integration responsibility** | TZ6 is responsible for the shared world, the bridge config, the integrated launch file, and cross-team compatibility. |
| **Interface approach** | A shared ROS 2 interfaces package will be the contract between teams — code, not a document. See the architecture doc for details. |
| **Team structure** | TZ2 owns the physical layer. TZ6 owns the simulation layer (this repo). TZ3, TZ4, and TZ5 each independently contribute to the intelligence layer. |
| **Team isolation** | Any party can work against the shared world independently without needing other parties' code. |

---

## Open Questions

Unresolved as of TZ6 joining the project (2026-03-25). Raise in team meetings.

### Interface contract
- [ ] Who creates the first version of the shared interfaces package, and when?
- [ ] What is the change process for the interface? If the robot team renames a joint, what is the notification and migration process?

### Team state
- [ ] Has anyone (TZ2, TZ3, TZ4, TZ5) already written nodes with topic names that would need to be reconciled?
- [ ] What sensors does the robot have? Each sensor becomes a bridge topic and must be in the interface contract.

### Workspace & code sharing
- [ ] How do teams share their ROS packages for others to use? Options: Git submodules, separate repos cloned into `workspace/`, shared network mount.
- [ ] Where do team launch files live if teams have separate repos? TZ6 needs a stable path to call them from the integrated launch.

### Hardware & GPU
- [ ] Does every researcher have an NVIDIA GPU? The current Docker setup requires the NVIDIA Container Toolkit. Anyone on a Mac or CPU-only machine cannot run the current setup.
- [ ] Is there a shared server for headless testing?

### Breaking changes
- [ ] What happens when a change to the robot URDF or the interfaces package breaks other teams? A minimal process — even just "open an issue first" — prevents silent breakage.

---

## System Components — Ownership & Status

Everything the full system needs to run. Update as the project takes shape.

| Component | Description | Owner | Status |
|---|---|---|---|
| **Base Docker environment** | Shared container with ROS 2 and Gazebo | TZ6 | done |
| **Shared world (SDF)** | The Gazebo environment all teams run against | TZ6 | in progress |
| **Bridge configuration** | Maps simulation topics to ROS 2 — the world's public interface | TZ6 | missing |
| **Integrated launch file** | Assembles all team components into one running system | TZ6 | missing |
| **ROS 2 bag (reference session)** | Recorded interface topics for offline development | TZ6 | missing |
| **Shared interfaces package** | All cross-team message, service, and action types | ? | missing |
| **Robot description (URDF/Xacro)** | Full robot model with geometry, physics, and joint definitions | TZ2 | ? |
| **Controller configuration** | Defines how joints are controlled at runtime | TZ2 | ? |
| **TZ2 launch file** | Launches the robot description and controllers | TZ2 | ? |
| **TZ3 nodes** | Visual reasoning and social navigation | TZ3 | ? |
| **TZ3 launch file** | Launches TZ3 nodes | TZ3 | ? |
| **TZ4 nodes** | Human-aware AI | TZ4 | ? |
| **TZ4 launch file** | Launches TZ4 nodes | TZ4 | ? |
| **TZ5 nodes** | AI for decision making | TZ5 | ? |
| **TZ5 launch file** | Launches TZ5 nodes | TZ5 | ? |

`?` = unknown, to be established in team meetings.

---

## Meeting Agenda

Priority order for the first full team meeting:

1. **Interface contract** — who creates the first version of the interfaces package, and when. Block all cross-team subscriber/publisher development until this exists.
2. **Current state per team** — has TZ2, TZ3, TZ4, or TZ5 already written nodes? What topic names did they use?
3. **Sensor inventory** — what sensors does the robot have? This determines the bridge config and the interface contract.
5. **GPU availability** — a quick show of hands avoids a surprise on day one.
6. **Launch file convention** — where do team launch files live if code is in separate repos?
7. **Breaking change process** — agree on a minimal rule before anyone starts depending on another team's interface.
