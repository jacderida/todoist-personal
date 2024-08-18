import pkg_resources
from setuptools import setup, find_packages

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name="todoist-personal",
    version="0.3.3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "todoist = todoist.main:main",
        ],
    },
    install_requires=[
        str(requirement) for requirement in pkg_resources.parse_requirements(requirements)
    ],
)
