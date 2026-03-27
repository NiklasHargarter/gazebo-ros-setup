---
title: macOS Setup
layout: default
nav_order: 2
---

# macOS Setup

This page covers running the Gazebo UI on a Mac using Docker. The goal is the same as the Linux getting-started guide — open Gazebo and see the simulation window — but macOS needs two extra pieces: **Docker Desktop** instead of the Linux Docker engine, and **XQuartz** to display GUI windows from inside the container.

{: .note }
NVIDIA GPU passthrough is not supported on macOS Docker. Gazebo will run using software rendering (CPU/Mesa), which is fine for viewing and interacting with a simulation but not for headless GPU-accelerated sensor rendering.

---

## 1. Install Docker Desktop

[Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) and install it. Open it and wait for the engine to start — the whale icon in the menu bar stops animating when it's ready.

Verify it works:
```bash
docker run hello-world
```

---

## 2. Install and configure XQuartz

On macOS there is no built-in X11 server. XQuartz provides one. Without it, there is no way to display GUI windows from a Docker container on your screen.

```bash
brew install --cask xquartz
```

Docker on macOS runs inside a Linux VM, so it cannot reach XQuartz through a Unix socket the way Linux does. You must enable TCP connections:

1. Open **XQuartz**
2. Go to **XQuartz → Preferences → Security**
3. Enable **"Allow connections from network clients"**
4. **Quit and relaunch XQuartz** — the setting only applies after a full restart

Verify XQuartz is now listening on TCP:
```bash
lsof -i :6000
```
You should see an `X11` entry. If nothing appears, XQuartz is not running or the setting was not saved.

---

## 3. Grant Docker access to XQuartz

Run this in a Mac terminal before starting the container. You need to repeat it each time XQuartz restarts:

```bash
xhost +localhost
```

---

## 4. Clone the repo and prepare files

```bash
git clone <repo-url>
cd gazebo-ros-setup
mkdir -p workspace/src
touch .zsh_history
echo "ROS_DISTRO=humble" > .env
```

---

## 5. Remove the GPU devices line

The default `docker-compose.yml` requests an NVIDIA GPU, which does not exist on macOS. Open `docker-compose.yml` and remove or comment out the `devices` block:

```yaml
# Remove these two lines:
    devices:
      - nvidia.com/gpu=all
```

---

## 6. Set the display variable

On Linux the `DISPLAY` variable is set automatically by the OS. On macOS you need to set it to point at XQuartz. Add it to your `.env` file:

```bash
echo "DISPLAY=host.docker.internal:0" >> .env
```

`host.docker.internal` is a DNS name Docker provides inside containers that always resolves to your Mac. `:0` is XQuartz's display number.

---

## 7. Build and start the container

```bash
docker compose up -d --build
```

---

## 8. Open a terminal inside the container

```bash
docker compose exec ros-gazebo zsh
```

---

## 9. Launch Gazebo

### Empty world — confirm the GUI opens

```bash
ign gazebo
```

A Gazebo window should open on your Mac desktop showing an empty world with a grid floor. This confirms Docker, XQuartz, and display forwarding are all working correctly.

### Sensor demo world — confirm simulation produces data

```bash
ign gazebo sensors_demo.sdf
```

The window opens with a world containing sensors. Open a second terminal in the container to verify topics are publishing:

```bash
ign topic -l
ign topic -e --topic /thermal_camera
```

If you see a stream of data, **the setup is complete.**

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `docker compose up` fails with device error | `devices` block still in docker-compose.yml | Remove the `nvidia.com/gpu=all` lines |
| Gazebo opens but no window appears on screen | XQuartz not running or not configured | Check `lsof -i :6000`; re-enable network clients in XQuartz preferences |
| `cannot connect to X server` error | `xhost +localhost` not run | Run `xhost +localhost` in a Mac terminal, then retry |
| Window appears but is blank or crashes | Software rendering fallback not working | Try `export LIBGL_ALWAYS_SOFTWARE=1` inside the container before launching Gazebo |
