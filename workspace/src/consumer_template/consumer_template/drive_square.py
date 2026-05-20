import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist


class DriveSquare(Node):
    """Drive an open-loop square. Idle until the `start` parameter is true."""

    LINEAR_SPEED = 0.1   # m/s
    SIDE_DURATION = 5.0  # s -> ~0.5 m per side
    ANGULAR_SPEED = math.pi / 2 / 5.0  # rad/s -> 90 deg in 5 s
    TURN_DURATION = 5.0  # s

    def __init__(self):
        super().__init__('drive_square')
        self.declare_parameter('start', False)
        self.declare_parameter('topic', '/cmd_vel')
        topic = self.get_parameter('topic').get_parameter_value().string_value

        control_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.pub = self.create_publisher(Twist, topic, control_qos)

        if not self.get_parameter('start').get_parameter_value().bool_value:
            self.get_logger().info(
                'start:=false (default). Re-run with `--ros-args -p start:=true` to drive.'
            )
            self._timer = None
            return

        self._state = ('forward', 0)
        self._phase_start = self.get_clock().now()
        self._timer = self.create_timer(0.05, self._tick)
        self.get_logger().info(f'driving open-loop square on {topic}')

    def _publish(self, lin: float, ang: float) -> None:
        msg = Twist()
        msg.linear.x = lin
        msg.angular.z = ang
        self.pub.publish(msg)

    def _phase_elapsed(self) -> float:
        return (self.get_clock().now() - self._phase_start).nanoseconds * 1e-9

    def _tick(self) -> None:
        phase, side = self._state

        if phase == 'forward':
            if self._phase_elapsed() < self.SIDE_DURATION:
                self._publish(self.LINEAR_SPEED, 0.0)
                return
            self._state = ('turn', side)
            self._phase_start = self.get_clock().now()
            return

        if phase == 'turn':
            if self._phase_elapsed() < self.TURN_DURATION:
                self._publish(0.0, self.ANGULAR_SPEED)
                return
            side += 1
            if side >= 4:
                self._publish(0.0, 0.0)
                self.get_logger().info('square complete, stopping')
                self._timer.cancel()
                return
            self._state = ('forward', side)
            self._phase_start = self.get_clock().now()


def main():
    rclpy.init()
    node = DriveSquare()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.pub.publish(Twist())
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
