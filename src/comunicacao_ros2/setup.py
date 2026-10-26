import os
from glob import glob
from setuptools import setup

package_name = "comunicacao_ros2"

setup(
    name=package_name,
    version="0.0.2",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
            ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Mario Pego",
    maintainer_email="mario.pego@prof.infnet.edu.br",
    description="Comunicacao ROS 2, behavior tree, percepcao e navegacao 2D.",
    license="MIT",
    entry_points={
        "console_scripts": [
            # ---- TP2 Exercicio 2 ----
            "arvore_comportamento = comunicacao_ros2.arvore_comportamento:main",
            # ---- TP2 Exercicio 3 ----
            "detector_objetos = comunicacao_ros2.detector_objetos:main",
            "publicar_imagem_teste = comunicacao_ros2.publicar_imagem_teste:main",
            # ---- TP2 Exercicio 4 ----
            "gerador_waypoints = comunicacao_ros2.gerador_waypoints:main",
            "controlador_navegacao = comunicacao_ros2.controlador_navegacao:main",
            "monitor_progresso = comunicacao_ros2.monitor_progresso:main",
            "painel_status = comunicacao_ros2.painel_status:main",
        ],
    },
)
