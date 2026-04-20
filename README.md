# Contains details for easily replicatable gazebo-ros2 setup (Humble, Jazzy, etc.).
[link to docs](https://niklashargarter.github.io/gazebo-ros-setup/)

## Quick usage

Base (CPU/Intel, local-only):
```bash
docker compose up
```

With NVIDIA GPU:
```bash
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up
```

Server-client networking (remote GUI, see `docs/server-client.md`):
```bash
docker compose -f docker-compose.yml -f docker-compose.server.yml up
```

Stack `-f` files for any combination (e.g. NVIDIA + server).

## Examples

Two ready-to-run setups live under [`examples/`](examples/):

- [TurtleBot 4 (Jazzy)](examples/turtlebot4/) — full TB4 simulator stack on top of the base image.
- [Camera World](examples/camera_world/) — minimal custom SDF world with a camera sensor and a Python subscriber node.
