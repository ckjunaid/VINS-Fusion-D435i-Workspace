#!/bin/bash
source /opt/ros/humble/setup.bash
source /home/nvidia/ros2_ws/install/setup.bash

ros2 param set /camera/camera stereo_module.emitter_enabled 0 &
echo "Running the vins fusion..."

ros2 run vins vins_node   ~/ros2_ws/src/VINS-Fusion-ROS2-Humble/config/realsense_d435i/realsense_stereo_imu_config.yaml

