from setuptools import find_packages, setup

package_name = "fleet_manager"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/fleet_demo.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Manthan Rasal",
    description="ROS 2 multi-robot fleet registry and task allocation prototype.",
    license="MIT",
    entry_points={"console_scripts": [
        "fleet_manager = fleet_manager.fleet_manager_node:main",
    ]},
)
