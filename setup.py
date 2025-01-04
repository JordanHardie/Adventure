from setuptools import setup, find_packages

setup(
    name="adventure",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'pygame>=2.5.0',
        'noise>=1.2.2',
        'numpy>=1.24.0',
        'scipy>=1.10.0',
    ],
)
