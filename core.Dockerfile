ARG ROS_DISTRO=humble
FROM osrf/ros:${ROS_DISTRO}-desktop-full

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

RUN apt-get update && apt-get install -y \
        xterm \
        ros-${ROS_DISTRO}-moveit \
        ros-${ROS_DISTRO}-dynamixel-sdk \
        ros-${ROS_DISTRO}-nav2-bringup \
        ros-${ROS_DISTRO}-navigation2 \
        ros-${ROS_DISTRO}-hardware-interface \
        ros-${ROS_DISTRO}-ros2-control \
        ros-${ROS_DISTRO}-ros2-controllers \
        ros-${ROS_DISTRO}-joint-state-publisher \
        ros-${ROS_DISTRO}-joint-state-publisher-gui \
        ros-${ROS_DISTRO}-ign-ros2-control \
    && rm -rf /var/lib/apt/lists/*

# Core source is built into the image so consumers inherit all packages via
# FROM project-core without needing access to the private source repo.
# Before building: git clone <core-repo> core_ws/src/core
COPY core_ws/src /tmp/core_build/src
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && mkdir -p /opt/ros_overlay \
    && if find /tmp/core_build/src -name "package.xml" | grep -q .; then \
           rosdep update \
           && rosdep install --from-paths /tmp/core_build/src --ignore-src -y \
           && cd /tmp/core_build \
           && colcon build --merge-install --install-base /opt/ros_overlay; \
       fi \
    && rm -rf /tmp/core_build

ENV AMENT_PREFIX_PATH=/opt/ros_overlay

WORKDIR /root
