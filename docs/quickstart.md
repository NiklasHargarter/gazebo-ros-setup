---
title: Quickstart (Linux)
layout: default
nav_order: 2
---

# Quickstart (Linux)

**Requires:** Ubuntu 22.04 (other distros may work, untested) · Docker · optional NVIDIA GPU.

---

## 1. Install prerequisites

Install Docker, configure it for non-root use, and (if you have an NVIDIA GPU) install and configure the NVIDIA Container Toolkit.

| Step | Link | Why |
|---|---|---|
| Install Docker | [docs.docker.com](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository){:target="_blank"} | The container engine |
| Docker non-root | [docs.docker.com](https://docs.docker.com/engine/install/linux-postinstall/){:target="_blank"} | Needed for X11 passthrough |
| *(NVIDIA only)* Toolkit install | [nvidia.com](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian){:target="_blank"} | GPU access inside the container |
| *(NVIDIA only)* Toolkit configure | [nvidia.com](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration){:target="_blank"} | Registers the plugin with Docker |

{: .note }
After the "Docker non-root" step, **log out and back in** (or reboot). `newgrp docker` works in one terminal but does not update your desktop session, and the GUI-spawning commands below need the updated group.

If you don't have an NVIDIA GPU, skip the last two rows — Gazebo falls back to Mesa software rendering. Slower, still functional.

---

## 2. Clone the repo

```bash
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup
```

The repo already ships a `.env` (defaulting to `ROS_DISTRO=jazzy`) and the empty `workspace/src/` and `.zsh_history_dir/` folders the compose file expects. No file-creation steps needed.

If you want Humble instead of Jazzy, edit `.env` and set `ROS_DISTRO=humble`.

---

## 3. Start the container

```bash
# Let Docker open windows on your screen
xhost +local:docker

# Base — CPU / Intel / no GPU
docker compose up -d

# Or: with NVIDIA GPU
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
```

First run takes a few minutes (pulling the image). Subsequent starts are seconds.

---

## 4. Open a shell inside

```bash
docker compose exec ros-gazebo zsh
```

Run this in any new terminal to get more shells into the same container.

---

## 5. Verify ROS 2

```bash
ros2 topic list
```

Expected:
```
/parameter_events
/rosout
```

These two appear automatically when the ROS 2 middleware initialises — proof it's running.

---

## 6. Launch Gazebo

**Empty world — confirm the GUI opens:**

| Distro | Command |
|---|---|
| Humble | `ign gazebo empty.sdf` |
| Jazzy | `gz sim empty.sdf` |

{: .note }
Running `gz sim` / `ign gazebo` with no arguments opens a world-selection dialog, not a simulation. Pass `empty.sdf` explicitly to go straight to a running empty world.

**Sensor demo — confirm data flows:**

| Distro | Command |
|---|---|
| Humble | `ign gazebo sensors_demo.sdf` |
| Jazzy | `gz sim sensors_demo.sdf` |

Then in a second terminal inside the container:

| Distro | Commands |
|---|---|
| Humble | `ign topic -l` · `ign topic -e --topic /thermal_camera` |
| Jazzy  | `gz topic -l` · `gz topic -e --topic /thermal_camera` |

Streaming messages = setup works.

---

## 7. Shut down

```bash
docker compose down
```

Stops and removes the container. Your code in `workspace/` stays — it lives on the host.

---

## Common commands

```bash
docker compose up -d                     # start (no rebuild)
docker compose up -d --build --no-cache  # rebuild from scratch
docker compose exec ros-gazebo zsh       # second terminal in same container
colcon build --symlink-install           # build your workspace packages (in container)
source /workspace/install/setup.zsh      # source overlay (automatic in new shells)
```

---

## Next steps

- [Writing Your Own Nodes](writing-your-own-nodes)
- [Remote GUI Client](server-client) — split simulation from GUI across machines
- [Headless Rendering](headless-rendering) — run on a server with no display
