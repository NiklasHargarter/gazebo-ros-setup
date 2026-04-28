---
title: Writing Your Own Nodes
layout: default
nav_order: 4
---

# Writing Your Own Nodes

How to add consumer ROS 2 packages to the container. Covers only the container-specific parts — for ROS 2 concepts (nodes, topics, pub/sub) see the [official tutorials](https://docs.ros.org/en/jazzy/Tutorials.html).

For the full picture of how consumer code relates to the core image, see [Architecture](architecture).

---

## How the workspace works

Consumer packages live in a workspace that is bind-mounted into the consumer container at `/workspace`:

```
/opt/ros/${ROS_DISTRO}   ← ROS base
/opt/ros_overlay         ← core packages (baked into the image)
/workspace/install       ← consumer overlay (sourced automatically if built)
```

```
host: ./workspace/        ←→   consumer container: /workspace/
         src/                          src/         ← your packages
         install/          ←  colcon build writes here
         build/
         log/
```

You edit code on the host with your normal tools; the container builds and runs it.

---

## 1. Create a package

Open a shell in your consumer container:

```bash
docker compose exec consumer-example zsh
```

Use the ROS 2 scaffolder:

```bash
cd /workspace/src
ros2 pkg create --build-type ament_python my_package --node-name my_node
```

For C++ packages use `--build-type ament_cmake`; everything else below is identical.

---

## 2. Build

From `/workspace` in the container:

```bash
cd /workspace
colcon build --symlink-install
```

`--symlink-install` symlinks Python sources into `install/` so edits on your host take effect without rebuilding. You still need to rebuild if you add new entry points or change `setup.py`.

---

## 3. Run

```bash
ros2 run my_package my_node
```

Expected output: `Hi from my_package.`

---

## 4. Edit and iterate

Edit `./workspace/src/my_package/my_package/my_node.py` on your host. For a minimal publisher:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.pub = self.create_publisher(String, '/my_topic', 10)
        self.create_timer(1.0, self.tick)

    def tick(self):
        msg = String()
        msg.data = 'hello'
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(MyNode())
    rclpy.shutdown()
```

Because of `--symlink-install` you don't need to rebuild. Just re-run:

```bash
ros2 run my_package my_node
```

Verify from a second consumer shell or from core:

```bash
docker compose exec core bash
ros2 topic echo /my_topic
```

---

## Package structure reference

```
workspace/src/my_package/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── my_package            # empty marker — ros2 run finds packages via this
└── my_package/
    ├── __init__.py
    └── my_node.py
```

You rarely need to touch any of these by hand — `ros2 pkg create` and `colcon build` manage them.
