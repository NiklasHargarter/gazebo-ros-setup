---
title: Home
layout: home
nav_order: 1
---

# ROS 2 & Gazebo Docker Environment

This project provides a fully containerized, GPU-accelerated development environment for ROS 2 and Gazebo. It supports multiple ROS distributions (Humble, Jazzy, etc.) and includes native NVIDIA GPU injection, X11 forwarding for GUI applications, headless rendering via EGL, and a persistent `zsh` environment that automatically sources the correct ROS version.

---

## Prerequisites

Before using this setup, ensure your host machine has the following installed and configured:

1. [Docker installation](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
2. [Docker non-root configuration](https://docs.docker.com/engine/install/linux-postinstall/)
3. [NVIDIA Container Toolkit installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian)
4. [NVIDIA Container Toolkit configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration)

---

## File Structure

Your project directory should look exactly like this:

```text
.
├── docker-compose.yml   # Container orchestration config
├── Dockerfile           # Builds the custom zsh/ROS image
├── container_zshrc      # Custom zsh configuration
├── .env                 # Sets ROS_DISTRO (e.g. ROS_DISTRO=jazzy)
├── workspace/           # Your mapped local code folder
└── .zsh_history         # Stores your terminal history
```

---

## Initial Setup

Before running the container for the very first time, create the history file and workspace directory on your host. If you skip this, Docker will accidentally create `.zsh_history` as a directory instead of a file.

Run this in the repo folder:

```bash
mkdir -p workspace
touch .zsh_history
```

---

## Usage

### 1. Start the Environment

```bash
# Allow local Docker containers to display GUIs on your screen
xhost +local:docker

# Build and start the container (defaults to Jazzy)
docker compose up -d --build

# OR specify a ROS version explicitly
ROS_DISTRO=jazzy docker compose up -d --build
```

### 2. Switching ROS Versions

The environment defaults to **ROS 2 Jazzy**. To use a different version:

**Option A — environment variable:**

```bash
ROS_DISTRO=humble docker compose up -d --build
```

**Option B — `.env` file:**

Create a `.env` file in the root directory:

```env
ROS_DISTRO=jazzy
```

Then run:

```bash
docker compose up -d --build
```

### 3. Open a Terminal

```bash
docker compose exec ros-gazebo zsh
```

### 4. Running Gazebo

**GUI mode** — X11 forwarding is handled automatically:

```bash
gz sim
```

**Headless mode** — for servers or machines without a display. Unsets `$DISPLAY` to force EGL rendering directly via the GPU:

Jazzy:
```bash
DISPLAY= gz sim -v 4 -s -r --headless-rendering sensors_demo.sdf
```

Humble:
```bash
DISPLAY= ign gazebo -v 4 -s -r --headless-rendering sensors_demo.sdf
```

### 5. Shut Down

```bash
docker compose down
```

---

## Notes

| Distro | Gazebo version | Launch command |
|---|---|---|
| Jazzy | Harmonic | `gz sim` |
| Humble | Fortress | `ign gazebo` |
