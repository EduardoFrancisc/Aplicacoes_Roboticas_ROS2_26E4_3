#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gazebo.launch.py  -  DR3 / TP2 - Exercicio 1
Versao da Etapa 3: ja aponta para o robo_diff_gazebo.xacro, que traz
os plugins libgazebo_ros_diff_drive.so e libgazebo_ros_ray_sensor.so.

Substitui o gazebo.launch.py do TP1. Nao precisa editar nada.

    ros2 launch descricao_robo gazebo.launch.py

Para voltar ao modelo sem plugins, do TP1:
    ros2 launch descricao_robo gazebo.launch.py modelo:=robo_diff.xacro
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

MODELO_PADRAO = "robo_diff_gazebo.xacro"


def _montar(context, *args, **kwargs):
    pkg = get_package_share_directory("descricao_robo")
    gz = get_package_share_directory("gazebo_ros")

    nome = LaunchConfiguration("modelo").perform(context)
    caminho = os.path.join(pkg, "urdf", nome)
    if not os.path.exists(caminho):
        raise RuntimeError(
            f"Modelo nao encontrado: {caminho}\n"
            f"Confira se o colcon build instalou a pasta urdf/ com:\n"
            f"  ls {os.path.join(pkg, 'urdf')}")

    robot_desc = xacro.process_file(caminho).toxml()

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gz, "launch", "gazebo.launch.py"))),

        Node(package="robot_state_publisher",
             executable="robot_state_publisher",
             name="robot_state_publisher",
             parameters=[{"robot_description": robot_desc,
                          "use_sim_time": True}],
             output="screen"),

        Node(package="gazebo_ros",
             executable="spawn_entity.py",
             name="spawn_entity",
             arguments=["-topic", "robot_description",
                        "-entity", "robo_diff",
                        "-z", "0.1"],
             output="screen"),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "modelo", default_value=MODELO_PADRAO,
            description="Arquivo .xacro dentro de descricao_robo/urdf/"),
        OpaqueFunction(function=_montar),
    ])
