"""Trivial example consumer.

Subscribes to the TurtleBot 4 camera, computes mean pixel brightness, and
publishes a Twist on /cmd_vel: drive forward when the scene is bright,
spin in place when dark. Stand-in for "real consumer that runs an
AI/CV model on the camera feed and controls the robot."
"""

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Image

CAMERA_TOPIC = '/oakd/rgb/preview/image_raw'
CMD_VEL_TOPIC = '/cmd_vel'
BRIGHTNESS_THRESHOLD = 100.0  # 0-255


class BrightnessDriver(Node):
    def __init__(self) -> None:
        super().__init__('brightness_driver')
        self.create_subscription(Image, CAMERA_TOPIC, self._on_image, 10)
        self._cmd_pub = self.create_publisher(Twist, CMD_VEL_TOPIC, 10)
        self.get_logger().info(
            f'Subscribed to {CAMERA_TOPIC}, publishing to {CMD_VEL_TOPIC}'
        )

    def _on_image(self, msg: Image) -> None:
        frame = np.frombuffer(msg.data, dtype=np.uint8)
        mean = float(frame.mean())

        cmd = Twist()
        if mean >= BRIGHTNESS_THRESHOLD:
            cmd.linear.x = 0.2
        else:
            cmd.angular.z = 0.5
        self._cmd_pub.publish(cmd)

        self.get_logger().info(
            f'mean={mean:6.2f}  ->  lin={cmd.linear.x:.2f} ang={cmd.angular.z:.2f}',
            throttle_duration_sec=1.0,
        )


def main() -> None:
    rclpy.init()
    node = BrightnessDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
