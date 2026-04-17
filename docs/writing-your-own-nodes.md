---
title: Writing Your Own Nodes
layout: default
nav_order: 4
---

# Writing Your Own Nodes

How to add your own ROS 2 package to the container. Covers only the container-specific parts — for ROS 2 concepts (nodes, topics, pub/sub) see the [official tutorials](https://docs.ros.org/en/jazzy/Tutorials.html).

---

## How the workspace works

The `./workspace` directory on your host is mounted into the container at `/workspace`:

```
host: ./workspace/        ←→   container: /workspace/
         src/                          src/         ← your packages
         install/          ←  colcon build writes here
         build/
         log/
```

You edit code on the host with your normal tools; the container builds and runs it. `install/setup.zsh` is sourced automatically when you open a new shell (see `container_zshrc`), so freshly built packages are immediately available.

---

## 1. Create a package

Open a shell in the container:

```bash
docker compose exec ros-gazebo zsh
```

Use the ROS 2 scaffolder — it generates a correct `package.xml`, `setup.py`, and resource markers in one step:

```bash
cd /workspace/src
ros2 pkg create --build-type ament_python my_package --node-name my_node
```

For C++ packages use `--build-type ament_cmake`; everything else below is identical.

The generated `my_node.py` is a stub `main()` that prints "Hi from my_package." — enough to prove the build/run pipeline works.

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

If you get `Package 'my_package' not found`, the overlay isn't sourced. Open a new shell (auto-sources) or run `source /workspace/install/setup.zsh` manually.

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

Verify from a second container shell:

```bash
docker compose exec ros-gazebo zsh
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
