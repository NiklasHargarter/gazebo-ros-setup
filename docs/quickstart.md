---
title: Quickstart (Linux)
layout: default
nav_order: 2
---

# Quickstart (Linux)

**Requires:** Ubuntu 22.04+ · Docker · optional NVIDIA GPU.

This repo provides the dev-container infrastructure. You bring the core source (private repo) and your own consumer code. Both images are built locally on each machine — nothing with private source is ever published.

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
```

Add to your `~/.zshrc` (or `~/.bashrc`):

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

Reload your shell:

```bash
source ~/.zshrc
```

Run `ros-help` to see all available commands.

---

## 3. Clone the core source

```bash
git clone --branch 0.0.3 https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git -C core_ws/src/hugo_moveit_config checkout 3eb7c8d5c756bfa08947a4466f68e6737e1d368d
```

`core_ws/src/*` is gitignored. `robotis_hand` must be pinned to `0.0.3` — newer versions have a broken dependency chain.

---

## 4. Configure `.env`

```bash
cp .env.example .env
```

The default only needs `ROS_DISTRO`:

```env
ROS_DISTRO=humble
```

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

X11 passthrough is granted automatically. For NVIDIA GPU:

```bash
ros-profile nvidia
ros-upd
```

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
| `ros-help` | Full command reference |

---

## Next steps

- [Architecture](architecture) — full picture of the core / consumer image layers
- [Core Stack](core-stack) — building and iterating on the core workspace
- [Writing Your Own Nodes](writing-your-own-nodes) — adding consumer packages
- [Remote GUI Client](server-client) — split simulation from GUI across machines
- [Headless Rendering](headless-rendering) — run on a server with no display
