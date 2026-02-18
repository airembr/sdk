from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='airembr_sdk',
    version='0.0.6',
    description='Airembr SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    packages=['airembr'],
    install_requires=[
        'pydantic',
        'jinja2',
        'durable-dot-dict>=0.0.23',
        'python-dateutil',
        'requests',
        'airembr-pararun-os>=0.0.7',
        'orjson',
        'pytz',
        'aiohttp',
        'pytimeparse',
        'pydantic-ai==1.27.0',
        'user-agents==2.2.0',
        'sqlalchemy',
        'msgpack'
        'redis',
        'lark',
        'dateparser',
        'pytz',
        'pytimeparse',
        'instructor'
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
