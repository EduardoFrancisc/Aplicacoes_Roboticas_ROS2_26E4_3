#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
navegacao_turtlesim.launch.py  -  DR3 / TP2 - Exercicio 4
Sobe o Turtlesim e os quatro nos do sistema de navegacao.

    ros2 launch comunicacao_ros2 navegacao_turtlesim.launch.py
    ros2 launch comunicacao_ros2 navegacao_turtlesim.launch.py \
         waypoints:="[9.0, 9.0, 2.0, 9.0, 2.0, 2.0]"
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

WPS_PADRAO = "[8.0, 8.0, 3.0, 8.0, 3.0, 3.0]"


def generate_launch_description():
    wps = LaunchConfiguration("waypoints")

    return LaunchDescription([
        DeclareLaunchArgument(
            "waypoints", default_value=WPS_PADRAO,
            description="Lista plana [x1,y1, x2,y2, ...]"),

        Node(package="turtlesim", executable="turtlesim_node",
             name="turtlesim", output="screen"),

        Node(package="comunicacao_ros2", executable="gerador_waypoints",
             name="gerador_waypoints", output="screen",
             parameters=[{"waypoints": wps}]),

        Node(package="comunicacao_ros2", executable="controlador_navegacao",
             name="controlador_navegacao", output="screen"),

        Node(package="comunicacao_ros2", executable="monitor_progresso",
             name="monitor_progresso", output="screen",
             parameters=[{"total_waypoints": 3}]),

        Node(package="comunicacao_ros2", executable="painel_status",
             name="painel_status", output="screen"),
    ])
