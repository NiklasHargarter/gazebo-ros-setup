ARG ROS_DISTRO=humble
FROM osrf/ros:${ROS_DISTRO}-desktop-full

# Redeclare ARG to use it after FROM
ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

# Install zsh
RUN apt-get update && apt-get install -y zsh && rm -rf /var/lib/apt/lists/*

# Inject your standard config file
COPY container_zshrc /root/.zshrc

WORKDIR /workspace
