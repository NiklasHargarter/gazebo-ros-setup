---
title: Repo Tour
layout: default
nav_order: 5
---

# Repo tour

One paragraph per top-level file or directory: what it does, when you touch it.

## Build & runtime

**`core.Dockerfile`** — builds `project-core:${ROS_DISTRO}` on top of `osrf/ros:${ROS_DISTRO}-desktop-full`. Installs apt deps (MoveIt, Nav2, ros2-control, gz-ros2-control, dynamixel SDK, zsh tooling) and wires the entrypoint. Rebuild with `ros-build` only when apt deps change.

**`core_entrypoint.sh`** — runs on every container start. Sources `/opt/ros/${ROS_DISTRO}/setup.bash` and, if it exists, `/core_ws/install/setup.bash`. The `exec "$@"` at the end hands control to whatever command the container was started with (zsh by default).

**`core_zshrc`** — interactive shell setup inside the `core` container: sources the same ROS overlays for zsh, sets persistent history into the bind-mounted `.zsh_history_dir/`, and defines the `launch` alias for `mobile_manipulation_gazebo.launch.py`.

**`docker-compose.yml`** — base stack. Defines `core` (the robot + sim container), `consumer-template` (one example consumer, profile `template`), and `postgres` (optional shared infra, profile `postgres`). Bind-mounts `core_ws/`, `workspace/`, X11 socket, history dir; ROS services use `network_mode: host` and `ipc: host` so DDS discovery and FastDDS shared-memory transport work across containers. `postgres` listens on host port 5432; any container can connect via `localhost`.

**`docker-compose.nvidia.yml`** — overlay that adds `devices: nvidia.com/gpu=all` to `core` and `consumer-template`. Layered on top of the base file via `COMPOSE_FILE` (raw `docker compose`) or `ros-profile nvidia` (shortcuts).

## Source workspaces

**`core_ws/`** — host directory bind-mounted into the `core` container at `/core_ws`. You clone the robot + sim sources here (`hugo_moveit_config`, `robotis_hand`, `turtlebot3_manipulation`). `core_ws/src/*` is gitignored — every machine clones its own copy. `colcon build` runs *inside* the container and writes back to host `core_ws/build/`, `core_ws/install/`.

**`workspace/`** — host directory bind-mounted into consumer containers at `/workspace`. Holds consumer ROS 2 packages. `workspace/src/consumer_template/` ships with the repo as a working example; other packages are gitignored.

**`consumer-template/`** — the consumer-side Dockerfile (`FROM project-core`) plus the zsh dev-shell layer (oh-my-zsh, p10k, plugins). Inherits the entrypoint from `project-core`. Copy this directory as the starting point for a new consumer; the ROS package source lives separately under `workspace/src/consumer_template/`.

## UX layer

**`shell/ros-shortcuts.sh`** — the `ros-*` commands (`ros-upd`, `ros-zsh`, `ros-exec`, `ros-build`, …) that wrap `docker compose` with the right `-f` flags based on `ROS_PROFILE` in `.env`. The single source of UX. Source it from your `~/.zshrc` / `~/.bashrc`. Run `ros-help` for the full list.

**`.env` / `.env.example`** — `ROS_DISTRO` (default `humble`), `COMPOSE_FILE` (overlay set for raw `docker compose`), and optional `ROS_PROFILE` (for the shortcuts). Compose reads `.env` automatically; the shortcuts read it via `_ros_get` / `_ros_set`.

**`.zsh_history_dir/`** — bind-mounted into containers so zsh history persists across container restarts. Empty marker dir; the file itself (`.zsh_history`) is gitignored.

**`ignition_pictures/`** — bind-mounted at `/root/.ignition/gui/pictures` so screenshots taken from the Gazebo GUI end up on the host. Gitignored.

## Docs and process

**`README.md`** — top-level entry. Quick "clone, build, launch" recipe. Defers detail to `docs/`.

**`docs/`** — Jekyll site published to GitHub Pages via `.github/workflows/pages.yml`. Each `.md` has a `nav_order` frontmatter that orders it in the sidebar. The canonical home for everything beyond the README.

**`tickets/`** — local work plans (gitignored). Each `sNN-*.md` is a self-contained session brief. Not shipped to users.

## Conventions you might wonder about

- **Why two workspaces?** Core (`core_ws`) is the robot + sim, rebuilt rarely. Consumers (`workspace`) iterate constantly. Splitting them means a consumer rebuild doesn't recompile MoveIt + Nav2, and the consumer image stays small.

- **Why bind-mount `core_ws` instead of baking source into the image?** Build artefacts stay visible on the host; rebuilds don't require an image rebuild; the source repo (`hugo_moveit_config`) is private to each machine and never lands in a published image.

- **Why `network_mode: host` and `ipc: host`?** Host network so DDS discovery just works between containers. Host IPC so FastDDS's shared-memory transport (which uses `/dev/shm`) actually carries data between containers — without it, discovery succeeds but no payload flows.

- **Why a `project-core` layer at all?** So consumer images inherit the apt deps (MoveIt, Nav2, ros2-control) without each consumer Dockerfile re-listing them. The image is built locally on every machine; nothing is published.
