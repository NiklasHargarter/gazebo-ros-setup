FROM osrf/ros:kilted-desktop-full

# Install zsh
RUN apt-get update && apt-get install -y zsh && rm -rf /var/lib/apt/lists/*

# Inject your standard config file
COPY container_zshrc /root/.zshrc

WORKDIR /workspace
