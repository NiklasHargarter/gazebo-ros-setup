"""Launches gz sim on the camera world, bridges the image topic, runs the subscriber.

Assumes:
  - This file lives at /workspace/src/camera_subscriber/launch/... OR is run via its
    absolute path: `ros2 launch /workspace/examples/camera_world/launch/camera_demo.launch.py`.
  - The world SDF is resolved via the GZ_SIM_RESOURCE_PATH env var (set below) or
    passed with an absolute path.
"""

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node


EXAMPLE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD_PATH = os.path.join(EXAMPLE_DIR, 'worlds', 'camera_world.sdf')


def generate_launch_description():
    return LaunchDescription([
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=os.path.join(EXAMPLE_DIR, 'worlds'),
        ),

        ExecuteProcess(
            cmd=['gz', 'sim', '-r', WORLD_PATH],
            output='screen',
        ),

        # Bridge the Gazebo camera topic to a ROS 2 sensor_msgs/Image topic.
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/camera/image@sensor_msgs/msg/Image@gz.msgs.Image'],
            output='screen',
        ),

        Node(
            package='camera_subscriber',
            executable='image_consumer',
            output='screen',
            parameters=[{'topic': '/camera/image'}],
        ),
    ])
