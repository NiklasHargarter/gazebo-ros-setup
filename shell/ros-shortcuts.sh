# gazebo-ros-setup shortcuts — add to ~/.zshrc or ~/.bashrc:
#   export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"
#   source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
#
# Config lives in $ROS_SETUP_DIR/.env (Docker Compose reads it directly):
#   ROS_DISTRO    humble | jazzy | ...
#   COMPOSE_FILE  overlay set — drop docker-compose.nvidia.yml if you have no GPU

: "${ROS_SETUP_DIR:?set ROS_SETUP_DIR to the gazebo-ros-setup repo root before sourcing}"

# All commands are thin wrappers over this. --project-directory makes .env
# (incl. COMPOSE_FILE) resolve from the repo root regardless of $PWD.
dc() { docker compose --project-directory "$ROS_SETUP_DIR" "$@"; }

ros-build()   { dc build "$@"; }                       # rebuild the image
ros-up()      { xhost +local:docker >/dev/null 2>&1; dc up "$@"; }       # start (foreground)
ros-upd()     { xhost +local:docker >/dev/null 2>&1; dc up -d "$@"; }    # start (detached)
ros-down()    { dc down "$@"; }                        # stop and remove
ros-restart() { dc restart "${@:-core}"; }             # restart (default: core)
ros-logs()    { dc logs "${@:--f}"; }                  # tail logs
ros-ps()      { dc ps "$@"; }                          # status

# Shell into a running container: `ros-zsh` for core, `ros-exec SVC [cmd...]`
# for any service. Mostly for debugging — talk to the stack over host ROS.
ros-zsh()  { ros-exec core "$@"; }
ros-exec() {
    local svc="${1:?usage: ros-exec SERVICE [cmd...]}"; shift
    if [ $# -eq 0 ]; then dc exec "$svc" /bin/zsh; else dc exec "$svc" /bin/zsh -ic "$*"; fi
}

# Rebuild the mounted /core_ws and restart core to pick it up.
ros-ws-build() { dc exec core /bin/zsh -ic "cd /core_ws && colcon build" && dc restart core; }

# One-off container as the host user, so files it writes to ./workspace stay
# host-owned. Use for `ros2 pkg create`, ad-hoc colcon, anything that writes.
# USER is forwarded because the host UID has no /etc/passwd entry in the image.
ros-run() {
    local svc=core
    [ "$1" = "-s" ] && { svc="${2:?ros-run: -s requires a service name}"; shift 2; }
    dc run --rm --user "$(id -u):$(id -g)" -e "USER=${USER:-$(id -un)}" "$svc" "$@"
}

ros-root() { cd "$ROS_SETUP_DIR" || return; }
