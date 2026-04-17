# 1. Global Scope: Define the default once
ARG ROS_DISTRO=humble

FROM osrf/ros:${ROS_DISTRO}-desktop-full

# 2. Stage Scope: "Unlock" the global ARG by redeclaring it without a value
ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}

RUN apt-get update && apt-get install -y \
        zsh git curl fzf \
    && rm -rf /var/lib/apt/lists/*

# Oh My Zsh + Powerlevel10k + plugins (all shallow clones to keep image small)
ENV ZSH=/root/.oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
 && git clone --depth=1 https://github.com/romkatv/powerlevel10k.git           ${ZSH}/custom/themes/powerlevel10k \
 && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git   ${ZSH}/custom/plugins/zsh-autosuggestions \
 && git clone --depth=1 https://github.com/zsh-users/zsh-completions.git       ${ZSH}/custom/plugins/zsh-completions \
 && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH}/custom/plugins/zsh-syntax-highlighting \
 && git clone --depth=1 https://github.com/Aloxaf/fzf-tab.git                  ${ZSH}/custom/plugins/fzf-tab

COPY container_zshrc   /root/.zshrc
COPY container_p10k.zsh /root/.p10k.zsh

WORKDIR /workspace
