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
        # Both sdk and deferpy
        'pydantic',
        'jinja2',
        'durable-dot-dict>=0.0.20',
        'python-dateutil',
        'requests',

        # For adapters
        'pulsar-client==3.5.0',
        'kafka-python==2.1.5',
        'aiokafka==0.12.0'
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
