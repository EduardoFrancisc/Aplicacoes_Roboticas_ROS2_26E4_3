#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detector_objetos.py  -  DR3 / TP2 - Exercicio 3
Percepcao por cor: assina a camera, converte com cv_bridge,
segmenta em HSV, extrai contornos e publica os resultados.

Assina:
    /camera/image_raw            sensor_msgs/Image
Publica:
    /objetos_detectados          std_msgs/Int32
    /camera/imagem_processada    sensor_msgs/Image

Execucao:
    ros2 run comunicacao_ros2 detector_objetos
    ros2 run comunicacao_ros2 detector_objetos --ros-args \
         -p h_min:=100 -p h_max:=130          # azul em vez de vermelho
"""

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Int32


class DetectorObjetos(Node):

    def __init__(self):
        super().__init__("detector_objetos")

        # ----- limiares HSV, configuraveis sem recompilar -----
        self.declare_parameter("h_min", 0)      # vermelho: 0..10
        self.declare_parameter("h_max", 10)
        self.declare_parameter("s_min", 120)
        self.declare_parameter("v_min", 70)
        self.declare_parameter("area_min", 300)  # ignora ruido

        self.bridge = CvBridge()

        self.create_subscription(Image, "/camera/image_raw", self.cb_img, 10)
        self.pub_n   = self.create_publisher(Int32, "/objetos_detectados", 10)
        self.pub_img = self.create_publisher(
            Image, "/camera/imagem_processada", 10)

        self.get_logger().info("Detector no ar, aguardando imagens")

    def p(self, nome):
        return self.get_parameter(nome).value

    def cb_img(self, msg):
        # 1) ROS Image -> array NumPy BGR
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:                      # encoding inesperado
            self.get_logger().error(f"cv_bridge falhou: {e}")
            return

        # 2) BGR -> HSV (matiz separada do brilho)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 3) mascara binaria da cor-alvo
        baixo = np.array([self.p("h_min"), self.p("s_min"), self.p("v_min")])
        alto  = np.array([self.p("h_max"), 255, 255])
        mascara = cv2.inRange(hsv, baixo, alto)

        # limpa pontos isolados
        kernel = np.ones((5, 5), np.uint8)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)

        # 4) contornos
        contornos, _ = cv2.findContours(
            mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos = [c for c in contornos
                     if cv2.contourArea(c) >= self.p("area_min")]

        # 5) marca as deteccoes na imagem
        for c in contornos:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(frame, f"objetos: {len(contornos)}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 6) publica os dois resultados
        self.pub_n.publish(Int32(data=len(contornos)))
        saida = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        saida.header = msg.header          # preserva frame_id e timestamp
        self.pub_img.publish(saida)


def main(args=None):
    rclpy.init(args=args)
    no = DetectorObjetos()
    try:
        rclpy.spin(no)
    except KeyboardInterrupt:
        pass
    finally:
        no.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
