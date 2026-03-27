---
title: Headless Rendering
layout: default
nav_order: 2
---

# Headless Rendering

Headless mode runs Gazebo on a machine with no display — a remote server, a CI box, or any host where you don't want or have a screen. Instead of X11, it uses **EGL**, a rendering interface that talks directly to the GPU without needing a display server.

{: .important }
Headless rendering requires OGRE2 as the render engine in your SDF world. The standard `sensors_demo.sdf` uses OGRE2 and works out of the box.

---

## Running headless

Unsetting `$DISPLAY` tells Gazebo to skip X11 and fall back to EGL. The `--headless-rendering` flag explicitly enables the EGL path:

**Humble (Fortress):**
```bash
DISPLAY= ign gazebo -v 4 -s -r --headless-rendering sensors_demo.sdf
```

**Jazzy (Harmonic):**
```bash
DISPLAY= gz sim -v 4 -s -r --headless-rendering sensors_demo.sdf
```

Flag reference:

| Flag | Meaning |
|---|---|
| `DISPLAY=` | Unsets the display variable for this command only, forcing EGL |
| `-v 4` | Verbosity level 4 — useful for confirming EGL is initialised |
| `-s` | Server only — no GUI process |
| `-r` | Start running immediately |
| `--headless-rendering` | Activates EGL-based GPU rendering without a display |

---

## Verifying sensor output remotely

Once the simulation is running headless on the server, open a second shell (e.g. SSH into the machine) and confirm topics are publishing:

**Humble (Fortress):**
```bash
# List all active topics
ign topic -l

# Check that a publisher is active on a topic
ign topic -i --topic /thermal_camera

# Stream messages (Ctrl-C to stop)
ign topic -e --topic /thermal_camera
```

**Jazzy (Harmonic):**
```bash
gz topic -f -t /thermal_camera
```

{: .note }
Fortress's `ign topic` has no frequency flag. Use `-e` to confirm data is flowing and `-i` to confirm a publisher exists.

---

## Separate server and GUI client

Running the physics server on one machine and the Gazebo GUI on another is documented separately — coming soon.
