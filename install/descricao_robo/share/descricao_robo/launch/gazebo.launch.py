#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gazebo.launch.py  -  DR3 / Etapa 2
Sobe o Gazebo Classic, publica a descricao do robo e faz o spawn.
Este e o arquivo que o TP2 (Exercicio 1) manda atualizar com os
plugins libgazebo_ros_diff_drive e libgazebo_ros_ray_sensor.

  ros2 launch descricao_robo gazebo.launch.py
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("descricao_robo")
    gz = get_package_share_directory("gazebo_ros")

    robot_desc = xacro.process_file(
        os.path.join(pkg, "urdf", "robo_diff.xacro")).toxml()

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gz, "launch", "gazebo.launch.py")
            )
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_desc,
                         "use_sim_time": True}],
            output="screen",
        ),
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            name="spawn_entity",
            arguments=["-topic", "robot_description",
                       "-entity", "robo_diff",
                       "-z", "0.1"],
            output="screen",
        ),
    ])
