ARG ROS_DISTRO=humble
FROM project-core:${ROS_DISTRO}

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

RUN apt-get update && apt-get install -y \
        ros-${ROS_DISTRO}-vision-msgs \
        ros-${ROS_DISTRO}-cv-bridge \
        python3-pip \
        python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# numpy<2 pin: apt's matplotlib (and other ROS python deps) compiled
# against numpy 1.x; without the pin, pip pulls numpy 2.x as a torch
# transitive and matplotlib imports break.
RUN pip install --no-cache-dir \
        'numpy<2' \
        torch torchvision \
        ultralytics \
        ftfy regex tqdm \
        git+https://github.com/openai/CLIP.git

# Pre-bake YOLO-World weights so the detector starts fast. The 'x' model
# has the capacity to score flat sim primitives (and real objects) far
# better than 's' on open-vocab prompts; a 4090 runs it well above 10 Hz.
ENV YOLO_MODEL_PATH=/opt/yolo/yolov8x-world.pt
RUN mkdir -p /opt/yolo && \
    python3 -c "from ultralytics import YOLO; YOLO('yolov8x-world.pt')" && \
    mv yolov8x-world.pt /opt/yolo/yolov8x-world.pt
