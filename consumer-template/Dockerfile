ARG ROS_DISTRO=humble
FROM project-core:${ROS_DISTRO}

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

# Add consumer-specific deps here. Examples:
#
#   RUN apt-get update && apt-get install -y \
#           python3-pip \
#       && rm -rf /var/lib/apt/lists/*
#
#   RUN pip install --no-cache-dir \
#           torch torchvision \
#           opencv-python \
#           transformers
#
# For CUDA, use a CUDA-enabled base by overriding BASE_IMAGE when
# building project-core, then add only the Python/runtime layers here.
