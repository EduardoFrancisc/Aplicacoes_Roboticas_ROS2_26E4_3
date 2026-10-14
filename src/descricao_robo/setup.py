import os
from glob import glob
from setuptools import setup

package_name = "descricao_robo"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
            ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # ---------------------------------------------------------------
        # Sem estas tres linhas os arquivos ficam so em src/ e o
        # "ros2 launch" falha com:
        #   file 'visualizar.launch.py' was not found in the share directory
        # ---------------------------------------------------------------
        (os.path.join("share", package_name, "urdf"),   glob("urdf/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "rviz"),   glob("rviz/*.rviz")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Mario Pego",
    maintainer_email="mario.pego@prof.infnet.edu.br",
    description="Descricao URDF/XACRO do robo_diff e nos de navegacao basica.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "controlador_turtle = descricao_robo.controlador_turtle:main",
        ],
    },
)
