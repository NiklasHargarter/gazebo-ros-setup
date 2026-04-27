# Consumer template

Skeleton for a new consumer (e.g. a VLA model, a perception node, a planner)
that runs against the project core stack.

## How a consumer fits in

```
base image (this repo, Dockerfile)         — ROS + zsh, generic
  └── project-core (this repo, core.Dockerfile) — adds core deps. Built locally.
        └── your consumer (this Dockerfile)     — adds your AI/CV deps. Built locally.
```

Source code (core repo, your consumer repo) is bind-mounted at runtime, not
baked into images.

## Setup

1. Copy this directory into your consumer repo, or use it as a starting point
   in place.
2. Edit `Dockerfile` to install your consumer's deps.
3. Build it locally:

   ```bash
   docker build -t my-consumer:humble \
                --build-arg ROS_DISTRO=humble \
                .
   ```

4. From the dev-container repo, set `CONSUMER_IMAGE=my-consumer:humble` in
   `.env`, then `docker compose up`.

## Where your code goes

Your consumer's ROS packages get bind-mounted into `/workspace/src/` inside
the container. Clone your repo into `workspace/src/<your-pkg>/` (or symlink),
then build with `colcon build` inside the container. The build overlays on
top of the core workspace automatically.
