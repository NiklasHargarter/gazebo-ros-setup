---
title: Project Coordination
layout: default
nav_order: 3
---

# Project Coordination

This is the living project state document. It tracks what has been decided, what is still unknown, and who owns what. Update it as answers arrive from team meetings.

For the technical architecture behind these decisions, see [Integration Architecture & Team Workflow](ros2-gazebo-integration).

---

## Decisions

| Decision | Detail |
|---|---|
| **Repo purpose** | Reproducible base environment + shared world. Teams bring their own code in separate repos. |
| **World ownership** | Shared Gazebo world lives in this repo, maintained by the integration lead. |
| **Integration responsibility** | Integration lead is responsible for the shared world, the bridge config, the integrated launch file, and cross-team compatibility. |
| **Interface approach** | A shared ROS 2 interfaces package will be the contract between teams — code, not a document. See the architecture doc for details. |
| **Team structure** | Two fixed parties with clear ownership: TZ2 (physical layer) and simulation/integration lead (this repo). TZ3, TZ4, TZ5, and TZ6 each contribute to the intelligence layer independently. |
| **Team isolation** | Any party can work against the shared world independently without needing other parties' code. |

---

## Open Questions

Unresolved as of project start (2026-03-25). Raise in team meetings.

### Interface contract
- [ ] Who creates the first version of the shared interfaces package, and when?
- [ ] What is the change process for the interface? If the robot team renames a joint, what is the notification and migration process?

### Team state
- [ ] Who are all the parties involved on the intelligence side, and what is each working on?
- [ ] Has anyone already written nodes with topic names that would need to be reconciled?
- [ ] What sensors does the robot have? Each sensor becomes a bridge topic and must be in the interface contract.

### Workspace & code sharing
- [ ] How do teams share their ROS packages for others to use? Options: Git submodules, separate repos cloned into `workspace/`, shared network mount.
- [ ] Where do team launch files live if teams have separate repos? The integration lead needs a stable path to call them.

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
| **Base Docker environment** | Shared container with ROS 2 and Gazebo | Integration lead | done |
| **Shared world (SDF)** | The Gazebo environment all teams run against | Integration lead | in progress |
| **Bridge configuration** | Maps simulation topics to ROS 2 — the world's public interface | Integration lead | missing |
| **Shared interfaces package** | All cross-team message, service, and action types | ? | missing |
| **Integrated launch file** | Assembles all team components into one running system | Integration lead | missing |
| **ROS 2 bag (reference session)** | Recorded interface topics for offline development | Integration lead | missing |
| **Robot description (URDF/Xacro)** | Full robot model with geometry, physics, and joint definitions | TZ2 | ? |
| **Controller configuration** | Defines how joints are controlled at runtime | TZ2 | ? |
| **TZ2 launch file** | Launches the robot description and controllers | TZ2 | ? |
| **TZ3 nodes** | Visual reasoning and social navigation | TZ3 | ? |
| **TZ3 launch file** | Launches TZ3 nodes | TZ3 | ? |
| **TZ4 nodes** | Human-aware AI | TZ4 | ? |
| **TZ4 launch file** | Launches TZ4 nodes | TZ4 | ? |
| **TZ5 nodes** | AI for decision making | TZ5 | ? |
| **TZ5 launch file** | Launches TZ5 nodes | TZ5 | ? |
| **TZ6 nodes** | Robot training in virtual environments | TZ6 | ? |
| **TZ6 launch file** | Launches TZ6 nodes | TZ6 | ? |

`?` = unknown, to be established in team meetings.

---

## Meeting Agenda

Priority order for the first full team meeting:

1. **Interface contract** — who creates the first version of the interfaces package, and when. Block all cross-team subscriber/publisher development until this exists.
2. **Current state per team** — has TZ2, TZ3, TZ4, TZ5, or TZ6 already written nodes? What topic names did they use?
3. **Sensor inventory** — what sensors does the robot have? This determines the bridge config and the interface contract.
4. **TZ6 coordination** — robot training in virtual environments overlaps directly with the simulation layer. Align early on what world configurations and scenario scripting TZ6 needs.
5. **GPU availability** — a quick show of hands avoids a surprise on day one.
6. **Launch file convention** — where do team launch files live if code is in separate repos?
7. **Breaking change process** — agree on a minimal rule before anyone starts depending on another team's interface.
