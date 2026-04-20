# Extends the base image with the TurtleBot 4 simulation stack.
# Only targets Jazzy — the TB4 package names and Gazebo version differ on Humble.
ARG ROS_DISTRO=jazzy
FROM ghcr.io/niklashargarter/gazebo-ros-setup:${ROS_DISTRO}

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

RUN apt-get update && apt-get install -y \
        ros-${ROS_DISTRO}-turtlebot4-desktop \
        ros-${ROS_DISTRO}-turtlebot4-simulator \
        ros-${ROS_DISTRO}-turtlebot4-navigation \
        ros-${ROS_DISTRO}-irobot-create-nodes \
        ros-${ROS_DISTRO}-slam-toolbox \
        ros-${ROS_DISTRO}-nav2-bringup \
    && rm -rf /var/lib/apt/lists/*
