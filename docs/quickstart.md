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

## 2. Clone this repo

```bash
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup
```

---

## 3. Clone the core source

The core stack consists of three repos. Clone them all into `core_ws/src/`:

```bash
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
cd core_ws/src/turtlebot3_manipulation && git checkout humble && cd -
```

`core_ws/src/` is gitignored so these clones won't show up as changes to the dev-container repo.

---

## 4. Build the project-core image

Core's apt deps and source packages are baked into a local image. No published image exists — every machine builds it once:

```bash
docker build -f core.Dockerfile \
             -t project-core:humble \
             --build-arg ROS_DISTRO=humble .
```

Only rerun this when core *dependencies* change (new apt package, new ROS package dep) or when the core source itself changes. Rebuilding is the one step to pick up core changes.

---

## 5. Build your consumer image

Your consumer image extends `project-core` with your own deps (AI/CV libraries, custom apt packages, etc.). The `consumer-template/` directory is a starting point:

```bash
docker build -t my-consumer:humble \
             --build-arg ROS_DISTRO=humble \
             consumer-template/
```

Edit `consumer-template/Dockerfile` to add your deps before building.

---

## 6. Configure `.env`

```bash
cp .env.example .env
```

The default only needs `ROS_DISTRO`:

```env
ROS_DISTRO=humble
```

---

## 7. Start the stack

Allow Docker to open windows on your screen:

```bash
xhost +local:docker
```

Start core. **Pick one** based on whether you have an NVIDIA GPU.

Without NVIDIA GPU (CPU / Intel / Mesa):

```bash
docker compose up -d
```

With NVIDIA GPU:

```bash
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
```

Start a consumer (optional):

```bash
docker compose --profile example up -d
```

---

## 8. Open a shell in core

```bash
docker compose exec core bash
```

---

## 9. Verify ROS 2

Inside the container:

```bash
ros2 topic list
```

Expected:

```
/parameter_events
/rosout
```

---

## 10. Launch the HuGO simulation

Confirms the simulator starts, the GUI passes through X11, and the full core stack comes up:

```bash
ros2 launch hugo_moveit_config gezebo.launch.py
```

Gazebo and RViz should open with the HuGO robot loaded. Ctrl-C to stop.

---

## 11. Verify ROS 2 topics

With the simulation running, open a **second** shell:

```bash
docker compose exec core bash
ros2 topic list
```

You should see topics including `/joint_states`, `/tf`, `/clock`, and the controller topics. A populated topic list confirms the bridge and ros2_control stack are running end to end.

---

## 12. Shut down

```bash
docker compose down
```

---

## Common commands

Rebuild the core image after a change:

```bash
docker build -f core.Dockerfile -t project-core:humble --build-arg ROS_DISTRO=humble .
```

Build your consumer workspace packages (run inside a consumer container):

```bash
cd /workspace
colcon build --symlink-install
```

---

## Next steps

- [Architecture](architecture) — full picture of the core / consumer image layers
- [Core Stack](core-stack) — building and iterating on the core image
- [Writing Your Own Nodes](writing-your-own-nodes) — adding consumer packages
- [Remote GUI Client](server-client) — split simulation from GUI across machines
- [Headless Rendering](headless-rendering) — run on a server with no display
