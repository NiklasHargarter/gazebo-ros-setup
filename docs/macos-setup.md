---
title: macOS Setup
layout: default
nav_order: 3
---

# macOS Setup

On macOS, use a Linux workstation as the simulation server and connect from your Mac as a native GUI client. See the [Remote GUI Client](server-client) guide.

---

## Native install via Homebrew

Install the Gazebo version matching the distro on your server.

---

### Humble + Fortress

#### 1. Install Gazebo Fortress

```bash
brew tap osrf/simulation
brew install ignition-fortress
```

Verify the install:

```bash
ign gazebo --version
```

#### 2. Run the GUI client

With a simulation server already running on your Linux workstation (see [Remote GUI Client](server-client)):

```bash
export IGN_PARTITION=ros2_sim
export IGN_IP=<workstation IP>
ign gazebo -g
```

To avoid setting the variables each session, add them to your shell profile:

```bash
echo 'export IGN_PARTITION=ros2_sim' >> ~/.zshrc
echo 'export IGN_IP=<workstation IP>' >> ~/.zshrc
```

---

### Jazzy + Harmonic

#### 1. Install Gazebo Harmonic

```bash
brew tap osrf/simulation
brew install gz-harmonic
```

Verify the install:

```bash
gz sim --version
```

#### 2. Run the GUI client

With a simulation server already running on your Linux workstation (see [Remote GUI Client](server-client)):

```bash
export GZ_PARTITION=ros2_sim
export GZ_IP=<workstation IP>
gz sim -g
```

To avoid setting the variables each session, add them to your shell profile:

```bash
echo 'export GZ_PARTITION=ros2_sim' >> ~/.zshrc
echo 'export GZ_IP=<workstation IP>' >> ~/.zshrc
```

---

The Gazebo window opens on your Mac and connects to the running simulation on the workstation.
