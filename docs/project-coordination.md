---
title: Project Coordination & Open Questions
nav_order: 2
---

# Project Coordination & Open Questions

This document captures the current state of coordination decisions, known gaps, and questions to resolve in team meetings. It is a living document — update it as answers arrive.

---

## What is decided

| Decision | Detail |
|---|---|
| **Repo purpose** | Reproducible base environment + shared world. Teams bring their own code. |
| **World ownership** | Shared Gazebo world lives in this repo, maintained by the integration lead. |
| **Integration responsibility** | One person (integration lead) is responsible for ensuring all teams' work is compatible. |
| **Base philosophy** | Interface-first via ROS 2 topics/services/actions. No team depends directly on Gazebo internals. |
| **Team layers** | Three layers: Physical (robot/URDF), Environment (world/sensors), Intelligence (AI/control). |
| **Team code structure** | Each team maintains their own separate work. This repo provides the base they run against. |
| **Starting point** | Teams can run in isolation against the shared world without needing other teams' code. |

---

## Open questions — find out in meetings

These are unresolved as of project start. Each needs an answer before the relevant team begins building.

### Interface contract
- [ ] **Who defines the ROS 2 topic names, message types, and QoS settings?** The integration lead is the natural owner, but this must be agreed before teams write subscribers or publishers.
- [ ] **Does a shared `interfaces` ROS 2 package need to be created?** Or is a documented spec (YAML/Markdown) sufficient for now?
- [ ] **What is the change process for the interface?** If the robot team renames a joint (breaking change), what is the review/notification process?

### Team state & current work
- [ ] **What stage is each team at?** Has anyone already written nodes with topic names that would need to be reconciled?
- [ ] **What does the robot team's URDF currently look like?** Joint names and link names will define topic names.
- [ ] **What sensors are defined?** Camera, IMU, force-torque — each becomes a bridge topic.

### Workspace & code sharing
- [ ] **How do teams share their ROS packages for others to use?** Options: Git submodules in this repo, separate repos cloned into `workspace/`, a shared network mount, or a ROS package registry.
- [ ] **Should a `workspace/` directory convention be defined?** e.g., `workspace/robot/`, `workspace/tasks/`, `workspace/control/` so the launch file can find packages predictably.
- [ ] **When someone wants to run another team's code alongside theirs, what is the process?**

### Hardware & GPU
- [ ] **Does every researcher have an NVIDIA GPU?** The current Docker setup requires `nvidia.com/gpu=all` and the nvidia-container-toolkit. Anyone on a Mac or CPU-only machine cannot run the current setup.
- [ ] **Is there a shared server for headless/CI testing?** The architecture supports this (headless mode is documented) but no server is confirmed.
- [ ] **Is GPU required for the shared world, or only for AI inference?** Affects whether the base environment can run on non-NVIDIA machines.

### Breaking changes & versioning
- [ ] **What happens when the robot URDF changes in a way that breaks other teams?** Need a process: versioned tags, a PR review requirement, a migration guide, or something else.
- [ ] **Should the shared world be versioned separately from the Docker environment?** Or is a single `main` branch acceptable while the project is early-stage?

---

## Architecture intent (current understanding)

```
this repo
├── Dockerfile + docker-compose   ← base environment (all teams use this)
├── world/                        ← shared Gazebo world SDF (integration lead owns)
│   ├── world.sdf
│   └── launch/                   ← integrated launch file
└── docs/                         ← documentation and interface specs

team repos (separate, mounted into workspace/)
├── robot-team/                   ← URDF, Xacro, ros2_control config
├── tasks-team/                   ← task definitions, scenario scripts
└── control-team/                 ← AI/VLA nodes, control models
```

The bridge config inside `launch/` will be the **authoritative list of topics** that the world exposes. All teams must read this before writing their first subscriber or publisher.

---

## Meeting agenda items (derived from open questions)

Priority order for first team meeting:

1. **Interface contract** — agree on who owns it and when the first version will exist. Block all subscriber/publisher development until this is done.
2. **Current state of each team** — has anyone already written nodes? What topic names did they use?
3. **GPU availability** — a quick show of hands avoids a nasty surprise on day one.
4. **Workspace convention** — agree on the directory layout so the launch file can be written once.
5. **Breaking change process** — even a simple rule ("open an issue before renaming anything") prevents integration pain later.
