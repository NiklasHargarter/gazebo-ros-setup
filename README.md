# Reproducible ROS 2 + Gazebo dev environment

Two image layers, both built locally.

```
osrf/ros:humble-desktop-full         ← upstream, pulled once
  └── project-core  (core.Dockerfile)
        ← apt deps, zsh shell, entrypoint that auto-sources the workspace
        └── your consumer  (FROM project-core)
              ← your deps, communicates over ROS topics
```

Core runs the robot and simulation. Consumers connect over ROS topics/services/actions via host network.
The `core_ws` is bind-mounted from the host so build artifacts are visible outside the container.

For a paragraph-per-file map of what's in this repo and why, see
[`docs/repo-tour.md`](docs/repo-tour.md).

## Shell shortcuts

The repo ships a set of `ros-*` shortcuts that wrap `docker compose` with the right files and options.
Add these two lines to your `~/.zshrc` (or `~/.bashrc`):

```bash
export ROS_SETUP_DIR="$HOME/gazebo-ros-setup"   # path to this repo
source "$ROS_SETUP_DIR/shell/ros-shortcuts.sh"
```

Then reload your shell (`source ~/.zshrc`). Run `ros-help` to see all available commands.

## Workflows

### Fresh install
```bash
git clone https://github.com/NiklasHargarter/gazebo-ros-setup.git
cd gazebo-ros-setup
bin/setup-core-ws.sh    # clones the three source repos into core_ws/src/
ros-build               # build the core image
ros-upd                 # start the stack
ros-ws-build            # build the workspace inside the container
ros-zsh                 # shell in, then `launch` to run the sim
```

### Daily run
```bash
ros-upd && ros-zsh
launch   # alias for: ros2 launch hugo_moveit_config mobile_manipulation_gazebo.launch.py
```

### After editing core_ws source
```bash
ros-ws-build
```

### Update hugo to a new pinned SHA
After someone bumps the SHA in `bin/setup-core-ws.sh`:
```bash
cd core_ws/src/hugo_moveit_config
git fetch && git checkout <new-sha>
ros-ws-build
```

### Work on hugo locally
```bash
cd core_ws/src/hugo_moveit_config
git checkout my-branch
# edit, then:
ros-ws-build
```

### Rebuild the core image (after apt-dep changes)
```bash
ros-build
```

### Nuke and start over
```bash
ros-down
rm -rf core_ws/build core_ws/install core_ws/log
ros-build --no-cache
ros-upd
ros-ws-build
```

### Run the example consumer
`consumer-template/` is a working starting point:
```bash
ros-upd --profile template
ros-exec consumer-template "cd /workspace && colcon build --symlink-install"
ros-exec consumer-template ros2 run consumer_template echo_camera
```

For the full topic / action contract and how to add your own consumer, see
[`docs/writing-your-own-nodes.md`](docs/writing-your-own-nodes.md).
