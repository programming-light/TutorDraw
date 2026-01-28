"""
Setup configuration for TutorDraw
"""
from setuptools import setup, find_packages

setup(
    name="tutordraw",
    version="2.0.0",
    description="Professional screen annotation tool with smooth laser pointer",
    author="TutorDraw Team",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.5.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tutordraw=tutorDraw.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
