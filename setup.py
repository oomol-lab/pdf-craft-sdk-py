from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pdf-craft-sdk",
    version="0.4.1",
    description="A Python SDK for PDF Craft API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="User",  # Placeholder
    author_email="user@example.com",  # Placeholder
    url="https://github.com/yourusername/pdf-craft-sdk",  # Placeholder
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
