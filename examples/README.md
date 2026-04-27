# Examples

End-to-end demos of the [project architecture](../docs/architecture.md):
the **TurtleBot 4** example acts as a stand-in for the (private) core
image, and **consumer-camera** is an example consumer that runs on top
of it. Together they exercise the full base / core / consumer flow
without needing GitLab access.

| Example | Role | Path |
|---|---|---|
| [TurtleBot 4 (Jazzy)](turtlebot4/) | **Core stand-in.** Builds `project-core:jazzy` from the TB4 simulator stack, in place of the real private core. | `examples/turtlebot4/` |
| [Consumer — camera brightness driver](consumer-camera/) | **Example consumer.** `FROM project-core:jazzy` + a tiny ROS Python node that turns camera frames into `/cmd_vel`. | `examples/consumer-camera/` |
| [Camera World](camera_world/) | Standalone tutorial on writing a custom SDF world and a Python subscriber against the bare base image. Predates the core/consumer split. | `examples/camera_world/` |

The first two are the path to follow if you want to see the real
deployment shape. Camera World is kept around as a smaller, self-contained
intro to ROS+Gazebo wiring. All three assume `ROS_DISTRO=jazzy`.
