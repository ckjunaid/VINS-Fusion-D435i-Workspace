#!/bin/bash
source /opt/ros/humble/setup.bash
source install/setup.bash
echo " running the rviz.."
ros2 launch vins vins_rviz.launch.xml
