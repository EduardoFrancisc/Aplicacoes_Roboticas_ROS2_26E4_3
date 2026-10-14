#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visualizar.launch.py  -  DR3 / TP1 - Exercicio 2
Sobe o robot_state_publisher com o URDF puro e abre o RViz2.

  ros2 launch descricao_robo visualizar.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("descricao_robo")
    urdf = os.path.join(pkg, "urdf", "robo_diff.urdf")
    rviz = os.path.join(pkg, "rviz", "robo_diff.rviz")

    # robot_description recebe o CONTEUDO do arquivo, nao o caminho.
    with open(urdf, "r") as f:
        robot_desc = f.read()

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_desc}],
            output="screen",
        ),
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
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
