# Consumer template

Skeleton for a consumer service that runs against `project-core`.

```
osrf/ros:${ROS_DISTRO}-desktop-full
  └── project-core      (this repo, core.Dockerfile)
        └── your consumer  (this Dockerfile, FROM project-core)
```

## Setup

1. Copy this directory into your consumer repo (or edit in place).
2. Edit `Dockerfile` to add your apt / pip deps. The opinionated zsh block
   is enabled by default — strip it for minimal/headless consumers and
   switch the compose `command:` to `/bin/bash`.
3. Build:

   ```bash
   docker build -t my-consumer:humble \
                --build-arg ROS_DISTRO=humble .
   ```

4. Add a service block in `docker-compose.yml` (copy `consumer-example`),
   point it at your image, give it a unique `profiles:` name, then:

   ```bash
   docker compose --profile <name> up -d
   ```

## Source layout

Consumer packages live in `./workspace/src/<your-pkg>/` (host) and are
bind-mounted to `/workspace/src/` (container). See
[Writing your own nodes](../docs/writing-your-own-nodes.md).
