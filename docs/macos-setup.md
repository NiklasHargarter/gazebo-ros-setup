---
title: macOS Setup
layout: default
nav_order: 2
---

# macOS Setup

On macOS, use a Linux workstation as the simulation server and connect from your Mac as a native GUI client. See the [Remote GUI Client](server-client) guide.

---

## Why the container does not work on macOS

On Linux, Docker containers share the host's GPU and X11 socket directly. On macOS, Docker runs inside a Linux VM with no GPU access and no path to a working display.

**No GPU passthrough.** The VM cannot reach the Mac's GPU. Mesa falls back to its software rasterizer (swrast), but swrast requires DRI kernel interfaces that also do not exist in the VM.

**XQuartz GLX is broken over the Docker network boundary.** XQuartz is macOS's X11 server. Containers reach it over TCP (`DISPLAY=host.docker.internal:0`), but XQuartz's GLX implementation does not advertise the framebuffer configurations that Mesa and Qt require — `X_GLXCreateNewContext` returns `BadValue` (visual ID `0x0`) and Qt aborts.

No Mesa environment variable (`LIBGL_ALWAYS_SOFTWARE`, `LIBGL_ALWAYS_INDIRECT`, etc.) fixes this — the failure is in XQuartz's GLX layer, not in Mesa's driver selection.

---

## Native install via Homebrew

Installing Gazebo Fortress natively uses macOS's own OpenGL stack and works without any workarounds.

### 1. Install Gazebo Fortress

```bash
brew tap osrf/simulation
brew install ignition-fortress
```

Verify the install:

```bash
ign gazebo --version
```

### 2. Run the GUI client

With a simulation server already running on your Linux workstation (see [Remote GUI Client](server-client)):

```bash
export IGN_PARTITION=ros2_sim
export IGN_IP=<workstation IP>
ign gazebo -g
```

The Gazebo window opens on your Mac and connects to the running simulation on the workstation.

To avoid setting the variables each session, add them to your shell profile:

```bash
echo 'export IGN_PARTITION=ros2_sim' >> ~/.zshrc
echo 'export IGN_IP=<workstation IP>' >> ~/.zshrc
```
