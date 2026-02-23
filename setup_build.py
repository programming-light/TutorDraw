"""
Setup configuration for TutorDraw
"""
from setuptools import setup, find_packages
import os

# Read README for long description
long_description = ""
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="tutordraw",
    version="2.1.0",
    author="TutorDraw Team",
    author_email="contact@tutordraw.org",
    description="Professional screen annotation tool with smooth laser pointer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tutordraw/tutordraw",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "Pillow>=8.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "tutordraw=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
