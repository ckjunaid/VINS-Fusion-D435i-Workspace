# VINS-Fusion with RealSense D435i in ROS 2 Humble

This repository contains a fully optimized and debugged setup for running [VINS-Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion) (Visual-Inertial Navigation System) using an Intel RealSense D435i camera in ROS 2 Humble. 

This setup has been specifically tuned to eliminate common RealSense issues such as timestamp jitter, IR emitter interference, and high IMU noise, ensuring drift-free Visual Odometry. It also includes an option to run Pure Stereo Visual Odometry (without IMU) for downstream fusion with flight controllers like Pixhawk.

---

## 🛠️ System Requirements
* **OS:** Ubuntu 22.04
* **ROS Version:** ROS 2 Humble
* **Hardware:** Intel RealSense D435i (USB 3.0 connection required)

## 📦 Dependencies & Installation

### 1. System Dependencies
VINS-Fusion heavily relies on Ceres Solver for optimization and OpenCV for feature tracking.
```bash
sudo apt-get update
sudo apt-get install -y ros-humble-cv-bridge ros-humble-image-transport \
                        ros-humble-message-filters ros-humble-tf2-ros \
                        libceres-dev
```

### 2. Download this Workspace
Clone this entire pre-configured workspace to your computer:
```bash
cd ~
git clone https://github.com/ckjunaid/VINS-Fusion-D435i-Workspace.git ros2_ws
```

### 3. Build the Workspace
Compile the entire workspace (including VINS-Fusion and the RealSense wrapper).
```bash
cd ~/ros2_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

---

## 🚀 Key Fixes & Optimizations Included
1. **TF Tree Fix:** Fixed a bug in the original VINS-Fusion `visualization.cpp` that prevented the `world` to `body` Transform from broadcasting, which broke RViz rendering.
2. **C++ Native IMU Uniting:** Fixed the `realsense2_camera` launch file to correctly use `unite_imu_method: 'linear_interpolation'`. This completely eliminates the need for slow Python IMU merger scripts and prevents the timestamp jitter that causes gravity vector initialization failures.
3. **IR Projector Disabled:** Forced the D435i IR emitter to `0` inside `rs_launch.py`. This stops the camera from projecting static dots into the environment, which previously caused the VINS feature tracker to mistakenly perceive a stationary state during movement.
4. **IMU Noise Calibration:** Tuned the `realsense_stereo_imu_config.yaml` to handle the naturally noisy BMI085 IMU chip inside the D435i. This prevents "dead-walking" (stationary drift).
5. **Stereo Sync Enforced:** Enforced hardware frame synchronization (`enable_sync: true`) between the left and right infrared cameras.

---

## ⚙️ Running the System

### 1. Launch the Camera
The RealSense ROS 2 wrapper has been hardcoded with the optimal VSLAM parameters (30 FPS, Sync ON, Emitter OFF). Simply launch it:
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch realsense2_camera rs_launch.py
```

### 2. Launch VINS-Fusion
We have provided two execution scripts depending on your architectural needs. **IMPORTANT:** After running either script, leave the camera perfectly still on a flat surface for 3-5 seconds so VINS can initialize the gravity vector!

#### Option A: Full Visual-Inertial Odometry (VIO)
Uses both the Stereo Infrared Cameras and the internal D435i IMU.
```bash
cd ~/ros2_ws
./vins.sh
```

#### Option B: Pure Stereo Visual Odometry (VO Only)
Ignores the D435i IMU entirely. This is highly recommended for drone applications where the visual odometry output is fed into a Pixhawk/Flight Controller EKF, as the Pixhawk's IMU is isolated from vibrations and of much higher quality.
```bash
cd ~/ros2_ws
./vins_stereo.sh
```

---

## 📊 Verifying Performance in RViz
When the system is running correctly:
1. The green path line in RViz should remain perfectly steady when the camera is placed on a desk.
2. Moving the camera should result in a smooth, continuous path with no jagged teleportation or Z-axis runaways.
3. Returning the camera to its starting physical location should result in a clean loop closure in the RViz visualization.

## 🧰 Useful Debugging Commands
If you suspect hardware issues, use these commands to verify the RealSense output:
```bash
# Verify camera is hitting 30 FPS
ros2 topic hz /camera/infra1/image_rect_raw

# Verify IMU is hitting ~200 FPS
ros2 topic hz /camera/imu

# Verify IR emitter is successfully disabled
ros2 param get /camera/camera stereo_module.emitter_enabled
```
