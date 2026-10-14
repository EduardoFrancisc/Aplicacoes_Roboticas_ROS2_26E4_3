#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visualizar_xacro.launch.py  -  DR3 / TP1 - Exercicio 3
Processa o .xacro em tempo de launch e sobe o joint_state_publisher_gui
para movimentar as juntas continuous interativamente.

  ros2 launch descricao_robo visualizar_xacro.launch.py
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("descricao_robo")
    xacro_file = os.path.join(pkg, "urdf", "robo_diff.xacro")
    rviz = os.path.join(pkg, "rviz", "robo_diff.rviz")

    # expansao do XACRO -> string URDF
    robot_desc = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_desc}],
            output="screen",
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz] if os.path.exists(rviz) else [],
            output="screen",
        ),
    ])
