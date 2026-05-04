# Reproducible ROS 2 + Gazebo dev environment

Two image layers, both built locally.

```
osrf/ros:humble-desktop-full         ← upstream, pulled once
  └── project-core  (core.Dockerfile)
        ← apt deps + core source built with colcon
        └── your consumer  (FROM project-core)
              ← your deps, communicates over ROS topics
```

Core runs the robot and simulation. Consumers connect over ROS topics/services/actions via host network.

## Setup (new machine)

```bash
# 1. Clone this repo
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup

# 2. Clone core source into core_ws/src/
#    robotis_hand must be pinned to 0.0.3 — newer versions have a broken dep chain
git clone --branch 0.0.3 https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config

# 3. Build the core image
docker build -f core.Dockerfile -t project-core:humble --build-arg ROS_DISTRO=humble .

# 4. Allow X11 passthrough and start core
xhost +local:docker
docker compose up -d

# 5. Shell into core and launch the sim
docker compose exec core zsh
launch   # alias for: ros2 launch hugo_moveit_config mobile_base_gazebo.launch.py
```

## Adding a consumer

```bash
# Build your consumer image (uses consumer-template/ as a starting point)
docker build -t my-consumer:humble --build-arg ROS_DISTRO=humble consumer-template/

# Start it alongside core
docker compose --profile example up -d
docker compose exec consumer-example zsh
```

Your consumer image is `FROM project-core` so it has the full core workspace sourced. Connect to the running sim over ROS topics — no extra configuration needed.

## Rebuilding core

Rebuild whenever core source or apt deps change:

```bash
docker build -f core.Dockerfile -t project-core:humble --build-arg ROS_DISTRO=humble .
```
