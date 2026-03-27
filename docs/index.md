---
title: Getting Started
layout: home
nav_order: 1
---

# Getting Started with ROS 2 & Gazebo

> **Distro used in this guide:** ROS 2 Humble + Gazebo Fortress — the robotics team default.
> If you need Jazzy + Harmonic instead, see the reference table at the bottom.

---

## What is this?

This repo gives you a ready-to-run robotics development environment without installing anything on your own machine. It uses **Docker** — a tool that packages software and all its dependencies into a self-contained unit called a *container*. You can think of it as a lightweight isolated Linux machine that lives inside your real one. When you're done, you just stop the container; nothing is left behind on your host system.

Inside the container you get:

- **ROS 2 Humble** — the Robot Operating System, a framework for writing robot software as a graph of communicating nodes
- **Gazebo Fortress** — a physics simulator where you can drop in a robot world and have it produce realistic sensor data without any real hardware
- GPU passthrough via the NVIDIA Container Toolkit, so the simulator can use your GPU for rendering
- X11 forwarding, so graphical windows (like the Gazebo UI) appear on your desktop even though they're running inside the container

---

## Assumptions

- Host OS: **Ubuntu 22.04** (other Linux distros may work but are untested)
- You have an **NVIDIA GPU** and its drivers installed (see [No NVIDIA GPU](#no-nvidia-gpu) if you don't)
- You're comfortable running commands in a terminal

---

## 1. Install Prerequisites

Four things need to be on your host machine before you start. Do them in order — each one builds on the last.

| Step | What it is | Why you need it |
|---|---|---|
| [Install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) | The container engine | Runs and manages containers |
| [Configure Docker for non-root use](https://docs.docker.com/engine/install/linux-postinstall/) | Lets your user run Docker without `sudo` | Required for X11 display passthrough to work correctly |
| [Install NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian) | Plugin that gives containers GPU access | Without it, Gazebo can't use your GPU |
| [Configure NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) | Registers the plugin with Docker | Activates the `nvidia.com/gpu` device injection used in `docker-compose.yml` |

---

## 2. Clone and Prepare the Repo

```bash
git clone <repo-url>
cd gazebo-ros-setup
```

Then create the three files Docker expects to find before the first run:

```bash
mkdir -p workspace/src   # your code goes here later
touch .zsh_history        # shell history file — must exist as a file, not a folder
echo "ROS_DISTRO=humble" > .env   # tells Docker which ROS version to use
```

{: .note }
If you skip `touch .zsh_history`, Docker will create a *directory* called `.zsh_history` instead of a file, which breaks the volume mount. The touch command creates an empty file with the right name.

After this step your directory looks like:

```text
.
├── docker-compose.yml   # describes the container: image, mounts, GPU, network
├── Dockerfile           # recipe for building the ROS + Gazebo image
├── container_zshrc      # shell config that gets copied into the container
├── .env                 # sets ROS_DISTRO=humble
├── workspace/           # mounted into the container at /workspace
└── .zsh_history         # mounted so your history persists between sessions
```

---

## 3. Build and Start the Container

```bash
# Allow Docker containers to open windows on your screen
xhost +local:docker

# Build the image and start the container in the background (-d = detached)
docker compose up -d --build
```

`docker compose up` reads `docker-compose.yml`, builds the image described in the `Dockerfile` (this takes a few minutes the first time — it's downloading and installing ROS 2 and Gazebo), then starts the container. The `--build` flag tells it to rebuild if anything has changed. After the first time you can omit `--build` if you haven't changed the Dockerfile.

---

## 4. Open a Terminal Inside the Container

The container is now running in the background. To get a shell inside it:

```bash
docker compose exec ros-gazebo zsh
```

`exec` connects you to the already-running container named `ros-gazebo` and opens a `zsh` shell. Your prompt will change, indicating you're now inside the container. You can open as many terminals as you like by running this command again in a new tab.

---

## 5. Verify ROS 2 is Active

Inside the container:

```bash
ros2 topic list
```

You should see:
```
/parameter_events
/rosout
```

These two topics are created automatically by the ROS 2 middleware as soon as it initialises — you haven't started any nodes yet, but their presence confirms ROS 2 is running and your environment is sourced correctly.

---

## 6. Launch Gazebo

### Empty world — confirm the GUI opens

```bash
ign gazebo
```

A window should open on your desktop showing an empty Gazebo world with a grid floor and a toolbar. This confirms two things at once: the simulator is working, and X11 forwarding is passing the GUI through to your screen. Close it with Ctrl-C in the terminal when you're done.

### Sensor demo world — confirm simulation produces data

```bash
ign gazebo sensors_demo.sdf
```

The Gazebo window opens again, this time with a world that contains a robot equipped with sensors (thermal camera, depth camera, lidar, and others). The simulation is running and the sensors are actively producing data.

To confirm data is flowing, open a **second terminal** in the container (`docker compose exec ros-gazebo zsh` in a new tab) and run:

```bash
# See all topics the simulation is publishing
ign topic -l

# Check that a publisher is active on the thermal camera topic
ign topic -i --topic /thermal_camera

# Stream live messages from the thermal camera (Ctrl-C to stop)
ign topic -e --topic /thermal_camera
```

If `ign topic -i` shows a publisher address and `ign topic -e` prints a stream of data, **the setup is complete and working.**

---

## 7. Shut Down

```bash
docker compose down
```

This stops and removes the container. Your files in `workspace/` are safe — they live on your host machine, not inside the container.

---

## Reference

### Distro — Gazebo compatibility

| Distro | Gazebo version | Launch command | |
|---|---|---|---|
| Humble | Fortress | `ign gazebo` | **default — robotics team** |
| Jazzy | Harmonic | `gz sim` | |

### Common commands

```bash
# Start without rebuilding (image already exists)
docker compose up -d

# Force a full rebuild from scratch
docker compose up -d --build --no-cache

# Open a second terminal in the same running container
docker compose exec ros-gazebo zsh

# Build your workspace packages inside the container
colcon build --symlink-install

# After building, source the overlay (done automatically on next shell open)
source /workspace/install/setup.zsh
```

---

## No NVIDIA GPU

Remove the `devices` block from `docker-compose.yml`. Headless GPU rendering won't work, but GUI mode via X11 will still run using software rendering (Mesa) — performance will be limited but functional for basic use.

---

## Next Steps

- **Headless rendering** — run Gazebo on a server with no display, using EGL: [Headless Rendering](headless-rendering)
- **Writing your own nodes** — add your own ROS 2 nodes to the workspace: [Writing Your Own Nodes](writing-your-own-nodes)
