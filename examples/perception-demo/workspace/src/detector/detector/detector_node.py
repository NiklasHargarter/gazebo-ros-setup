import os
import time

import cv2
import rclpy
import torch
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ultralytics import YOLO
from vision_msgs.msg import (
    BoundingBox2D,
    Detection2D,
    Detection2DArray,
    ObjectHypothesisWithPose,
    Point2D,
    Pose2D,
)

MODEL_PATH = os.environ.get('YOLO_MODEL_PATH', '/opt/yolo/yolov8x-world.pt')

# YOLO-World is open-vocab, so phrasing dominates score on flat sim
# primitives. Feed several synonyms per object and remap every hit back to
# the canonical label, keeping the best score. 'red cube' alone scores ~0.05;
# the box/block synonyms recover it.
PROMPT_GROUPS = {
    'red cube': ['red cube', 'red box', 'red block', 'small red box'],
    'green can': ['green can', 'green cylinder', 'green soda can'],
    'blue can': ['blue can', 'blue cylinder', 'blue soda can'],
}
# Flat prompt list fed to the model + index -> canonical label.
PROMPTS = [p for group in PROMPT_GROUPS.values() for p in group]
PROMPT_TO_LABEL = {
    p: label for label, group in PROMPT_GROUPS.items() for p in group
}

LABEL_COLOR_BGR = {
    'red cube': (0, 0, 255),
    'green can': (0, 255, 0),
    'blue can': (255, 0, 0),
}
# Per-label confidence floor. The cube is the weakest detection, so it gets
# the lowest gate; cans clear a higher bar to suppress false boxes.
CONF_BY_LABEL = {'red cube': 0.10, 'green can': 0.05, 'blue can': 0.05}
INFER_HZ = 30.0
# Global floor handed to predict(); per-label gate above does the real work.
CONF_THRESH = 0.02


class Detector(Node):
    def __init__(self):
        super().__init__('detector')
        self.bridge = CvBridge()

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.get_logger().info(f'YOLO-World device: {self.device}')
        self.model = YOLO(MODEL_PATH)
        self.model.set_classes(PROMPTS)

        # Active target published by the head tracker, drawn on the overlay.
        self.active_target = None

        self.det_pub = self.create_publisher(
            Detection2DArray, '/perception/detections', 10
        )
        self.img_pub = self.create_publisher(
            Image, '/perception/image_annotated', 10
        )
        self.create_subscription(
            Image, '/camera/rgb/image_raw',
            self._on_frame, qos_profile_sensor_data,
        )
        self.create_subscription(
            String, '/perception/target', self._on_target, 10
        )

        self._min_dt = 1.0 / INFER_HZ
        self._last_t = 0.0

    def _on_target(self, msg: String):
        self.active_target = msg.data

    def _on_frame(self, msg: Image):
        now = time.monotonic()
        if now - self._last_t < self._min_dt:
            return
        self._last_t = now

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model.predict(
            frame, device=self.device, conf=CONF_THRESH, verbose=False
        )
        boxes = results[0].boxes
        names = results[0].names

        det_array = Detection2DArray()
        det_array.header = msg.header

        annotated = frame.copy()
        h, w = annotated.shape[:2]
        cv2.drawMarker(
            annotated, (w // 2, h // 2), (0, 255, 255),
            cv2.MARKER_CROSS, 24, 2,
        )

        if boxes is not None and len(boxes) > 0:
            for i in range(len(boxes)):
                conf = float(boxes.conf[i].item())
                cls_id = int(boxes.cls[i].item())
                prompt = names.get(cls_id, str(cls_id))
                label = PROMPT_TO_LABEL.get(prompt, prompt)
                if conf < CONF_BY_LABEL.get(label, CONF_THRESH):
                    continue

                x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                bw, bh = x2 - x1, y2 - y1

                det = Detection2D()
                det.bbox = BoundingBox2D(
                    center=Pose2D(
                        position=Point2D(x=cx, y=cy), theta=0.0,
                    ),
                    size_x=bw, size_y=bh,
                )
                hyp = ObjectHypothesisWithPose()
                hyp.hypothesis.class_id = label
                hyp.hypothesis.score = conf
                det.results.append(hyp)
                det_array.detections.append(det)

                color = LABEL_COLOR_BGR.get(label, (255, 255, 255))
                # Thicken the box of whichever object the tracker is chasing.
                thick = 4 if label == self.active_target else 2
                cv2.rectangle(
                    annotated,
                    (int(x1), int(y1)), (int(x2), int(y2)),
                    color, thick,
                )
                cv2.putText(
                    annotated, f'{label} {conf:.2f}',
                    (int(x1), int(y1) - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA,
                )

        if self.active_target is not None:
            banner = f'TARGET: {self.active_target}'
            color = LABEL_COLOR_BGR.get(self.active_target, (255, 255, 255))
            cv2.putText(
                annotated, banner, (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA,
            )

        self.det_pub.publish(det_array)
        out_img = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
        out_img.header = msg.header
        self.img_pub.publish(out_img)


def main():
    rclpy.init()
    node = Detector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
