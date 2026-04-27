# Stand-in for the project-core image, populated with the TurtleBot 4 stack
# instead of the real (private) core deps. Same role as core.Dockerfile at
# the repo root: produces an image tagged project-core:${ROS_DISTRO} that
# consumer images then FROM.
#
# Jazzy only — TB4 package names and Gazebo version differ on Humble.
ARG ROS_DISTRO=jazzy
ARG BASE_IMAGE=ghcr.io/niklashargarter/gazebo-ros-setup:${ROS_DISTRO}
FROM ${BASE_IMAGE}

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
