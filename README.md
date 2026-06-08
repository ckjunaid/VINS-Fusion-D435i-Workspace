# VINS-Fusion with RealSense D435i in ROS 2 Humble

This repository contains a fully optimized and debugged setup for running [VINS-Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion) (Visual-Inertial Navigation System) using an Intel RealSense D435i camera in ROS 2 Humble. 

This setup has been specifically tuned to eliminate common RealSense issues such as timestamp jitter, IR emitter interference, and high IMU noise, ensuring drift-free Visual Odometry. It also includes an option to run Pure Stereo Visual Odometry (without IMU) for downstream fusion with flight controllers like Pixhawk.

> **Note:** The original VINS-Fusion-ROS2 targets Ubuntu 20.04 + ROS2 Foxy. This fork has been ported and tested on **Ubuntu 22.04 + ROS2 Humble**.

---

## 🛠️ System Requirements

| Component | Requirement |
|-----------|------------|
| **OS** | Ubuntu 22.04 LTS |
| **Architecture** | `x86_64` (Intel/AMD Laptop) or `arm64` (Jetson/Raspberry Pi) |
| **ROS Version** | ROS 2 Humble |
| **Camera** | Intel RealSense D435i |
| **USB** | USB 3.0 port (blue port) required |

---

## 📦 Dependencies & Installation

### 1. Install ROS 2 Humble
Follow the [official ROS 2 Humble installation guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html), or run:
```bash
sudo apt install ros-humble-desktop
```

### 2. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-message-filters \
    ros-humble-tf2-ros \
    libgoogle-glog-dev \
    libgflags-dev \
    libatlas-base-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    cmake
```

### 3. Install Ceres Solver 2.1.0 (Build from Source)
VINS-Fusion requires Ceres Solver for its optimization backend. It must be built from source:
```bash
cd ~
git clone https://ceres-solver.googlesource.com/ceres-solver
cd ceres-solver
git checkout 2.1.0
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

### 4. Install Intel RealSense SDK (librealsense2)

**For x86_64 (Laptop):**
```bash
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo jammy main" | sudo tee /etc/apt/sources.list.d/librealsense.list
sudo apt update
sudo apt install librealsense2-dkms librealsense2-utils librealsense2-dev
```

**For arm64 (Jetson / Raspberry Pi):**
```bash
# Build librealsense from source
cd ~
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

### 5. Clone and Build this Workspace
```bash
cd ~
git clone https://github.com/ckjunaid/VINS-Fusion-D435i-Workspace.git ros2_ws
cd ros2_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

---

## 🚀 Key Fixes & Optimizations Included
1. **TF Tree Fix:** Fixed a bug in the original VINS-Fusion `visualization.cpp` where the `pubTF()` function was short-circuited with an early `return;` statement. This prevented the `world → body → camera` Transform Tree from broadcasting, which completely broke RViz rendering. We rewrote the function with a properly initialized `tf2_ros::TransformBroadcaster`.
2. **C++ Native IMU Uniting:** Fixed the `realsense2_camera` launch file to correctly use `unite_imu_method: 'linear_interpolation'` (the original used `'1'` which was silently failing in ROS2 Humble). This eliminates the need for slow Python IMU merger scripts and prevents timestamp jitter.
3. **IR Projector Disabled:** Hardcoded the D435i IR emitter to `OFF` inside `rs_launch.py`. The projected dot pattern was causing the feature tracker to lock onto static dots, resulting in catastrophic drift.
4. **IMU Noise Calibration:** Tuned the IMU noise parameters (`acc_n`, `gyr_n`, `acc_w`, `gyr_w`) in `realsense_stereo_imu_config.yaml` to match the naturally noisy BMI085 IMU chip inside the D435i.
5. **Stereo Sync Enforced:** Enforced hardware frame synchronization (`enable_sync: true`) between the left and right infrared cameras to prevent stereo mismatch during motion.

---

## ⚙️ Running the System

### 1. Launch the Camera
The RealSense ROS 2 wrapper has been hardcoded with optimal VSLAM parameters (30 FPS, Sync ON, Emitter OFF):
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch realsense2_camera rs_launch.py
```

### 2. Launch VINS-Fusion

> ⚠️ **IMPORTANT:** After running either script, leave the camera perfectly still on a flat surface for **3-5 seconds** so VINS can initialize the gravity vector!

#### Option A: Full Visual-Inertial Odometry (VIO)
Uses both the Stereo Infrared Cameras and the internal D435i IMU:
```bash
cd ~/ros2_ws
./vins.sh
```

#### Option B: Pure Stereo Visual Odometry (VO Only — Recommended for Drones)
Ignores the D435i IMU entirely. Recommended for drone applications where the visual odometry output is fed into a Pixhawk/Flight Controller EKF, as the Pixhawk's IMU is vibration-isolated and of much higher quality:
```bash
cd ~/ros2_ws
./vins_stereo.sh
```

### 3. Launch RViz Visualization
```bash
cd ~/ros2_ws
./rviz.sh
```

---

## 📊 Verifying Performance
When the system is running correctly:
1. ✅ The green path line in RViz should remain **perfectly steady** when the camera is placed on a desk.
2. ✅ Moving the camera should result in a **smooth, continuous path** with no jagged teleportation.
3. ✅ Returning the camera to its starting location should result in a **clean loop closure**.
4. ❌ If the path shoots vertically into the sky → IMU timestamp issue (use `./vins_stereo.sh` instead).
5. ❌ If you see hundreds of features clustered in the image center → IR emitter is ON (verify with debugging commands below).

## 🧰 Debugging Commands
```bash
# Verify camera is hitting 30 FPS
ros2 topic hz /camera/infra1/image_rect_raw

# Verify IMU is hitting ~200 FPS
ros2 topic hz /camera/imu

# Verify IR emitter is OFF (should return 0)
ros2 param get /camera/camera stereo_module.emitter_enabled

# View raw X, Y, Z position in real-time
ros2 topic echo /odometry
```

---

## 🏗️ Architecture
This workspace uses the D435i's **stereo infrared cameras** (global shutter) instead of the RGB camera (rolling shutter) for superior visual tracking performance. The system publishes:

| Topic | Description |
|-------|------------|
| `/odometry` | 6-DOF pose estimate (position + orientation) |
| `/path` | Full trajectory history |
| `/point_cloud` | 3D feature points in world frame |
| `/camera/imu` | Unified IMU data (when using VIO mode) |

---

## 📄 License
This project builds upon [VINS-Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion) by HKUST Aerial Robotics Group, licensed under the GNU General Public License v3.0.
