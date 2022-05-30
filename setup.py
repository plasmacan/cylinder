import pathlib

from setuptools import setup

import src.cylinder

# pylint: disable=wrong-spelling-in-comment

# pip install twine
# pip install wheel
# change version in module
# change version below
# git tag version
# rd /s /q dist
# rd /s /q build
# python setup.py sdist bdist_wheel
# twine check dist/*
# twine upload --repository-url https://test.pypi.org/legacy/ dist/* --non-interactive --username xxx --password xxx
# twine upload --repository-url https://upload.pypi.org/legacy/ dist/* --non-interactive --username xxx --password xxx
# pip install --upgrade cylinder

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding="utf-8")

# This call to setup() does all the work
setup(
    name="cylinder",
    version=src.cylinder.__version__,
    description="A web application framework and webserver based on Flask and Waitress",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/plasmacan/cylinder",
    author="Chris Wheeler",
    author_email="cwheeler@tier2.tech",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    py_modules=["cylinder"],
    package_dir={"": "src"},
    include_package_data=False,
    install_requires=["flask", "waitress"],
)
