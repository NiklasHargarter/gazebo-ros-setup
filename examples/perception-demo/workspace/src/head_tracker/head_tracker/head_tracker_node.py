import math
import time

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, JointState
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from vision_msgs.msg import Detection2DArray

TARGETS = ['red cube', 'green can', 'blue can']  # must match detector groups
KP_PAN = 0.5
KP_TILT = 0.6
# Enter fixation inside FIX_TOL, leave only outside the larger EXIT_TOL, so a
# centered target doesn't chatter in/out of the locked state on small jitter.
FIX_TOL_NORM = 0.10
EXIT_TOL_NORM = 0.16
FIX_HOLD_S = 2.5
NECK_PAN_MIN, NECK_PAN_MAX = -1.07, 2.07
NECK_TILT_MIN, NECK_TILT_MAX = -1.57, 0.5
PAN_JOINT = 'neck_pan'
TILT_JOINT = 'neck_tilt'

CTRL_HZ = 10.0
# Command horizon: ~2 control ticks. Matching the publish rate keeps the
# trajectory controller in smooth follow instead of restarting a 0.3 s move
# every 0.1 s (the old cause of the jerk).
GOAL_DT = 0.2
# Max change in commanded angle per tick (rad). At 10 Hz this caps head speed
# to MAX_STEP*CTRL_HZ rad/s and is the single knob that kills aggressive snaps.
MAX_STEP = 0.03

# A cached detection older than this is treated as "no target" -> search.
# Generous so brief YOLO flicker doesn't drop a lock mid-track.
DET_FRESH_S = 0.8

# Search sweep: slow Lissajous, eased in over SEARCH_RAMP_S so it doesn't
# lurch from rest. Peak velocities stay under MAX_STEP*CTRL_HZ so the sweep
# tracks the reference exactly (no slew clipping = no stutter).
SEARCH_PAN_CENTER = 0.5
SEARCH_PAN_AMP = 0.8
SEARCH_PAN_PERIOD_S = 18.0    # keep peak sweep vel under MAX_STEP*CTRL_HZ
SEARCH_TILT_CENTER = 0.12     # mild downward bias; objects sit near eye line
SEARCH_TILT_AMP = 0.2
SEARCH_TILT_PERIOD_S = 29.0   # coprime-ish with pan period for coverage
SEARCH_RAMP_S = 2.0


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


class HeadTracker(Node):
    def __init__(self):
        super().__init__('head_tracker')
        self.frame_w = None
        self.frame_h = None
        self.cur_pan = 0.0
        self.cur_tilt = 0.0
        self.have_joint = False
        self.target_idx = 0
        self.fix_t0 = None

        # Commanded reference we slew toward goal_*. Seeded from the measured
        # pose once, then driven open-loop in command space so actuator lag
        # never feeds back into the correction (the old windup/bounce bug).
        self.cmd_init = False
        self.cmd_pan = 0.0
        self.cmd_tilt = 0.0

        self.last_det = None
        self.last_det_t = 0.0
        self.searching = False
        self.search_t0 = None

        self.cmd_pub = self.create_publisher(
            JointTrajectory, '/Head_controller/joint_trajectory', 10
        )
        self.target_pub = self.create_publisher(
            String, '/perception/target', 10
        )
        self.create_subscription(
            CameraInfo, '/camera/rgb/camera_info', self._on_caminfo, 10
        )
        self.create_subscription(
            JointState, '/joint_states', self._on_joints, 10
        )
        self.create_subscription(
            Detection2DArray, '/perception/detections', self._on_det, 10
        )
        self.create_timer(1.0 / CTRL_HZ, self._control)

        self.get_logger().info(
            f'tracker armed. first target: {TARGETS[self.target_idx]}'
        )

    def _on_caminfo(self, msg: CameraInfo):
        self.frame_w = msg.width
        self.frame_h = msg.height

    def _on_joints(self, msg: JointState):
        pos = dict(zip(msg.name, msg.position))
        if PAN_JOINT in pos:
            self.cur_pan = pos[PAN_JOINT]
        if TILT_JOINT in pos:
            self.cur_tilt = pos[TILT_JOINT]
        self.have_joint = True

    def _on_det(self, msg: Detection2DArray):
        self.last_det = msg
        self.last_det_t = time.monotonic()

    def _publish_target(self):
        self.target_pub.publish(String(data=TARGETS[self.target_idx]))

    def _emit(self, goal_pan, goal_tilt):
        """Slew the commanded reference toward goal and publish it."""
        goal_pan = _clamp(goal_pan, NECK_PAN_MIN, NECK_PAN_MAX)
        goal_tilt = _clamp(goal_tilt, NECK_TILT_MIN, NECK_TILT_MAX)
        self.cmd_pan += _clamp(goal_pan - self.cmd_pan, -MAX_STEP, MAX_STEP)
        self.cmd_tilt += _clamp(goal_tilt - self.cmd_tilt, -MAX_STEP, MAX_STEP)

        traj = JointTrajectory()
        traj.joint_names = [PAN_JOINT, TILT_JOINT]
        pt = JointTrajectoryPoint()
        pt.positions = [self.cmd_pan, self.cmd_tilt]
        pt.time_from_start = Duration(sec=0, nanosec=int(GOAL_DT * 1e9))
        traj.points = [pt]
        self.cmd_pub.publish(traj)

    def _match_target(self):
        """Best-confidence detection of the current target, or None."""
        if self.last_det is None:
            return None
        if time.monotonic() - self.last_det_t > DET_FRESH_S:
            return None
        target = TARGETS[self.target_idx]
        match, best = None, -1.0
        for det in self.last_det.detections:
            if not det.results:
                continue
            r = det.results[0]
            if r.hypothesis.class_id == target and r.hypothesis.score > best:
                match, best = det, r.hypothesis.score
        return match

    def _control(self):
        if self.frame_w is None or not self.have_joint:
            return
        if not self.cmd_init:
            self.cmd_pan = self.cur_pan
            self.cmd_tilt = self.cur_tilt
            self.cmd_init = True

        self._publish_target()

        match = self._match_target()
        if match is None:
            self._search()
            return

        if self.searching:
            self.searching = False
            self.get_logger().info(
                f'acquired {TARGETS[self.target_idx]} -> tracking'
            )

        cx = match.bbox.center.position.x
        cy = match.bbox.center.position.y
        err_x = (cx - self.frame_w / 2.0) / self.frame_w
        err_y = (cy - self.frame_h / 2.0) / self.frame_h

        # Always keep correcting (slew-limited), even while fixated, so the
        # lock holds against drift instead of freezing and losing the target.
        self._emit(
            self.cmd_pan - KP_PAN * err_x,
            self.cmd_tilt + KP_TILT * err_y,
        )

        centered = abs(err_x) < FIX_TOL_NORM and abs(err_y) < FIX_TOL_NORM
        drifted = abs(err_x) > EXIT_TOL_NORM or abs(err_y) > EXIT_TOL_NORM
        now = time.monotonic()
        if centered and self.fix_t0 is None:
            self.fix_t0 = now
        elif drifted:
            self.fix_t0 = None

        if self.fix_t0 is not None and now - self.fix_t0 >= FIX_HOLD_S:
            self.get_logger().info(f'{TARGETS[self.target_idx]} fixated')
            self.target_idx = (self.target_idx + 1) % len(TARGETS)
            self.fix_t0 = None
            self.get_logger().info(
                f'-> next target: {TARGETS[self.target_idx]}'
            )

    def _search(self):
        now = time.monotonic()
        if not self.searching:
            self.searching = True
            self.search_t0 = now
            self.fix_t0 = None
            self.get_logger().info(
                f'searching for {TARGETS[self.target_idx]}...'
            )
        dt = now - self.search_t0
        ramp = min(1.0, dt / SEARCH_RAMP_S)
        pan = SEARCH_PAN_CENTER + ramp * SEARCH_PAN_AMP * math.sin(
            2.0 * math.pi * dt / SEARCH_PAN_PERIOD_S
        )
        tilt = SEARCH_TILT_CENTER + ramp * SEARCH_TILT_AMP * math.sin(
            2.0 * math.pi * dt / SEARCH_TILT_PERIOD_S
        )
        self._emit(pan, tilt)


def main():
    rclpy.init()
    node = HeadTracker()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
