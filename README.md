# Reproducible ROS 2 + Gazebo dev environment
[Full docs](https://niklashargarter.github.io/gazebo-ros-setup/)

Two image layers, both built locally. Nothing is published.

```
osrf/ros:humble-desktop-full         ← upstream, pulled once
  └── project-core  (core.Dockerfile)
        ← core apt deps + core source baked in
        └── your consumer  (your own Dockerfile, FROM project-core)
              ← your deps (torch, opencv, custom libs, ...)
```

Core and consumers run as **separate containers** in one compose stack, communicating over ROS topics/services/actions via host network.

## Setup (new machine)

```bash
# 1. Clone this repo
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup

# 2. Clone the core source into the expected location
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
cd core_ws/src/turtlebot3_manipulation && git checkout humble && cd -

# 3. Build the project-core image (bakes in core source + deps)
docker build -f core.Dockerfile -t project-core:humble --build-arg ROS_DISTRO=humble .

# 4. Build your consumer image (start from consumer-template/Dockerfile)
docker build -t my-consumer:humble --build-arg ROS_DISTRO=humble consumer-template/

# 5. Configure .env
cp .env.example .env

# 6. Start core
xhost +local:docker
docker compose up -d

# 7. Start a consumer (optional, uses compose profiles)
docker compose --profile example up -d
```

See the [Quickstart](docs/quickstart.md) for the full walkthrough.

## Compose profiles

Consumers are opt-in via compose profiles. The `core` service always starts; consumers start only when their profile is requested:

```bash
docker compose up -d                              # core only
docker compose --profile example up -d            # core + consumer-example
```

Hardware overlays stack on top:

```bash
# NVIDIA GPU
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d

# Server-client networking (remote GUI)
docker compose -f docker-compose.yml -f docker-compose.server.yml up -d
```

## Shell shortcuts

Quality-of-life wrappers live in [`shell/ros-shortcuts.sh`](shell/ros-shortcuts.sh). Source it once:

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

```bash
ros-upd                        # start core detached
ros-zsh                        # shell into core container
ros-exec consumer-example      # shell into a consumer container
ros-zsh ros2 topic list        # one-off command in core
ros-logs                       # tail logs
ros-down                       # stop the stack
```

Switch hardware overlays: `ros-profile nvidia`, `ros-profile nvidia-server`. Switch distros: `ros-distro humble`. Run `ros-help` for the full list.

## Adding a consumer service

Copy the `consumer-example` block in `docker-compose.yml`, give it a name and profile, point it at your consumer image. Start it with `docker compose --profile <name> up`.

## Consumer template

`consumer-template/` is a starting point for a consumer Dockerfile. It includes an optional block for the opinionated zsh shell (Oh My Zsh + Powerlevel10k). Copy the directory into your consumer repo and edit from there.
