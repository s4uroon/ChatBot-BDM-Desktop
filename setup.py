"""
setup.py
========
Script d'installation pour Chatbot Desktop
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatbot-desktop",
    version="1.0.0",
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="Application desktop professionnelle de chatbot avec PyQt6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votreuser/chatbot-desktop",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.1",
        "PyQt6-WebEngine>=6.6.0",
        "openai>=1.12.0",
        "httpx>=0.26.0",
    ],
    entry_points={
        "console_scripts": [
            "chatbot-desktop=main:main",
        ],
    },
    include_package_data=True,
    keywords="chatbot desktop pyqt6 openai ai assistant gui",
    project_urls={
        "Bug Reports": "https://github.com/votreuser/chatbot-desktop/issues",
        "Source": "https://github.com/votreuser/chatbot-desktop",
    },
)
