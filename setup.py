from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='airembr-sdk',
    version='0.0.1',
    description='Airembr SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    packages=['sdk'],
    install_requires=[
        'pydantic',
        'jinja2',
        'durable-dot-dict>=0.0.21',
        'python-dateutil',
        'requests',
        'airembr-pararun-os',
        'orjson'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['airembr', 'sdk'],
    include_package_data=True,
    python_requires=">=3.10",
)
