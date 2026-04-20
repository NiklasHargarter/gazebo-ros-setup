# Examples

Two self-contained setups that build on the base image.

| Example | What it shows | Path |
|---|---|---|
| [TurtleBot 4 (Jazzy)](turtlebot4/) | Off-the-shelf robot: installs the TurtleBot 4 simulation stack on top of the base image and launches the full bringup + Gazebo. | `examples/turtlebot4/` |
| [Camera World](camera_world/) | Minimal custom setup: a hand-written SDF world with a camera sensor, bridged into ROS 2, consumed by a Python node. | `examples/camera_world/` |

Each example is independent — pick whichever matches what you want to learn. Both assume `ROS_DISTRO=jazzy` in the repo's `.env`.
