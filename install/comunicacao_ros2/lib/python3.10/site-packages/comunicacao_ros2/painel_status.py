#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
painel_status.py  -  DR3 / TP2 - Exercicio 4  (no 4 de 4)
Exibe o estado geral da missao no log.

Assina  : /status_navegacao (String)
Consome : /status_missao (Trigger), consultado a cada 2 s

E o unico no que nao comanda nada: so observa e informa.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class PainelStatus(Node):

    def __init__(self):
        super().__init__("painel_status")

        self.declare_parameter("periodo", 2.0)

        self.create_subscription(String, "/status_navegacao",
                                 self.cb_status, 10)
        self.cli = self.create_client(Trigger, "/status_missao")
        self.fut = None

        self.create_timer(self.get_parameter("periodo").value, self.consultar)
        self.get_logger().info("Painel no ar")

    def cb_status(self, msg):
        self.get_logger().info(f"[estado] {msg.data}")

    def consultar(self):
        if self.fut is not None:
            if self.fut.done():
                r = self.fut.result()
                marca = "OK " if r.success else "..."
                self.get_logger().info(f"[progresso] {marca} {r.message}")
                self.fut = None
            return
        if not self.cli.service_is_ready():
            return
        self.fut = self.cli.call_async(Trigger.Request())


def main(args=None):
    rclpy.init(args=args)
    no = PainelStatus()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
