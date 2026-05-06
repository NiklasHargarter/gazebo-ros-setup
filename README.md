# Reproducible ROS 2 + Gazebo dev environment

Two image layers, both built locally.

```
osrf/ros:humble-desktop-full         ← upstream, pulled once
  └── project-core  (core.Dockerfile)
        ← apt deps, zsh shell, entrypoint that auto-sources the workspace
        └── your consumer  (FROM project-core)
              ← your deps, communicates over ROS topics
```

Core runs the robot and simulation. Consumers connect over ROS topics/services/actions via host network.
The `core_ws` is bind-mounted from the host so build artifacts are visible outside the container.

## Shell shortcuts

The repo ships a set of `ros-*` shortcuts that wrap `docker compose` with the right files and options.
Add these two lines to your `~/.zshrc` (or `~/.bashrc`):

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"   # path to this repo
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

Then reload your shell (`source ~/.zshrc`). Run `ros-help` to see all available commands.

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
git -C core_ws/src/hugo_moveit_config checkout 3eb7c8d5c756bfa08947a4466f68e6737e1d368d

# 3. Build the core image (installs apt deps, sets up entrypoint)
ros-build

# 4. Start the container (also grants X11 access automatically)
ros-upd

# 5. First time only — build the workspace inside the container
ros-zsh
cd /core_ws && colcon build
exit

# 6. Restart so the entrypoint picks up the built workspace
ros-restart

# 7. Shell in and launch the sim
ros-zsh
launch   # alias for: ros2 launch hugo_moveit_config mobile_manipulation_gazebo.launch.py
```

After the first `colcon build`, build artifacts live in `core_ws/build/` and `core_ws/install/` on the host.
Every subsequent `ros-upd` sources the workspace automatically — no manual `source` call needed.

## Day-to-day

```bash
ros-upd          # start the stack
ros-zsh          # shell into core (workspace already sourced)
launch           # run the sim
ros-down         # stop the stack
```

## Adding a consumer

```bash
# 1. Build your consumer image (use consumer-template/ as a starting point)
docker build -t my-consumer:humble --build-arg ROS_DISTRO=humble consumer-template/

# 2. Add a service block in docker-compose.yml (copy the consumer-example block),
#    set image: my-consumer:humble and give it a unique profiles: name.

# 3. Start core + consumer together
ros-upd --profile example

# 4. Shell into the consumer
ros-exec consumer-example
```

The consumer inherits the entrypoint from `project-core` so its shell is sourced automatically.
Connect to the running sim over ROS topics — no extra network configuration needed.

## Rebuilding

Rebuild the core image whenever apt deps change:

```bash
ros-build
```

Rebuild the workspace inside the container whenever source files change:

```bash
ros-zsh
cd /core_ws && colcon build
```
