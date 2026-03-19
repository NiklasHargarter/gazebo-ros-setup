---
title: Home
layout: home
---
# ROS 2 Kilted & Gazebo Docker Environment

This project provides a fully containerized, GPU-accelerated development environment for ROS 2 (Kilted) and Gazebo. It features native NVIDIA GPU injection, X11 forwarding for GUI applications, headless rendering support (EGL), and a persistent `zsh` environment that automatically sources ROS.

## Prerequisites

Before using this setup, ensure your host machine has the following installed and configured:
1. [docker installation](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
2. [docker non root configuration](https://docs.docker.com/engine/install/linux-postinstall/)
3. [nvidia-container-toolkit installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian)
4. [nvidia-container-toolkit configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration)
## File Structure

Your project directory should look exactly like this:

```text
.
├── docker-compose.yml   # The container orchestration config
├── Dockerfile           # Builds the custom zsh/ROS image
├── container_zshrc      # Your custom zsh configuration
├── workspace/           # (Directory) Your mapped local code folder
└── .zsh_history         # (File) Stores your terminal history
```

## Initial setup
Before running the container for the very first time, you must create the history file and workspace directory on your host. If you skip this, Docker will accidentally create .zsh_history as a directory instead of a file.

Run this in the repo folder:
```bash
mkdir -p workspace
touch .zsh_history
```
## Usage Workflow

### 1. Start the Environment

To spin up the container in the background, run:
```bash
# Allow local Docker containers to display GUIs on your screen
xhost +local:docker

# Build and start the container
docker compose up -d --build
```

### 2. Open a Terminal

To start developing, drop into your pre-configured zsh shell:
```bash
docker compose exec ros-gazebo zsh
```

### 3. Running Gazebo

GUI Mode:
Because the environment natively forwards X11, you can launch Gazebo normally and it will appear on your host monitor:
```bash
gz sim
```

Headless Mode:
If you need to run camera sensors in headless mode (e.g., on a cloud server or without a monitor), temporarily wipe the $DISPLAY variable inline. This forces Gazebo to use the GPU directly via EGL instead of looking for a windowing system:
```bash
DISPLAY= gz sim -v 4 -s -r --headless-rendering sensors_demo.sdf
```

### 4. Shutting Down 

```bash
docker compose down
```
