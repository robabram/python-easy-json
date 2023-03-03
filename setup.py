#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import os

from setuptools import setup, find_packages

__VERSION__ = "1.0.14"

base_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base_dir, "README.rst")) as readme:
    readme_contents = readme.read()

with open("requirements.txt") as requirements:
    requirements_list = []
    for r in requirements.readlines():
        cleaned = r.split('#')[0].strip()
        if cleaned:
            requirements_list.append(cleaned)

setup(
    # This is what people 'pip install'.
    name="python-easy-json",
    version=__VERSION__,
    description=(
        "A simple, yet powerful, JSON/python dictionary to object deserialization"
    ),
    author="Robert Abram",
    author_email="rabram991@gmail.com",
    long_description=readme_contents,
    url="https://github.com/robabram/python-easy-json",
    packages=find_packages("src", exclude=("tests*", "examples")),
    package_dir={"": "src"},
    license="MIT",
    install_requires=requirements_list,
    zip_safe=False,
    keywords=[
        "serialization",
        "rest",
        "json",
        "api",
        "marshal",
        "marshalling",
        "deserialization",
        "schema",
        "model",
        "models",
        "data"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    test_suite="tests",
    project_urls={
        "Changelog": "https://pypi.python.org/pypi/python-easy-json",
        "Issues": "https://github.com/robabram/python-easy-json/issues"
    },
)