# Reproducible ROS 2 + Gazebo robot + sim

Runs the robot and Gazebo Fortress sim (ROS 2 Humble) in Docker — no ROS on
your host. That's the whole job of this repo.

Your code talks to it over ROS on the **host network**: run your nodes however
you like — a container with host networking from anywhere on your machine, or
natively on the host. How your code gets built/containerised is up to you. The
[`examples/`](examples) are reference, not a required pattern.

```
osrf/ros:humble-desktop-full         ← upstream, pulled once
  └── project-core  (core.Dockerfile) ← apt deps + entrypoint that auto-sources core_ws
```

Core source isn't baked into the image — it's cloned into `core_ws/` on the
host and bind-mounted at runtime, so build artifacts stay on the host.

Full docs: <https://niklashargarter.github.io/gazebo-ros-setup>

## Setup

```bash
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup
bin/install.sh        # wires ros-* shortcuts into your rc, offers to clone core source
```

`bin/install.sh` prints what it adds and asks first; `--print` edits nothing.
It ends by dropping you into a fresh shell with the `ros-*` shortcuts loaded.
See [docs/quickstart.md](docs/quickstart.md) for the full step-by-step (Docker
prereqs, NVIDIA, first build).

## Daily run

```bash
ros-upd && ros-zsh
launch          # ros2 launch hugo_moveit_config mobile_manipulation_gazebo.launch.py
```

## Common commands

| Command | What it does |
|---|---|
| `ros-upd` | Start core detached |
| `ros-zsh [cmd]` | Shell into core (or run a command) |
| `ros-ws-build` | `colcon build` core_ws, then restart core |
| `ros-build` | Rebuild the core image (after apt-dep changes) |
| `ros-restart` | Restart core |
| `ros-down` | Stop and remove the stack |

GPU overlay is on by default via `COMPOSE_FILE` in `.env` — drop `docker-compose.nvidia.yml` from that line if you have no NVIDIA GPU.

After someone bumps the pinned SHA in `bin/setup-core-ws.sh`:

```bash
cd core_ws/src/hugo_moveit_config && git fetch && git checkout <new-sha>
ros-ws-build
```

## Talking to the sim

Anything that speaks ROS on the host network can drive the robot — see
[docs/topics.md](docs/topics.md) for what's exposed. Run your nodes in a
container (host networking + `ipc: host` for shared-memory transport) or
natively; your choice.

[`examples/perception-demo`](examples/perception-demo) is one reference: a
two-node consumer (YOLO-World detector + head tracker) as its own compose
stack. It happens to build `FROM project-core`, but that's just convenient, not
required.

```bash
ros-upd                          # core
cd examples/perception-demo
docker compose build
docker compose run --rm detector bash -c "cd /workspace && colcon build"
docker compose up
```
