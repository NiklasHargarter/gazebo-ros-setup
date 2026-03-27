---
title: Writing Your Own Nodes
layout: default
nav_order: 4
---

# Writing Your Own Nodes

This page explains how to write and run your own ROS 2 nodes using this container — without relying on built-in demos. This applies equally to robotics developers writing control or sensor logic and to AI developers integrating perception or decision-making nodes.

---

## How External Code Works in This Setup

The `./workspace` directory on your host machine is mounted into the container at `/workspace`. This means:

- You write and edit code on your host with your normal tools (VSCode, etc.)
- The container compiles and runs it
- Changes are reflected immediately — no rebuild of the Docker image needed

```
host: ./workspace/        ←→   container: /workspace/
         src/my_package/               src/my_package/
         install/          ←  colcon build writes here
         build/
         log/
```

---

## Step 1 — Create a Package on Your Host

From the repo root on your **host machine**:

```bash
# Python package
mkdir -p workspace/src/my_package/my_package
touch workspace/src/my_package/my_package/__init__.py

# Minimal package.xml
cat > workspace/src/my_package/package.xml << 'EOF'
<?xml version="1.0"?>
<package format="3">
  <name>my_package</name>
  <version>0.0.1</version>
  <description>My ROS 2 node</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <buildtool_depend>ament_python</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
EOF

# setup.py
cat > workspace/src/my_package/setup.py << 'EOF'
from setuptools import setup

setup(
    name='my_package',
    version='0.0.1',
    packages=['my_package'],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'my_node = my_package.my_node:main',
        ],
    },
)
EOF
```

---

## Step 2 — Write Your Node

Create `workspace/src/my_package/my_package/my_node.py` on your host:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')

        # Publish on a topic
        self.publisher = self.create_publisher(String, '/my_topic', 10)

        # Subscribe to a topic
        self.subscription = self.create_subscription(
            String,
            '/my_topic',
            self.listener_callback,
            10,
        )

        # Timer: publish every second
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('my_node started')

    def timer_callback(self):
        msg = String()
        msg.data = 'hello from my_node'
        self.publisher.publish(msg)

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

This is a smoke test only — the node publishes to itself to confirm the build and run pipeline works end to end. Real nodes subscribe to topics from the bridge config and the shared interfaces package, not `std_msgs`.

---

## Step 3 — Build Inside the Container

Open a terminal in the container:

```bash
docker compose exec ros-gazebo zsh
```

Then build:

```bash
cd /workspace
colcon build --symlink-install
```

`--symlink-install` means Python files are symlinked rather than copied — edits on your host take effect immediately without rebuilding.

---

## Step 4 — Run Your Node

The workspace overlay is sourced automatically when you open a new shell (via `.zshrc`). If you're in the same shell where you just built:

```bash
source /workspace/install/setup.zsh
ros2 run my_package my_node
```

Verify it's running in another terminal:

```bash
docker compose exec ros-gazebo zsh
ros2 node list        # should show /my_node
ros2 topic echo /my_topic
```

---

## Working Against the Shared Interface

For nodes that integrate with the rest of the team stack, replace the `std_msgs` imports with the shared interfaces package. The pattern is identical — only the message type changes:

```python
from my_interfaces.msg import MyCustomMsg   # shared interfaces package

self.subscription = self.create_subscription(
    MyCustomMsg,
    '/agreed/topic/name',    # from bridge config YAML
    self.callback,
    10,
)
```

The shared interfaces package must be present in `workspace/src/` and built before your node. See [Integration Architecture](ros2-gazebo-integration.md) for the full interface contract.

---

## Developing Without the Full Stack

If the simulation or robot team's code is not available, use a bag file to replay the topics your node depends on:

```bash
# In one terminal — replay recorded sensor data
ros2 bag play path/to/recorded.bag

# In another terminal — run your node against the replayed topics
ros2 run my_package my_node
```

Your node cannot tell the difference between live topics and a bag replay.

---

## Package Structure Reference

```
workspace/
└── src/
    └── my_package/
        ├── package.xml
        ├── setup.py
        └── my_package/
            ├── __init__.py
            └── my_node.py
```

For C++ nodes the structure uses `CMakeLists.txt` instead of `setup.py` and `<buildtool_depend>ament_cmake</buildtool_depend>` in `package.xml`. The build and run steps are identical.
