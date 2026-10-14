#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
turtlesim_nav.launch.py  -  DR3 / TP1 - Exercicio 4
Sobe o turtlesim_node e o controlador_turtle simultaneamente.

  ros2 launch descricao_robo turtlesim_nav.launch.py
  ros2 launch descricao_robo turtlesim_nav.launch.py lado:=3.0
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    lado = LaunchConfiguration("lado")

    return LaunchDescription([
        DeclareLaunchArgument(
            "lado",
            default_value="2.0",
            description="Comprimento do lado do quadrado",
        ),
        Node(
            package="turtlesim",
            executable="turtlesim_node",
            name="turtlesim",
            output="screen",
        ),
        Node(
            package="descricao_robo",
            executable="controlador_turtle",
            name="controlador_turtle",
            output="screen",
            parameters=[{"lado": lado}],
        ),
    ])
