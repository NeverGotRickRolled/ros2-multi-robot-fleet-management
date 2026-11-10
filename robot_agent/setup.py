from setuptools import find_packages, setup

package_name = "robot_agent"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Manthan Rasal",
    description="ROS 2 robot-side telemetry and fleet assignment agent.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "robot_agent = robot_agent.robot_agent_node:main",
        ],
    },
)
