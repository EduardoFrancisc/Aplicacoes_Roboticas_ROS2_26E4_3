#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arvore_comportamento.py  -  DR3 / TP2 - Exercicio 2
Behavior Tree em Python puro, integrada ao executor do ROS 2.

Padrao tick/status:
    cada no responde SUCCESS, FAILURE ou RUNNING a cada tick.
    O tick desce pela arvore a partir da raiz, a cada 0.5 s.

Arvore montada:
    Sequence( VerificarBateria, MoverParaPonto )

Execucao:
    ros2 run comunicacao_ros2 arvore_comportamento

Em outro terminal, para forcar o FAILURE:
    ros2 topic pub /bateria std_msgs/msg/Float32 "{data: 10.0}"
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32


# ===================== os tres estados =====================
class Estado:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


# ===================== no base =====================
class No:
    """Todo no de uma Behavior Tree sabe responder a um tick."""

    def __init__(self, nome):
        self.nome = nome

    def tick(self):
        raise NotImplementedError


# ===================== nos de CONTROLE =====================
class Sequence(No):
    """E logico: executa os filhos em ordem, para no primeiro FAILURE."""

    def __init__(self, nome, filhos):
        super().__init__(nome)
        self.filhos = filhos

    def tick(self):
        for filho in self.filhos:
            st = filho.tick()
            if st in (Estado.FAILURE, Estado.RUNNING):
                return st          # interrompe a sequencia
        return Estado.SUCCESS      # todos deram SUCCESS


class Fallback(No):
    """OU logico: executa os filhos em ordem, para no primeiro SUCCESS."""

    def __init__(self, nome, filhos):
        super().__init__(nome)
        self.filhos = filhos

    def tick(self):
        for filho in self.filhos:
            st = filho.tick()
            if st in (Estado.SUCCESS, Estado.RUNNING):
                return st
        return Estado.FAILURE      # todos falharam


# ===================== nos de EXECUCAO =====================
class VerificarBateria(No):
    """Condition: le /bateria e reprova abaixo do limite."""

    def __init__(self, no_ros, limite=20.0):
        super().__init__("VerificarBateria")
        self.no_ros = no_ros
        self.limite = limite
        self.nivel = 100.0
        no_ros.create_subscription(Float32, "/bateria", self.cb, 10)

    def cb(self, msg):
        self.nivel = msg.data

    def tick(self):
        if self.nivel < self.limite:
            self.no_ros.get_logger().warn(
                f"{self.nome}: FAILURE  (bateria {self.nivel:.1f})")
            return Estado.FAILURE
        self.no_ros.get_logger().info(
            f"{self.nome}: SUCCESS  (bateria {self.nivel:.1f})")
        return Estado.SUCCESS


class MoverParaPonto(No):
    """Action: publica velocidade e so conclui apos 3 ticks."""

    TICKS_ATE_CONCLUIR = 3

    def __init__(self, no_ros):
        super().__init__("MoverParaPonto")
        self.no_ros = no_ros
        self.contador = 0
        self.pub = no_ros.create_publisher(Twist, "/cmd_vel", 10)

    def tick(self):
        if self.contador < self.TICKS_ATE_CONCLUIR:
            self.contador += 1
            cmd = Twist()
            cmd.linear.x = 0.2
            self.pub.publish(cmd)
            self.no_ros.get_logger().info(
                f"{self.nome}: RUNNING  ({self.contador}"
                f"/{self.TICKS_ATE_CONCLUIR})")
            return Estado.RUNNING

        self.pub.publish(Twist())          # para o robo
        self.no_ros.get_logger().info(f"{self.nome}: SUCCESS")
        return Estado.SUCCESS

    def resetar(self):
        self.contador = 0


# ===================== o no ROS 2 que hospeda a arvore =====================
class ArvoreComportamento(Node):

    def __init__(self):
        super().__init__("arvore_comportamento")

        self.declare_parameter("periodo_tick", 0.5)
        periodo = self.get_parameter("periodo_tick").value

        self.mover = MoverParaPonto(self)
        self.raiz = Sequence("Raiz", [VerificarBateria(self), self.mover])

        self.create_timer(periodo, self.tick_arvore)
        self.get_logger().info(
            f"Arvore no ar. Tick a cada {periodo:.2f} s.")

    def tick_arvore(self):
        st = self.raiz.tick()
        self.get_logger().info(f"--- raiz: {st} ---")
        if st == Estado.FAILURE:
            self.mover.resetar()           # recomeca quando a bateria voltar


def main(args=None):
    rclpy.init(args=args)
    no = ArvoreComportamento()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
