import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageConsumer(Node):
    def __init__(self):
        super().__init__('image_consumer')
        topic = self.declare_parameter('topic', '/camera/image').value
        self.sub = self.create_subscription(Image, topic, self._on_image, 10)
        self.get_logger().info(f'Subscribed to {topic}')

        self._frames = 0
        self._window_start = time.monotonic()
        self.create_timer(2.0, self._report)

    def _on_image(self, msg: Image):
        self._frames += 1
        if self._frames == 1:
            self.get_logger().info(
                f'First frame: {msg.width}x{msg.height} encoding={msg.encoding} '
                f'step={msg.step} bytes={len(msg.data)}'
            )

    def _report(self):
        now = time.monotonic()
        elapsed = now - self._window_start
        fps = self._frames / elapsed if elapsed > 0 else 0.0
        self.get_logger().info(f'{self._frames} frames in {elapsed:.2f}s ({fps:.1f} fps)')
        self._frames = 0
        self._window_start = now


def main():
    rclpy.init()
    try:
        rclpy.spin(ImageConsumer())
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()
