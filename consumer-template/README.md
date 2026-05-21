# consumer-template

Working example consumer. The Dockerfile (`FROM project-core`) sets up a zsh
dev shell; the ROS package itself lives at `workspace/src/consumer_template/`
and ships two example nodes (`echo_camera`, `drive_square`).

```bash
ros-upd --profile template
ros-exec consumer-template "cd /workspace && colcon build --symlink-install"
ros-exec consumer-template ros2 run consumer_template echo_camera
ros-exec consumer-template "ros2 run consumer_template drive_square --ros-args -p start:=true"
```

For the full topic / action surface, QoS conventions, and how to scaffold a new
consumer package, see [`docs/writing-your-own-nodes.md`](../docs/writing-your-own-nodes.md).
