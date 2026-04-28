# Example consumer image: subscribes to the TurtleBot 4 camera topic and
# publishes /cmd_vel based on a trivial image-mean rule. Mirrors the shape
# of consumer-template/Dockerfile, but pinned to the TB4 stand-in.
#
# Build from the repo root:
#   docker build -f examples/consumer-camera/Dockerfile \
#                -t consumer-camera:humble \
#                --build-arg ROS_DISTRO=humble \
#                .
#
# Then set CONSUMER_IMAGE=consumer-camera:humble in .env and `docker compose up`.

ARG ROS_DISTRO=humble
FROM project-core:${ROS_DISTRO}

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

# numpy is the only "AI/CV-ish" dep this demo needs. Real consumers add
# torch / opencv / transformers / ... here. Real consumers should also
# pin versions; this demo is intentionally version-agnostic.
RUN apt-get update && apt-get install -y \
        python3-numpy \
    && rm -rf /var/lib/apt/lists/*
