---
title: Remote GUI Client
layout: default
nav_order: 4
---

# Remote GUI Client

By default, the container runs both the physics simulation and the GUI in the same place. This page covers splitting them: the **server** runs the simulation headlessly on a workstation or remote machine, and a **client** connects from a separate machine to display the GUI — without running any simulation itself.

```
[Server — Linux workstation]          [Client — any machine]
  ign gazebo -s (physics only)   ←→    ign gazebo -g (GUI only)
  IGN_PARTITION=ros2_sim               IGN_PARTITION=ros2_sim
  IGN_IP=<server IP>                   IGN_IP=<server IP>
```

Ignition transport uses `IGN_PARTITION` to scope which simulation instances talk to each other on the network. Both sides must use the same partition name and the server's IP must be reachable from the client.

{: .important }
**Needs retesting on Humble.** The setup described here was originally tested with a Jazzy client. The instructions below reflect the corrected Humble/Fortress configuration — verify `IGN_PARTITION` / `IGN_IP` discovery works end-to-end before relying on this.

---

## Server setup (Linux workstation)

### 1. Set your workstation's IP in `.env`

Open `.env` and set `WORKSTATION_IP` to the IP address of the server machine — the one the client will connect to:

```env
ROS_DISTRO=humble
WORKSTATION_IP=192.168.1.100   # replace with your server's actual IP
```

This value gets injected into the container as `IGN_IP`, which tells the transport layer which network interface to advertise on.

### 2. Start the simulation server

Inside the container, run Gazebo in server-only mode with headless rendering:

```bash
DISPLAY= ign gazebo -v 4 -s -r --headless-rendering sensors_demo.sdf
```

The `-s` flag starts only the physics server — no GUI window opens. The simulation runs and publishes topics, waiting for a client to connect.

To confirm it is running, open a second terminal in the container and check topics:

```bash
ign topic -l
```

You should see the full list of simulation topics. If the list is empty, the server did not start correctly.

---

## Client setup

Make sure you have a working Gazebo Fortress install on the client machine. On macOS, see the [macOS Setup](macos-setup) guide. On Linux, the container itself can serve as the client.

Connect to the server:

```bash
export IGN_PARTITION=ros2_sim
export IGN_IP=<server IP>
ign gazebo -g
```

Replace `<server IP>` with the same IP you set in `WORKSTATION_IP` on the server. The Gazebo GUI window should open and connect to the running simulation.

---

## Verifying the connection

On the **client**, once the GUI is open, check that topics are visible:

```bash
ign topic -l
```

If you see the simulation's topics (same list as on the server), the transport layer has successfully connected. If the list is empty or only shows local topics, the client cannot reach the server — check the IP, firewall rules, and that both sides use the same `IGN_PARTITION` value.

---

## Firewall and network notes

- Both machines must be able to reach each other on the ports Ignition transport uses. If there is a firewall between them, open UDP ports **11345** and the ephemeral range used by ZeroMQ (typically 49152–65535).
- If the server is on a remote network (VPN, cloud), ensure routing allows direct UDP between client and server — Ignition transport does not work through NAT without additional configuration.
