from setuptools import setup, find_packages

setup(
    name="clanto",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
    ],
    entry_points={
        "console_scripts": [
            "clanto=src.main:main",
        ],
    },
    author="Daniel Ruiz Blanco",
    author_email="druizblancopdecastro@gmail.com",
    description="A Python tool for anonymising sensitive data quick and easily.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/paydos/clanto",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
