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

# Opinionated zsh dev shell. Strip this block for minimal / headless consumers
# (and switch the compose command to /bin/bash).
RUN apt-get update && apt-get install -y zsh git curl fzf \
    && rm -rf /var/lib/apt/lists/*

ENV ZSH=/root/.oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
 && git clone --depth=1 https://github.com/romkatv/powerlevel10k.git           ${ZSH}/custom/themes/powerlevel10k \
 && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git   ${ZSH}/custom/plugins/zsh-autosuggestions \
 && git clone --depth=1 https://github.com/zsh-users/zsh-completions.git       ${ZSH}/custom/plugins/zsh-completions \
 && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH}/custom/plugins/zsh-syntax-highlighting \
 && git clone --depth=1 https://github.com/Aloxaf/fzf-tab.git                  ${ZSH}/custom/plugins/fzf-tab \
 && ${ZSH}/custom/themes/powerlevel10k/gitstatus/install -f

COPY container_zshrc    /root/.zshrc
COPY container_p10k.zsh /root/.p10k.zsh
