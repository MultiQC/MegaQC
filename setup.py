#!/usr/bin/env python
"""
MegaQC is a web application that collects results from multiple runs of MultiQC
and allows bulk visualisation.

See the MultiQC website for installation instructions and documentation: https://megaqc.info/

MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and Denis Moreno at SciLifeLab Sweden (http://www.scilifelab.se)
"""

from setuptools import setup

setup(
    name="megaqc",
    version="0.2.0",
    author="Phil Ewels",
    author_email="phil.ewels@scilifelab.se",
    description="Collect and visualise data across multiple MultiQC runs",
    long_description=__doc__,
    keywords=[
        "bioinformatics",
        "biology",
        "sequencing",
        "NGS",
        "next generation sequencing",
        "quality control",
    ],
    url="https://megaqc.info/",
    download_url="https://github.com/ewels/MegaQC/releases",
    license="GPLv3",
    packages=["megaqc"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["megaqc = megaqc.cli:main",],},
    install_requires=[
        "argon2-cffi~=16.3",
        "click~=5.0",
        "Flask-APScheduler~=1.7",
        "Flask-Caching~=1.0",
        "Flask-DebugToolbar~=0.10",
        "Flask-Login~=0.5",
        "Flask-SQLAlchemy~=2.2",
        "Flask-WTF~=0.14",
        "Flask~=1.0",
        "future~=0.16",
        "itsdangerous~=0.24",
        "Jinja2~=2.9",
        "markdown~=2.6",
        "multiqc~=1.3",
        "numpy~=1.14",
        "passlib~=1.7",
        "plotly~=2.0",
        "pyyaml~=5.1",
        "SQLAlchemy~=1.1",
        "Werkzeug~=0.14",
        "WTForms[email]~=2.1",
        "flask_restful~=0.3",
        "flask-marshmallow~=0.10",
        "marshmallow~=3.0",
        "marshmallow-sqlalchemy~=0.17",
        "flask-uploads~=0.2",
        "marshmallow-jsonapi~=0.21",
        "outlier-utils~=0.0.3",
        "webargs~=5.5",
        "querystring-parser~=1.2",
        "scipy~=1.3",
        "flatten_json~=0.1",
        "flapison~=0.30",
        "Flask-Migrate~=2.5",
    ],
    extras_require={
        "dev": [
            # Testing
            "pytest~=3.0",
            "WebTest~=2.0",
            "factory-boy~=2.12",
            "livereload~=2.5",
            # Lint and code style
            "flake8~=3.7",
            "flake8-blind-except~=0.1",
            "flake8-debugger~=3.1",
            "flake8-docstrings~=1.3",
            "isort[pyproject]~=4.3",
            "pep8-naming~=0.8",
            "pre-commit",
        ],
        "deploy": ["wheel~=0.30"],
        "prod": ["psycopg2~=2.6", "gunicorn~=19.7",],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
