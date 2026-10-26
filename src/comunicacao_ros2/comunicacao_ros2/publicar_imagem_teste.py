#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publicar_imagem_teste.py  -  DR3 / TP2 - apoio ao Exercicio 3
Publica uma imagem sintetica em /camera/image_raw com N circulos
da cor-alvo. Serve para validar o detector sem camera nem Gazebo.

    ros2 run comunicacao_ros2 publicar_imagem_teste
    ros2 run comunicacao_ros2 publicar_imagem_teste --ros-args -p n_objetos:=3
"""

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class PublicarImagemTeste(Node):

    def __init__(self):
        super().__init__("publicar_imagem_teste")
        self.declare_parameter("n_objetos", 2)
        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, "/camera/image_raw", 10)
        self.create_timer(0.5, self.tick)
        self.get_logger().info("Publicando imagem sintetica a 2 Hz")

    def tick(self):
        n = self.get_parameter("n_objetos").value
        img = np.full((240, 320, 3), 40, dtype=np.uint8)   # fundo escuro
        for i in range(n):
            cx = 60 + i * 90
            cv2.circle(img, (cx, 120), 28, (0, 0, 255), -1)  # BGR vermelho
        msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
        msg.header.frame_id = "camera_link"
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    no = PublicarImagemTeste()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
