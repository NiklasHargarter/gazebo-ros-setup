#!/usr/bin/env bash
# Clone the three source repos into core_ws/src/. The hugo_moveit_config SHA
# below is the integration pin — bump it here when a new hugo version is
# ready for everyone else.

set -e
cd "$(dirname "$0")/../core_ws/src"

git clone --branch 0.0.3 https://github.com/ROBOTIS-GIT/robotis_hand.git
git clone https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git
git clone https://gitlab.sdu.dk/hugo/hugo_moveit_config.git
git -C hugo_moveit_config checkout 3eb7c8d5c756bfa08947a4466f68e6737e1d368d
