#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controlador_navegacao.py  -  DR3 / TP2 - Exercicio 4  (no 2 de 4)
Consome a lista de waypoints e comanda a tartaruga.
Mesma maquina de estados do controlador_turtle.py do TP1:
GIRAR aponta o nariz, AVANCAR percorre - decididas pela pose lida.

Assina : /waypoints (PoseArray)   /turtle1/pose (Pose)
Publica: /turtle1/cmd_vel (Twist) /waypoint_atual (Int32)
         /status_navegacao (String)
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseArray, Twist
from turtlesim.msg import Pose
from std_msgs.msg import Int32, String


class ControladorNavegacao(Node):

    def __init__(self):
        super().__init__("controlador_navegacao")

        self.declare_parameter("tol_pos", 0.15)
        self.declare_parameter("tol_ang", 0.05)
        self.declare_parameter("v_lin", 1.5)
        self.declare_parameter("v_ang", 2.0)

        qos = QoSProfile(depth=1,
                         history=HistoryPolicy.KEEP_LAST,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(PoseArray, "/waypoints", self.cb_wps, qos)
        self.create_subscription(Pose, "/turtle1/pose", self.cb_pose, 10)

        self.pub_cmd    = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pub_idx    = self.create_publisher(Int32, "/waypoint_atual", 10)
        self.pub_status = self.create_publisher(String, "/status_navegacao", 10)

        self.wps = []
        self.pose = None
        self.i = 0
        self.fase = "GIRAR"
        self.fim = False
        self.create_timer(0.05, self.tick)

    def p(self, n):
        return self.get_parameter(n).value

    def cb_wps(self, msg):
        if self.wps:
            return                       # aceita apenas a primeira lista
        self.wps = [(q.position.x, q.position.y) for q in msg.poses]
        self.get_logger().info(f"Recebi {len(self.wps)} waypoints")
        self.publicar("navegando")

    def cb_pose(self, msg):
        self.pose = msg

    @staticmethod
    def norm(a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def publicar(self, texto):
        self.pub_status.publish(String(data=texto))

    def tick(self):
        if self.pose is None or not self.wps or self.fim:
            return

        if self.i >= len(self.wps):
            self.pub_cmd.publish(Twist())
            self.fim = True
            self.publicar("Missao concluida")
            self.get_logger().info("Missao concluida")
            return

        alvo_x, alvo_y = self.wps[self.i]
        dx, dy = alvo_x - self.pose.x, alvo_y - self.pose.y
        dist = math.hypot(dx, dy)
        erro_ang = self.norm(math.atan2(dy, dx) - self.pose.theta)

        cmd = Twist()
        if self.fase == "GIRAR":
            if abs(erro_ang) > self.p("tol_ang"):
                cmd.angular.z = self.p("v_ang") if erro_ang > 0 \
                    else -self.p("v_ang")
            else:
                self.fase = "AVANCAR"
        else:
            if dist > self.p("tol_pos"):
                cmd.linear.x = min(self.p("v_lin"), 2.0 * dist)
                cmd.angular.z = 2.0 * erro_ang
            else:
                self.get_logger().info(
                    f"Waypoint {self.i + 1} atingido "
                    f"({self.pose.x:.2f}, {self.pose.y:.2f})")
                self.pub_idx.publish(Int32(data=self.i + 1))
                self.i += 1
                self.fase = "GIRAR"

        self.pub_cmd.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    no = ControladorNavegacao()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
