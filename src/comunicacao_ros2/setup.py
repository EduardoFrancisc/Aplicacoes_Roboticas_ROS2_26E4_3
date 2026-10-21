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
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Mario Pego",
    maintainer_email="mario.pego@prof.infnet.edu.br",
    description="Comunicacao ROS 2 e behavior tree (DR3 / TP2 Ex.2).",
    license="MIT",
    entry_points={
        "console_scripts": [
            # ---- TP2 Exercicio 2 ----
            "arvore_comportamento = comunicacao_ros2.arvore_comportamento:main",
        ],
    },
)
