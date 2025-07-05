from setuptools import setup, find_packages

from src.config import AUTHOR, VERSION

setup(
    name="minecraft-fontgen",
    version=VERSION,
    author=AUTHOR,
    description="A tool to convert Minecraft-style bitmaps into OpenType/TrueType fonts.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Automatically read from requirements.txt
        *open("requirements.txt").read().splitlines()
    ],
    entry_points={
        "console_scripts": [
            "minecraft-fontgen=main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)