---
title: Integration Architecture & Team Workflow
layout: default
nav_order: 3
---

# Integration Architecture & Team Workflow

---

## 1. The Interface-First Philosophy

The core principle is **decoupling**. No team should ever write code that depends directly on another team's implementation. Every interaction happens through agreed ROS 2 Topics, Services, and Actions.

This means:
- The AI team doesn't care how the robot is built — it reads topics.
- The robot team doesn't care how the AI works — it exposes topics.
- Gazebo is an implementation detail of the environment layer, not a dependency anyone else takes on.

The practical result: any layer can be swapped, upgraded, or tested in isolation without touching the others.

---

## 2. Team Layers & Responsibilities

The project is organized into three conceptual layers. Each layer is a clear boundary — a team only needs to know the ROS 2 interface at its boundary, not what is happening inside the other layers.

| Layer | Responsibility | Deliverables |
|---|---|---|
| **Physical Layer** (TZ2) | The robot's "body" | URDF/Xacro, mesh files, controller configurations |
| **Simulation Layer** (TZ6) | The shared world and its public interface | SDF world, sensor plugins, bridge configuration, integrated launch file |
| **Intelligence Layer** (TZ3, TZ4, TZ5) | Everything that reasons, plans, or acts | ROS 2 nodes for visual reasoning, human-aware AI, and decision making |

The Intelligence Layer has multiple independent parties. Each works against the same shared world and interface contract without needing to know about each other's implementation.

---

## 3. The Shared Interfaces Package

The interface contract must be **code, not a document**. A dedicated ROS 2 package — containing only `.msg`, `.srv`, and `.action` definitions — is the single source of truth that all teams depend on.

```
interfaces/
├── msg/      # shared message types
├── srv/      # shared service definitions
└── action/   # shared action definitions
```

Rules:
- No team invents their own message type for something that crosses a team boundary.
- A change to this package is a breaking change and requires coordination.
- This package is versioned and lives in the shared repository.

---

## 4. Technical Workflow

### Robot Description (URDF/Xacro)

The robot team's primary deliverable is a URDF (Unified Robot Description Format) file, typically written as Xacro for modularity. This file is the single source of truth for what the robot is — its geometry, physical properties, and how its joints are controlled. Every other team depends on this file being present and correct before the simulation can run.

### The Bridge as Interface Contract

The `ros_gz_bridge` configuration YAML is a machine-readable list of every topic the simulation exposes to ROS 2. Treat it as an authoritative document:

```yaml
- ros_topic_name: /camera/image_raw
  gz_topic_name: /world/main/model/robot/link/camera/sensor/camera/image
  ros_type_name: sensor_msgs/msg/Image
  gz_type_name: gz.msgs.Image
  direction: GZ_TO_ROS

- ros_topic_name: /joint_states
  gz_topic_name: /world/main/model/robot/joint_state
  ros_type_name: sensor_msgs/msg/JointState
  gz_type_name: gz.msgs.Model
  direction: GZ_TO_ROS
```

Any team writing a subscriber must find their topic in this file first. If it's not there, it needs to be added and reviewed before anyone writes code against it.

### Composed Launch Files

Each team ships their own launch file for their component. The integration layer assembles them with `IncludeLaunchDescription`:

```
launch/
├── robot.launch.py       # Robot team owns this
├── tasks.launch.py       # Task team owns this
├── control.launch.py     # Control team owns this
└── simulation.launch.py  # Integration lead: assembles all of the above
```

This means teams can launch and test their component in isolation. The integration lead is not a bottleneck for every launch change, and each team controls their own parameters and node configuration.

---

## 5. Team Autonomy Patterns

These patterns let teams work independently without waiting on each other.

### Topic Remapping

ROS 2 supports first-class topic remapping at launch time. A team can develop against any internal topic name and remap it to the agreed contract name without changing code:

```python
Node(
    package='control_team',
    executable='vla_node',
    remappings=[
        ('camera_in', '/camera/image_raw'),
        ('cmd_out', '/joint_trajectory_controller/joint_trajectory'),
    ]
)
```

### ROS 2 Bags as Development Stubs

Once the full stack has run once, any team can record the interface topics to a bag file and replay it during development. The AI team does not need the robot team's code running to develop their nodes — they replay a bag that publishes the agreed sensor topics.

```bash
# Record the interface topics
ros2 bag record /camera/image_raw /joint_states /tf

# Replay for offline development
ros2 bag play recorded_session.bag
```

This removes hard dependencies between teams during day-to-day work.

---

## 6. Key Properties of This Architecture

| Property | What it enables |
|---|---|
| **Sim-to-real** | The AI only talks to ROS 2. Swap Gazebo for a real robot without changing AI code. |
| **Headless testing** | The environment layer runs without a GUI on a server, enabling automated test runs. |
| **Isolated development** | Each team runs their component alone using bags or stubs — no full stack required. |
| **Simulator independence** | Standardized interfaces mean the simulation backend (Gazebo, Isaac Sim, etc.) is replaceable by updating the environment layer only. |
