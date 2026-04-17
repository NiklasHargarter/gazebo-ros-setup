---
title: Quickstart (Linux)
layout: default
nav_order: 2
---

# Quickstart (Linux)

**Requires:** Ubuntu 22.04 (other distros may work, untested) · Docker · optional NVIDIA GPU.

This guide gets you from zero to a running Gazebo simulation in the container.

---

## 1. Install prerequisites

| Step | Link | Why |
|---|---|---|
| Install Docker | [docs](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) | The container engine |
| Docker non-root | [docs](https://docs.docker.com/engine/install/linux-postinstall/) | Needed for X11 passthrough |
| *(NVIDIA users only)* NVIDIA Container Toolkit | [install](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian) · [configure](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) | GPU access inside the container |

If you don't have an NVIDIA GPU, skip the last row — Gazebo will fall back to Mesa software rendering. Functional, just slower.

---

## 2. Clone and prepare

```bash
git clone <repo-url>
cd gazebo-ros-setup

mkdir -p workspace/src            # your code goes here later
touch .zsh_history                 # must be a file, not a folder
chmod 666 .zsh_history             # container runs as root, needs write access
echo "ROS_DISTRO=jazzy" > .env     # or humble
```

{: .note }
If you skip `touch .zsh_history`, Docker creates a *directory* by that name and the volume mount breaks. `chmod 666` lets the container (root, different UID) write to it.

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

First run takes a few minutes (downloading the image). Subsequent starts are seconds.

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

Those two appear automatically when ROS 2 middleware initialises — proof it's running.

---

## 6. Launch Gazebo

**Empty world — confirm the GUI opens:**

| Distro | Command |
|---|---|
| Humble | `ign gazebo` |
| Jazzy | `gz sim` |

A window with a grid floor should appear. Ctrl-C to close.

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

Stops and removes the container. Your code in `workspace/` lives on the host, so it stays.

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
