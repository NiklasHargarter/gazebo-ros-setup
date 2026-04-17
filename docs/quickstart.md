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

The repo ships a `.env` (defaulting to `ROS_DISTRO=jazzy`) and the placeholder folders the compose file expects. No file-creation needed.

To use Humble instead, edit `.env` and set:

```bash
ROS_DISTRO=humble
```

---

## 3. Start the container

Allow Docker to open windows on your screen:

```bash
xhost +local:docker
```

Then start the container. **Pick one** of the two commands below based on whether you have an NVIDIA GPU.

Without NVIDIA GPU (CPU / Intel / Mesa):

```bash
docker compose up -d
```

With NVIDIA GPU:

```bash
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
```

First run takes a few minutes (pulling the image). Subsequent starts are seconds.

---

## 4. Open a shell inside

```bash
docker compose exec ros-gazebo zsh
```

Run this in any new terminal to get more shells into the same container. You'll need three open terminals for the bridge verification below.

{: .note }
**Shell:** the image ships with `zsh` configured with [Oh My Zsh](https://ohmyz.sh/) and the [Powerlevel10k](https://github.com/romkatv/powerlevel10k) prompt (autosuggestions, syntax highlighting, fzf-tab completion). The prompt's icons render best in a [Nerd Font](https://www.nerdfonts.com/) — set one in your terminal emulator. Prefer plain bash? Swap `zsh` for `bash` in any `docker compose exec` command — it's always available as a fallback.

---

## 5. Verify ROS 2

Inside the container:

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

## 6. Launch an empty Gazebo world

Confirms the simulator starts and the GUI passes through X11.

Jazzy:

```bash
gz sim -r empty.sdf
```

Humble:

```bash
ign gazebo -r empty.sdf
```

{: .note }
Running `gz sim` / `ign gazebo` with no arguments opens a world-selection dialog, not a running simulation. Pass the SDF file and `-r` (run on start) to go straight into a ticking empty world.

Leave the window open for the next step.

---

## 7. Verify the ROS 2 ↔ Gazebo bridge

This is what proves the image actually delivers on "ROS 2 + Gazebo working together" — Gazebo alone isn't enough. We bridge Gazebo's `/clock` topic into ROS 2 and watch it from the ROS side.

With the empty world from Step 6 still running, open a **second** container shell:

```bash
docker compose exec ros-gazebo zsh
```

Start the bridge for the clock topic.

Jazzy:

```bash
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock
```

Humble:

```bash
ros2 run ros_ign_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@ignition.msgs.Clock
```

The argument format is `<gz-topic>@<ros-msg-type>@<gz-msg-type>`. This is the whole bridge config — no YAML file needed for a single topic.

Open a **third** container shell:

```bash
docker compose exec ros-gazebo zsh
```

Confirm `/clock` is now visible from the ROS 2 side:

```bash
ros2 topic list
```

You should see `/clock` alongside `/parameter_events` and `/rosout`.

Stream messages:

```bash
ros2 topic echo /clock
```

A ticking clock stream = **bridge works end to end**. Ctrl-C out of each terminal when done.

---

## 8. Shut down

```bash
docker compose down
```

Stops and removes the container. Your code in `workspace/` stays — it lives on the host.

---

## Common commands

Rebuild the image from scratch:

```bash
docker compose up -d --build --no-cache
```

Build your workspace packages (run inside the container):

```bash
colcon build --symlink-install
```

Re-source the overlay manually (new shells do this automatically):

```bash
source /workspace/install/setup.zsh
```

---

## Next steps

- [Writing Your Own Nodes](writing-your-own-nodes)
- [Remote GUI Client](server-client) — split simulation from GUI across machines
- [Headless Rendering](headless-rendering) — run on a server with no display
