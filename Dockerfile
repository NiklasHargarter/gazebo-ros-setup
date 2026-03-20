# 1. Global Scope: Define the default once
ARG ROS_DISTRO=humble

FROM osrf/ros:${ROS_DISTRO}-desktop-full

# 2. Stage Scope: "Unlock" the global ARG by redeclaring it without a value
ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

RUN apt-get update && apt-get install -y zsh && \
    rm -rf /var/lib/apt/lists/*

COPY container_zshrc /root/.zshrc
WORKDIR /workspace
