# gazebo-ros-setup shortcuts — add to ~/.zshrc or ~/.bashrc:
#   export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"
#   source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
#
# All state lives in $ROS_SETUP_DIR/.env (the same file Docker Compose reads):
#   ROS_DISTRO   humble | jazzy | ...                       (default: humble)
#   ROS_PROFILE  base | nvidia | server | nvidia-server     (default: base)
#
# Change values with `ros-distro NAME` / `ros-profile NAME`. Run `ros-help` for
# the full command list.

: "${ROS_SETUP_DIR:?set ROS_SETUP_DIR to the gazebo-ros-setup repo root before sourcing}"

_ros_env_file="$ROS_SETUP_DIR/.env"
_ros_service="ros-gazebo"

# Read KEY from .env, or fall back to DEFAULT.
_ros_get() {
    local key="$1" default="$2" val=""
    if [ -f "$_ros_env_file" ]; then
        val="$(awk -F= -v k="$key" '$1 == k { sub(/^[^=]*=/, ""); print; exit }' "$_ros_env_file")"
    fi
    printf '%s' "${val:-$default}"
}

# Upsert KEY=VALUE in .env, preserving every other line.
_ros_set() {
    local key="$1" val="$2"
    touch "$_ros_env_file"
    local tmp; tmp="$(mktemp)"
    awk -v k="$key" -v v="$val" '
        BEGIN { FS = OFS = "="; found = 0 }
        $1 == k { print k "=" v; found = 1; next }
        { print }
        END { if (!found) print k "=" v }
    ' "$_ros_env_file" > "$tmp" && mv "$tmp" "$_ros_env_file"
}

_ros_compose_files() {
    local profile files=("-f" "$ROS_SETUP_DIR/docker-compose.yml")
    profile="$(_ros_get ROS_PROFILE base)"
    case "$profile" in
        base) ;;
        nvidia)
            files+=("-f" "$ROS_SETUP_DIR/docker-compose.nvidia.yml") ;;
        server)
            files+=("-f" "$ROS_SETUP_DIR/docker-compose.server.yml") ;;
        nvidia-server|server-nvidia)
            files+=("-f" "$ROS_SETUP_DIR/docker-compose.nvidia.yml")
            files+=("-f" "$ROS_SETUP_DIR/docker-compose.server.yml") ;;
        *)
            echo "ros-shortcuts: unknown ROS_PROFILE '$profile' in $_ros_env_file" >&2
            echo "               expected: base | nvidia | server | nvidia-server" >&2
            return 1 ;;
    esac
    printf '%s\n' "${files[@]}"
}

_ros_compose() {
    local files
    files=($(_ros_compose_files)) || return 1
    docker compose --project-directory "$ROS_SETUP_DIR" "${files[@]}" "$@"
}

ros-help() {
    cat <<EOF
gazebo-ros-setup shortcuts  (ROS_DISTRO=$(_ros_get ROS_DISTRO humble)  ROS_PROFILE=$(_ros_get ROS_PROFILE base))
  ros-zsh [cmd...]   Exec zsh (or a command) inside the running container
  ros-up             Start stack in foreground
  ros-upd            Start stack detached
  ros-down           Stop and remove stack
  ros-restart        Restart the service
  ros-logs [args]    Tail logs (default: -f)
  ros-ps             Show compose status
  ros-build          Rebuild the image
  ros-run [cmd...]   One-off container via 'compose run --rm'
  ros-compose ...    Raw 'docker compose' with current profile/distro
  ros-root           cd into the gazebo-ros-setup repo
  ros-profile NAME   Set profile (base|nvidia|server|nvidia-server) in .env
  ros-distro NAME    Set ROS_DISTRO (humble|jazzy|...) in .env
  ros-help           Show this help
EOF
}

ros-compose()  { _ros_compose "$@"; }
ros-up()       { _ros_compose up "$@"; }
ros-upd()      { _ros_compose up -d "$@"; }
ros-down()     { _ros_compose down "$@"; }
ros-restart()  { _ros_compose restart "${@:-$_ros_service}"; }
ros-logs()     { _ros_compose logs "${@:--f}"; }
ros-ps()       { _ros_compose ps "$@"; }
ros-build()    { _ros_compose build "$@"; }
ros-run()      { _ros_compose run --rm "$_ros_service" "$@"; }

ros-zsh() {
    if [ $# -eq 0 ]; then
        _ros_compose exec "$_ros_service" /bin/zsh
    else
        # -i so the container's .zshrc runs and ROS / workspace overlay are on PATH.
        _ros_compose exec "$_ros_service" /bin/zsh -ic "$*"
    fi
}

ros-root() { cd "$ROS_SETUP_DIR" || return; }

ros-profile() {
    if [ $# -ne 1 ]; then
        echo "current: ROS_PROFILE=$(_ros_get ROS_PROFILE base)"
        echo "usage: ros-profile <base|nvidia|server|nvidia-server>"
        return 1
    fi
    _ros_set ROS_PROFILE "$1"
    echo "ROS_PROFILE=$1  (saved to $_ros_env_file)"
}

ros-distro() {
    if [ $# -ne 1 ]; then
        echo "current: ROS_DISTRO=$(_ros_get ROS_DISTRO humble)"
        echo "usage: ros-distro <humble|jazzy|...>"
        return 1
    fi
    _ros_set ROS_DISTRO "$1"
    echo "ROS_DISTRO=$1  (saved to $_ros_env_file)"
}
