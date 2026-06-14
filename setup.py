from setuptools import setup, find_packages

setup(
    name="fnos-tunnel",
    version="1.0.0",
    description="fnOS Cloudflare Tunnel SDK for Python",
    author="fnOS",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)