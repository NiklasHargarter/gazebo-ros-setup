---
title: Writing Your Own Nodes
layout: default
nav_order: 4
---

# Writing your own nodes

Consumer packages live under `./workspace/src/`, bind-mounted into
`/workspace` inside the consumer container. Edits on the host are visible
immediately — no image rebuild.

```
host: ./workspace/        ↔   consumer: /workspace/
        src/                          src/
        install/          ←   colcon build writes here
        build/
        log/
```

Source layering inside the consumer container (auto-sourced in shells):

```
/opt/ros/${ROS_DISTRO}     base ROS
/opt/ros_overlay           core (baked into project-core)
/workspace/install         your packages (sourced if built)
```

## Create a package

```bash
docker compose --profile example up -d
docker compose exec consumer-example zsh
cd /workspace/src
ros2 pkg create --build-type ament_python my_package --node-name my_node
```

C++: `--build-type ament_cmake`.

## Build

```bash
cd /workspace
colcon build --symlink-install
```

`--symlink-install` symlinks Python sources, so edits take effect without
rebuild. New entry points or `setup.py` changes still need a rebuild.

Open a new shell to pick up the overlay, or `source install/setup.zsh`.

## Run

```bash
ros2 run my_package my_node
```

## Verify from another shell

```bash
docker compose exec core bash
ros2 topic echo /my_topic
```

## Package layout

```
workspace/src/my_package/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/my_package
└── my_package/
    ├── __init__.py
    └── my_node.py
```
