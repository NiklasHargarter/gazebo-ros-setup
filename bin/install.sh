#!/usr/bin/env bash
# Wire the ros-* shortcuts into your shell, then optionally clone the core
# source. Does nothing you can't do by hand — it prints the exact lines it
# would add and asks before touching any file. Manual path: copy the two
# `export`/`source` lines below into your rc file yourself.
#
# Usage:
#   bin/install.sh            # interactive: confirm before editing rc, offer clone
#   bin/install.sh --print    # just print the lines to add, edit nothing

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GUARD="# gazebo-ros-setup shortcuts"
BLOCK="$GUARD
export ROS_SETUP_DIR=\"$REPO_DIR\"
source \"\$ROS_SETUP_DIR/shell/ros-shortcuts.sh\""

if [ "$1" = "--print" ]; then
    printf '%s\n' "$BLOCK"
    exit 0
fi

# Pick the rc file from the user's login shell, overridable via $RC_FILE.
case "${RC_FILE:-${SHELL##*/}}" in
    *zsh*|zsh) rc="${RC_FILE:-$HOME/.zshrc}" ;;
    *bash*|bash) rc="${RC_FILE:-$HOME/.bashrc}" ;;
    *) rc="${RC_FILE:-$HOME/.profile}" ;;
esac

echo "Repo:    $REPO_DIR"
echo "RC file: $rc"
echo

if [ -f "$rc" ] && grep -qF "$GUARD" "$rc"; then
    echo "Shortcuts already wired into $rc — skipping."
else
    echo "These lines will be appended to $rc:"
    echo "---"
    printf '%s\n' "$BLOCK"
    echo "---"
    printf 'Append them? [y/N] '
    read -r reply
    case "$reply" in
        [yY]*)
            printf '\n%s\n' "$BLOCK" >> "$rc"
            echo "Done. Run 'source $rc' (or open a new shell) to load the shortcuts."
            ;;
        *)
            echo "Skipped. Add the lines above to $rc yourself, or re-run later."
            ;;
    esac
fi

echo
if [ -f "$REPO_DIR/.env" ]; then
    echo ".env already exists — skipping config."
else
    cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
    printf 'Do you have an NVIDIA GPU + container toolkit? [y/N] '
    read -r reply
    case "$reply" in
        [yY]*) echo "Keeping the NVIDIA overlay in .env." ;;
        *)
            sed -i 's/^COMPOSE_FILE=.*/COMPOSE_FILE=docker-compose.yml/' "$REPO_DIR/.env"
            echo "Dropped the NVIDIA overlay — base stack only." ;;
    esac
fi

echo
if [ -d "$REPO_DIR/core_ws/src" ] && [ -n "$(ls -A "$REPO_DIR/core_ws/src" 2>/dev/null | grep -v '^\.gitkeep$')" ]; then
    echo "core_ws/src already populated — skipping core-source clone."
else
    printf 'Clone the core source now (runs bin/setup-core-ws.sh)? [y/N] '
    read -r reply
    case "$reply" in
        [yY]*) "$REPO_DIR/bin/setup-core-ws.sh" ;;
        *) echo "Skipped. Run bin/setup-core-ws.sh when ready." ;;
    esac
fi

# Replace this script's process with a fresh login shell so the ros-* shortcuts
# are loaded — a child script can't source into the parent interactive shell,
# but exec-ing a new login shell reads the rc we just edited. Exit it to return
# to your original shell. Skipped when stdin isn't a terminal (CI, pipes).
echo
if [ -t 0 ]; then
    echo "Starting a fresh shell so the ros-* shortcuts are loaded (exit to go back)."
    exec "$SHELL" -l
else
    echo "Open a new shell (or 'source $rc') to load the ros-* shortcuts."
fi
