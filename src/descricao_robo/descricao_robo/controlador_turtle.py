#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controlador_turtle.py
DR3 - Aplicacoes Roboticas com ROS 2 / TP1 - Exercicio 4

Navega a tartaruga do Turtlesim por um quadrado de lado configuravel.

  - parametro  : lado (float, padrao 2.0)
  - publica em : /turtle1/cmd_vel   (geometry_msgs/msg/Twist)
  - assina     : /turtle1/pose      (turtlesim/msg/Pose)
  - servico    : /turtle1/set_pen   (turtlesim/srv/SetPen)

Projeto: maquina de estados avaliada por um timer.
Nao se usa sleep() dentro do callback: isso bloquearia o executor e a
pose nunca seria atualizada.

Execucao:
  ros2 run turtlesim turtlesim_node
  ros2 run descricao_robo controlador_turtle --ros-args -p lado:=3.0
"""

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen


class ControladorTurtle(Node):

    VEL_LINEAR = 1.0      # m/s  (unidades de canvas por segundo)
    VEL_ANGULAR = 1.0     # rad/s
    TOL_ANGULO = 0.02     # rad

    def __init__(self):
        super().__init__("controlador_turtle")

        # ---------------- parametros ----------------
        self.declare_parameter("lado", 2.0)
        self.lado = self.get_parameter("lado").value

        # ---------------- interfaces ----------------
        self.pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.create_subscription(Pose, "/turtle1/pose", self.cb_pose, 10)
        self.cli = self.create_client(SetPen, "/turtle1/set_pen")

        # ---------------- estado ----------------
        self.pose = None          # ultima pose recebida
        self.ini = None           # pose de referencia da fase atual
        self.fase = "AVANCAR"     # AVANCAR | GIRAR
        self.n_lado = 0           # lados ja concluidos
        self.fim = False

        self.create_timer(0.05, self.tick)
        self.get_logger().info(
            f"Controlador iniciado - lado = {self.lado:.2f}")

    # ------------------------------------------------------------------
    def cb_pose(self, msg):
        """Guarda apenas a ultima pose; nao processa nada aqui."""
        self.pose = msg

    # ------------------------------------------------------------------
    def tick(self):
        """Ciclo de controle: avalia o estado e publica um Twist."""
        if self.pose is None or self.fim:
            return

        if self.ini is None:
            self.ini = (self.pose.x, self.pose.y, self.pose.theta)

        cmd = Twist()

        if self.fase == "AVANCAR":
            d = math.hypot(self.pose.x - self.ini[0],
                           self.pose.y - self.ini[1])
            if d < self.lado:
                cmd.linear.x = self.VEL_LINEAR
            else:
                self.n_lado += 1
                self.get_logger().info(
                    f"Lado {self.n_lado} concluido - pose atual: "
                    f"({self.pose.x:.2f}, {self.pose.y:.2f}, "
                    f"{self.pose.theta:.2f})")
                self.trocar("GIRAR")

        else:  # GIRAR
            dth = abs(self.norm(self.pose.theta - self.ini[2]))
            if dth < math.pi / 2 - self.TOL_ANGULO:
                cmd.angular.z = self.VEL_ANGULAR
            elif self.n_lado >= 4:
                self.fim = True
                self.mudar_cor()
            else:
                self.trocar("AVANCAR")

        self.pub.publish(cmd)

    # ------------------------------------------------------------------
    def trocar(self, fase):
        """Muda de fase e reancora a pose de referencia."""
        self.fase = fase
        self.ini = (self.pose.x, self.pose.y, self.pose.theta)

    @staticmethod
    def norm(a):
        """Normaliza um angulo para o intervalo [-pi, pi]."""
        return (a + math.pi) % (2 * math.pi) - math.pi

    # ------------------------------------------------------------------
    def mudar_cor(self):
        """Chama /turtle1/set_pen ao fechar o quadrado."""
        self.pub.publish(Twist())          # garante parada

        if not self.cli.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn("Servico /turtle1/set_pen indisponivel")
            return

        req = SetPen.Request()
        req.r, req.g, req.b = 255, 0, 0
        req.width = 3
        req.off = 0
        self.cli.call_async(req)
        self.get_logger().info("Quadrado concluido - cor do traco alterada")


def main(args=None):
    rclpy.init(args=args)
    no = ControladorTurtle()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
