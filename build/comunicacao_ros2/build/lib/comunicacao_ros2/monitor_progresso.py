#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor_progresso.py  -  DR3 / TP2 - Exercicio 4  (no 3 de 4)
Acompanha a pose e oferece o status de chegada por SERVICO.

Assina : /turtle1/pose (Pose)   /waypoint_atual (Int32)
Serve  : /status_missao  std_srvs/srv/Trigger

Por que Trigger e nao um .srv proprio: pacote ament_python nao
gera interfaces. Mensagem ou servico customizado exigiria um
segundo pacote, em ament_cmake. Trigger resolve com o padrao.
"""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Int32
from std_srvs.srv import Trigger


class MonitorProgresso(Node):

    def __init__(self):
        super().__init__("monitor_progresso")

        self.declare_parameter("total_waypoints", 3)

        self.pose = None
        self.atingidos = 0
        self.dist = 0.0
        self.ultima = None

        self.create_subscription(Pose, "/turtle1/pose", self.cb_pose, 10)
        self.create_subscription(Int32, "/waypoint_atual", self.cb_wp, 10)
        self.create_service(Trigger, "/status_missao", self.servir)

        self.get_logger().info("Servico /status_missao disponivel")

    def cb_pose(self, msg):
        if self.ultima is not None:
            dx = msg.x - self.ultima[0]
            dy = msg.y - self.ultima[1]
            self.dist += (dx * dx + dy * dy) ** 0.5
        self.ultima = (msg.x, msg.y)
        self.pose = msg

    def cb_wp(self, msg):
        self.atingidos = msg.data

    def servir(self, req, resp):
        total = self.get_parameter("total_waypoints").value
        if self.pose is None:
            resp.success = False
            resp.message = "ainda sem pose"
            return resp
        resp.success = self.atingidos >= total
        resp.message = (
            f"{self.atingidos}/{total} waypoints | "
            f"pose ({self.pose.x:.2f}, {self.pose.y:.2f}) | "
            f"percorrido {self.dist:.2f}")
        return resp


def main(args=None):
    rclpy.init(args=args)
    no = MonitorProgresso()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
