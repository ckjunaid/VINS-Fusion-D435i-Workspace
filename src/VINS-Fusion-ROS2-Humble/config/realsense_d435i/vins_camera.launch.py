from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    # Path to the realsense launch file
    realsense_launch_file = os.path.join(
        FindPackageShare('realsense2_camera').find('realsense2_camera'),
        'launch',
        'rs_launch.py'
    )

    # Path to our custom yaml parameters
    custom_params_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'realsense_params.yaml'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(realsense_launch_file),
            launch_arguments={
                'config_file': f"'{custom_params_file}'"
            }.items()
        )
    ])
