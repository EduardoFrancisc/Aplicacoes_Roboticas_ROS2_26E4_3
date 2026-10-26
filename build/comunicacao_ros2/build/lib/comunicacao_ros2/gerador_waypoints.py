#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerador_waypoints.py  -  DR3 / TP2 - Exercicio 4  (no 1 de 4)
Publica a lista de waypoints uma unica vez, com QoS TRANSIENT_LOCAL
para que nos que subirem depois ainda a recebam.

Publica: /waypoints   geometry_msgs/PoseArray
Parametro: waypoints  -> lista plana [x1,y1, x2,y2, x3,y3, ...]
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseArray, Pose


class GeradorWaypoints(Node):

    def __init__(self):
        super().__init__("gerador_waypoints")

        self.declare_parameter("waypoints", [8.0, 8.0, 3.0, 8.0, 3.0, 3.0])
        plana = self.get_parameter("waypoints").value

        if len(plana) % 2 != 0:
            self.get_logger().error("waypoints precisa de pares x,y")
            return

        # latched: quem chegar depois recebe a ultima mensagem
        qos = QoSProfile(depth=1,
                         history=HistoryPolicy.KEEP_LAST,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(PoseArray, "/waypoints", qos)

        msg = PoseArray()
        msg.header.frame_id = "world"
        msg.header.stamp = self.get_clock().now().to_msg()
        for i in range(0, len(plana), 2):
            p = Pose()
            p.position.x = float(plana[i])
            p.position.y = float(plana[i + 1])
            msg.poses.append(p)

        self.pub.publish(msg)
        self.get_logger().info(
            f"{len(msg.poses)} waypoints publicados: " +
            ", ".join(f"({p.position.x:.1f}, {p.position.y:.1f})"
                      for p in msg.poses))


def main(args=None):
    rclpy.init(args=args)
    no = GeradorWaypoints()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
