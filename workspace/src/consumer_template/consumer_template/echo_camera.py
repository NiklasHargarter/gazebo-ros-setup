import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class EchoCamera(Node):
    def __init__(self):
        super().__init__('echo_camera')
        self.declare_parameter('topic', '/camera/rgb/image_raw')
        topic = self.get_parameter('topic').get_parameter_value().string_value
        self.sub = self.create_subscription(
            Image, topic, self._on_frame, qos_profile_sensor_data,
        )
        self._count = 0
        self.get_logger().info(f'subscribed to {topic} (sensor-data QoS)')

    def _on_frame(self, msg: Image) -> None:
        self._count += 1
        if self._count == 1 or self._count % 30 == 0:
            self.get_logger().info(
                f'frame #{self._count}: {msg.width}x{msg.height} '
                f'encoding={msg.encoding} step={msg.step}'
            )


def main():
    rclpy.init()
    node = EchoCamera()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
