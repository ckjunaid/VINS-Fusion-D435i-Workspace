#!/bin/bash
source /opt/ros/humble/setup.bash
source /home/nvidia/ros2_ws/install/setup.bash

echo "Starting RealSense with VINS-Fusion optimal parameters (Sync ON, Emitter OFF, 30 FPS)..."

ros2 launch realsense2_camera rs_launch.py \
  infra_fps:=30.0 \
  infra_width:=640 \
  infra_height:=480 \
  enable_infra1:=true \
  enable_infra2:=true \
  enable_color:=false \
  enable_depth:=false \
  enable_gyro:=true \
  enable_accel:=true \
  gyro_fps:=200.0 \
  accel_fps:=250.0 \
  unite_imu_method:=1 \
  enable_sync:=true \
  emitter_enabled:=0
