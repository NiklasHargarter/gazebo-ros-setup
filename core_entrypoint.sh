#!/bin/bash
source /opt/ros/${ROS_DISTRO}/setup.bash
[ -f /core_ws/install/setup.bash ] && source /core_ws/install/setup.bash
exec "$@"
