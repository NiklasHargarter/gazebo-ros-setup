# Contains details for easily replicatable gazebo-ros2 setup (Humble, Jazzy, etc.).
[link to docs](https://niklashargarter.github.io/gazebo-ros-setup/)

## Quick usage

Base (CPU/Intel, local-only):
```bash
docker compose up
```

With NVIDIA GPU:
```bash
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up
```

Server-client networking (remote GUI, see `docs/server-client.md`):
```bash
docker compose -f docker-compose.yml -f docker-compose.server.yml up
```

Stack `-f` files for any combination (e.g. NVIDIA + server).

## Shell shortcuts

Quality-of-life wrappers for the common `docker compose` commands live in
[`shell/ros-shortcuts.sh`](shell/ros-shortcuts.sh). Source it once from your
`~/.zshrc` or `~/.bashrc`:

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"   # path to your clone
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

Then from anywhere:

```bash
ros-upd           # start the stack detached
ros-zsh           # drop into a zsh in the running container
ros-zsh ros2 topic list   # one-off command inside the container
ros-logs          # tail logs
ros-down          # stop the stack
```

Switch overlays/distros without editing files: `ros-profile nvidia`,
`ros-profile nvidia-server`, `ros-distro jazzy`. These persist to the repo's
`.env` (same file Docker Compose reads), so new shells pick them up automatically.
Run `ros-help` for the full list.

## Examples

Two ready-to-run setups live under [`examples/`](examples/):

- [TurtleBot 4 (Jazzy)](examples/turtlebot4/) — full TB4 simulator stack on top of the base image.
- [Camera World](examples/camera_world/) — minimal custom SDF world with a camera sensor and a Python subscriber node.
