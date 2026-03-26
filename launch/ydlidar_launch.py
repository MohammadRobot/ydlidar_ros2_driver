#!/usr/bin/python3
# Copyright 2020, EAIBOT
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import LogInfo
from launch.actions import OpaqueFunction

import lifecycle_msgs.msg
import os


def _resolve_params_file(context, share_dir):
    params_file_arg = LaunchConfiguration('params_file').perform(context).strip()
    if params_file_arg:
        return params_file_arg

    lidar_type = LaunchConfiguration('lidar_type').perform(context).strip().lower()
    lidar_to_yaml = {
        'default': 'ydlidar.yaml',
        'ydlidar': 'ydlidar.yaml',
        'g1': 'G1.yaml',
        'g2': 'G2.yaml',
        'g4': 'G4.yaml',
        'g6': 'G6.yaml',
        'x2': 'X2.yaml',
        'x2l': 'X2.yaml',
        'x3': 'X3.yaml',
        'x4': 'X4.yaml',
        'x4-pro': 'X4-Pro.yaml',
        'x4_pro': 'X4-Pro.yaml',
        'tg': 'TG.yaml',
        'tg15': 'TG.yaml',
        'tg30': 'TG.yaml',
        'tg50': 'TG.yaml',
        'tmini': 'Tmini.yaml',
        'timini': 'Tmini.yaml',
        'tmini-pro': 'Tmini.yaml',
        'tmini_pro': 'Tmini.yaml',
        'tmini-plus': 'Tmini.yaml',
        'tmini_plus': 'Tmini.yaml',
        'tmini-plus-sh': 'Tmini-Plus-SH.yaml',
        'tmini_plus_sh': 'Tmini-Plus-SH.yaml',
        'tea': 'TEA.yaml',
        'gs2': 'GS2.yaml',
        'gs5': 'GS5.yaml',
        'sdm15': 'sdm15.yaml',
    }

    if lidar_type not in lidar_to_yaml:
        supported = ', '.join(sorted(lidar_to_yaml.keys()))
        raise RuntimeError(
            f"Unsupported lidar_type '{lidar_type}'. "
            f"Use one of: {supported}, or pass params_file:=/abs/path/to/file.yaml"
        )

    return os.path.join(share_dir, 'params', lidar_to_yaml[lidar_type])


def _launch_setup(context):
    share_dir = get_package_share_directory('ydlidar_ros2_driver')
    parameter_file = _resolve_params_file(context, share_dir)

    driver_node = LifecycleNode(package='ydlidar_ros2_driver',
                                executable='ydlidar_ros2_driver_node',
                                name='ydlidar_ros2_driver_node',
                                output='screen',
                                emulate_tty=True,
                                parameters=[parameter_file],
                                namespace='/',
                                )
    tf2_node = Node(package='tf2_ros',
                    executable='static_transform_publisher',
                    name='static_tf_pub_laser',
                    arguments=['0', '0', '0.02', '0', '0', '0', '1', 'base_link', 'laser_frame'],
                    )

    return [
        LogInfo(msg=f'Using LiDAR params file: {parameter_file}'),
        driver_node,
        tf2_node,
    ]


def generate_launch_description():
    params_declare = DeclareLaunchArgument('params_file',
                                           default_value='',
                                           description='Absolute path to a ROS2 parameter YAML file. If set, this overrides lidar_type.')
    lidar_type_declare = DeclareLaunchArgument(
        'lidar_type',
        default_value='default',
        description='LiDAR model preset (example: tmini, x4, g4, gs2, sdm15). Maps to params/<model>.yaml.'
    )

    return LaunchDescription([
        params_declare,
        lidar_type_declare,
        OpaqueFunction(function=_launch_setup),
    ])
