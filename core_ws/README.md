# Core workspace

This folder is mounted into the container at `/core_ws` and holds the
project's **shared core stack** — the robot description, ROS nodes, and
Gazebo sim layer maintained in the private GitLab core repo.

It is intentionally empty in this repo. Each machine clones the core repos
into `core_ws/src/` (gitignored) and the image is built once.

See [`docs/architecture.md`](../docs/architecture.md) for the full picture
of how this fits with `core.Dockerfile` and consumer images.

## One-time setup

From the repo root:

```bash
# 1. Clone the core source repos
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git core_ws/src/hugo_moveit_config
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git core_ws/src/turtlebot3_manipulation
git clone https://github.com/ROBOTIS-GIT/robotis_hand.git core_ws/src/robotis_hand
cd core_ws/src/turtlebot3_manipulation && git checkout humble && cd -

# 2. Build the project-core image (bakes in source + deps)
docker build -f core.Dockerfile \
             -t project-core:humble \
             --build-arg ROS_DISTRO=humble .

# 3. Build a consumer image that FROMs project-core
#    (see consumer-template/)

# 4. Run
docker compose up -d
docker compose exec core bash
```
