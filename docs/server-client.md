---
title: Remote GUI Client
layout: default
nav_order: 5
---

# Remote GUI Client

By default, the container runs both the physics simulation and the GUI in the same place. This page covers splitting them: the **server** runs the simulation headlessly on a workstation or remote machine, and a **client** connects from a separate machine to display the GUI — without running any simulation itself.

**Humble + Fortress:**
```
[Server — Linux workstation]            [Client — any machine]
  ign gazebo -s (physics only)   ←→      ign gazebo -g (GUI only)
  IGN_PARTITION=ros2_sim                 IGN_PARTITION=ros2_sim
  IGN_IP=<server IP>                     IGN_IP=<server IP>
```

**Jazzy + Harmonic:**
```
[Server — Linux workstation]            [Client — any machine]
  gz sim -s (physics only)       ←→      gz sim -g (GUI only)
  GZ_PARTITION=ros2_sim                  GZ_PARTITION=ros2_sim
  GZ_IP=<server IP>                      GZ_IP=<server IP>
```

The partition variable scopes which simulation instances talk to each other on the network. Both sides must use the same partition name and the server's IP must be reachable from the client.

---

## Server setup (Linux workstation)

### 1. Set your workstation's IP in `.env`

Open `.env` and set `WORKSTATION_IP` to the IP address of the server machine — the one the client will connect to:

```env
ROS_DISTRO=humble   # or jazzy
WORKSTATION_IP=192.168.1.100   # replace with your server's actual IP
```

This value gets injected into the container as `IGN_IP` (Humble) or `GZ_IP` (Jazzy), telling the transport layer which network interface to advertise on.

### 2. Start the container with the server overlay

The server env vars live in a separate overlay file (`docker-compose.server.yml`) so the base setup stays clean. Layer it on top of the base compose file:

```bash
docker compose -f docker-compose.yml -f docker-compose.server.yml up
```

Add `-f docker-compose.nvidia.yml` too if you have an NVIDIA GPU. The overlay sets both `GZ_*` and `IGN_*` variables; whichever distro you run picks up the one it reads and ignores the other.

### 3. Start the simulation server

Inside the container, run Gazebo in server-only mode with headless rendering:

**Humble (Fortress):**
```bash
DISPLAY= ign gazebo -v 4 -s -r --headless-rendering sensors_demo.sdf
```

**Jazzy (Harmonic):**
```bash
DISPLAY= gz sim -v 4 -s -r --headless-rendering sensors_demo.sdf
```

The `-s` flag starts only the physics server — no GUI window opens. The simulation runs and publishes topics, waiting for a client to connect.

---

## Client setup

Make sure you have a working Gazebo install on the client machine. On macOS, see the [macOS Setup](macos-setup) guide. On Linux, the container itself can serve as the client.

Connect to the server:

**Humble (Fortress):**
```bash
export IGN_PARTITION=ros2_sim
export IGN_IP=<server IP>
ign gazebo -g
```

**Jazzy (Harmonic):**
```bash
export GZ_PARTITION=ros2_sim
export GZ_IP=<server IP>
gz sim -g
```

Replace `<server IP>` with the same IP you set in `WORKSTATION_IP` on the server.
