---
title: Quickstart (Linux)
layout: default
nav_order: 2
---

# Quickstart (Linux)

**Requires:** Ubuntu 22.04+ · Docker · optional NVIDIA GPU.

This repo gets the robot + Gazebo sim running. You bring the core source (private repo); the core image is built locally on each machine, so nothing private is ever published. Your own code connects over ROS afterwards — that's up to you.

---

## 1. Install prerequisites

| Step | Link | Why |
|---|---|---|
| Install Docker | [docs.docker.com](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository){:target="_blank"} | The container engine |
| Docker non-root | [docs.docker.com](https://docs.docker.com/engine/install/linux-postinstall/){:target="_blank"} | Needed for X11 passthrough |
| *(NVIDIA only)* Toolkit install | [nvidia.com](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian){:target="_blank"} | GPU access inside the container |
| *(NVIDIA only)* Toolkit configure | [nvidia.com](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration){:target="_blank"} | Registers the plugin with Docker |

{: .note }
After the "Docker non-root" step, **log out and back in** (or reboot). `newgrp docker` works in one terminal but does not update your desktop session.

---

## 2. Clone this repo and set up shell shortcuts

```bash
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup
bin/install.sh
```

`bin/install.sh` shows the two lines it wants to add to your `~/.zshrc` (or
`~/.bashrc`), asks before appending, sets up `.env` (step 4), offers to clone
the core source (step 3), then drops you into a fresh shell with the shortcuts
loaded. It works for bash and zsh and edits nothing without a `y`.

Prefer to do it by hand? Run `bin/install.sh --print` to see the lines, add them
to your rc file, then reload (`source ~/.zshrc`):

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

---

## 3. Clone the core source

`bin/install.sh` offers this; to do it directly:

```bash
bin/setup-core-ws.sh
```

This clones `robotis_hand` (pinned to `0.0.3` — newer versions have a broken
dependency chain), `turtlebot3_manipulation`, and `hugo_moveit_config` (pinned
SHA) into `core_ws/src/`. `core_ws/src/*` is gitignored — every machine clones
its own copy.

---

## 4. Configure `.env`

`bin/install.sh` already created `.env` and set the overlay from the GPU
question. To do it by hand instead:

```bash
cp .env.example .env
```

Two keys: `ROS_DISTRO` (default `humble`) and `COMPOSE_FILE`. Drop
`docker-compose.nvidia.yml` from `COMPOSE_FILE` if you have no GPU.

---

## 5. Build the core image

```bash
ros-build
```

This installs apt dependencies and sets up the entrypoint. Only rerun when apt dependencies or the `core.Dockerfile` change.

---

## 6. Start the stack

```bash
ros-upd
```

X11 passthrough is granted automatically. The NVIDIA overlay is on by default
(via `COMPOSE_FILE` in `.env`) — drop `docker-compose.nvidia.yml` from that line
if you have no GPU.

---

## 7. Build the workspace (first time only)

```bash
ros-zsh
cd /core_ws && colcon build
exit
ros-restart
```

Build artifacts appear in `core_ws/build/` and `core_ws/install/` on the host. Every subsequent `ros-upd` sources the workspace automatically — no manual `source` call needed.

---

## 8. Launch the simulation

```bash
ros-zsh
launch
```

Gazebo and RViz should open with the robot loaded. Ctrl-C to stop.

---

## 9. Verify ROS 2 topics

With the simulation running, open a second shell:

```bash
ros-zsh
ros2 topic list
```

You should see topics including `/joint_states`, `/tf`, `/clock`, and the controller topics.

---

## 10. Shut down

```bash
ros-down
```

---

## Common commands

| Command | What it does |
|---|---|
| `ros-upd` | Start the stack detached |
| `ros-zsh` | Shell into core |
| `ros-exec <service>` | Shell into any service |
| `ros-build` | Rebuild the core image |
| `ros-restart` | Restart the core container |
| `ros-down` | Stop and remove the stack |
| `ros-logs` / `ros-ps` | Tail logs / show status |
| `ros-ws-build` | Rebuild core_ws, then restart core |

---

## Next steps

- [Architecture](architecture) — core / consumer image layers and how teams plug in
- [Topics](topics) — what the running sim exposes
- [`examples/perception-demo`](https://github.com/NiklasHargarter/gazebo-ros-setup/tree/main/examples/perception-demo) — a working two-node consumer as its own compose stack
