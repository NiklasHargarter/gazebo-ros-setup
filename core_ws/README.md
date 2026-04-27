# Core workspace

This folder is mounted into the container at `/core_ws` and holds the
project's **shared core stack** — the robot description, ROS nodes, and
Gazebo sim layer maintained in the private GitLab core repo.

It is intentionally empty in this repo. Each machine clones the core repo
into `core_ws/src/core` (gitignored) and builds it once inside the container.

See [`docs/architecture.md`](../docs/architecture.md) for the full picture
of how this fits with the base image, `core.Dockerfile`, and consumer
images.

## One-time setup

From the repo root:

```bash
# 1. Clone the core source (private GitLab — guest access required)
git clone <CORE_REPO_GITLAB_URL> core_ws/src/core

# 2. Build the project-core image locally (bakes in core deps)
docker build -f core.Dockerfile \
             -t project-core:${ROS_DISTRO:-humble} \
             --build-arg ROS_DISTRO=${ROS_DISTRO:-humble} .

# 3. Build a consumer image that FROMs project-core
#    (see consumer-template/)

# 4. Run
docker compose up -d
docker compose exec ros-gazebo zsh

# inside the container, one-time colcon build:
cd /core_ws
rosdep update
rosdep install --from-paths src --ignore-src -y
colcon build --merge-install
```

After that, new shells auto-source `/core_ws/install/setup.zsh`, and
`/workspace` (consumer packages) overlays on top.
