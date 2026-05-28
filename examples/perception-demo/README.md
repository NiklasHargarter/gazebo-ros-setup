# perception-demo

Two-node ROS2 consumer:

- `detector` — YOLO-World on `/camera/rgb/image_raw`. Open-vocab prompts
  `["red cube", "green can", "blue can"]` — shape-accurate words score far
  higher than `"block"` on the plain-shaded sim primitives. Publishes
  detections and an annotated image.
- `head_tracker` — P-controls `neck_pan` / `neck_tilt` to center the current
  target in frame. Cycles red → green → blue: holds each for `FIX_HOLD`
  consecutive in-tolerance frames, then advances. When the target isn't in
  view (startup, or swept out of frame) it runs a Lissajous head sweep until
  it reacquires, then resumes tracking. Control runs on a `CTRL_HZ` timer, not
  the detection callback, so the head keeps moving with no detections.

## Bring-up

```sh
ros-upd                          # sim + robot
cd examples/perception-demo
docker compose build
docker compose run --rm detector bash -c "cd /workspace && colcon build"
docker compose up
```

View annotated feed:

```sh
ros2 run rqt_image_view rqt_image_view /perception/image_annotated
```

## Topics

| Topic | Dir | Type |
|---|---|---|
| `/camera/rgb/image_raw` | sim → detector | `sensor_msgs/Image` |
| `/camera/rgb/camera_info` | sim → tracker | `sensor_msgs/CameraInfo` |
| `/perception/detections` | detector → tracker | `vision_msgs/Detection2DArray` |
| `/perception/image_annotated` | detector → | `sensor_msgs/Image` |
| `/perception/target` | tracker → detector | `std_msgs/String` |
| `/joint_states` | robot → tracker | `sensor_msgs/JointState` |
| `/Head_controller/joint_trajectory` | tracker → robot | `trajectory_msgs/JointTrajectory` |

## Tuning

`detector_node.py`: `PROMPT_GROUPS` (synonyms per object), `CONF_BY_LABEL`
(per-label floor), `INFER_HZ`.
`head_tracker_node.py`: `KP_PAN`, `KP_TILT`, `FIX_TOL_NORM`, `FIX_HOLD_S`,
`MAX_STEP` (slew cap), `SEARCH_*` (sweep center/amplitude/period for pan and
tilt), `DET_FRESH_S`.

If pan moves the wrong direction, flip the sign on `new_pan = self.cur_pan - KP_PAN * err_x`.
