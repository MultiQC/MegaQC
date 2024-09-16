#!/usr/bin/env python
"""
MegaQC is a web application that collects results from multiple runs of MultiQC and
allows bulk visualisation.

See the MegaQC website for installation instructions and documentation:
https://megaqc.info

MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and Denis Moreno at
SciLifeLab Sweden (
http://www.scilifelab.se)
  : https: //megaqc.info  MegaQC was written by Phil Ewels ( http://phil.ewels.co.uk)  :
https:
 //megaqc.info  MegaQC was written by Phil Ewels ( http://phil.ewels.co.uk)  : https:
//megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
  : https: //megaqc.info  MegaQC was written by Phil Ewels ( http://phil.ewels.co.uk) :
https:
 //megaqc.info  MegaQC was written by Phil Ewels ( http://phil.ewels.co.uk) : https:
//megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
 : https: //megaqc.info  MegaQC was written by Phil Ewels ( http://phil.ewels.co.uk) :
https:
 //megaqc.info  MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and Denis
Moreno at SciLifeLab Sweden (
http://www.scilifelab.se)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (
http://phil.ewels.co.uk)
: https: //megaqc.info  MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and
Denis Moreno at SciLifeLab Sweden (http://www.scilifelab.se) and extended by Michael
Milton, Tor Solli- Nowlan and Lukas Heumos.
"""

from setuptools import setup

setup(
    name="megaqc",
    version="0.3.0",
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
    download_url="https://github.com/MultiQC/MegaQC/releases",
    license="GPLv3",
    packages=["megaqc"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "megaqc = megaqc.cli:main",
        ],
    },
    install_requires=[
        "argon2-cffi~=20.1",
        "click~=7.0",
        "Flask-APScheduler~=1.11",
        "Flask-Caching~=1.9",
        "Flask-DebugToolbar~=0.11",
        "Flask-Login~=0.5",
        "Flask-SQLAlchemy~=2.4",
        "Flask-WTF~=0.14",
        "Flask~=1.1",
        "future~=0.18",
        "itsdangerous~=1.1",
        "Jinja2~=2.11",
        "markdown~=3.3",
        "multiqc~=1.9",
        "numpy~=1.14",
        "passlib~=1.7",
        "plotly>=2,<5",
        "pyyaml~=5.1",
        "SQLAlchemy~=1.1",
        "Werkzeug>=0.14,<2.0",
        "WTForms[email]~=2.1",
        "flask_restful~=0.3",
        "flask-marshmallow~=0.10",
        "marshmallow~=3.0",
        "marshmallow-sqlalchemy>=0.17,<0.26",
        "flask-uploads~=0.2",
        "marshmallow-jsonapi~=0.23",
        "outlier-utils~=0.0.3",
        "webargs~=5.5",  # do not upgrade, since it breaks parsing
        "querystring-parser~=1.2",
        "scipy~=1.5",
        "flatten_json~=0.1",
        "flapison~=0.30",
        "Flask-Migrate~=2.5",
        "environs~=9.2.0",
        "MarkupSafe<2.1.0",
    ],
    extras_require={
        "dev": [
            # Testing
            "pytest~=7.2",
            "WebTest~=2.0",
            "factory-boy>=2.12,<4.0",
            "livereload~=2.5",
            # Lint and code style
            "flake8>=3.7,<8.0",
            "flake8-blind-except~=0.1",
            "flake8-debugger>=3.1,<5.0",
            "flake8-docstrings~=1.3",
            "isort[pyproject]>=4.3,<6.0",
            "pep8-naming~=0.8",
            "pre-commit",
        ],
        "deploy": ["wheel~=0.30"],
        "prod": [
            "psycopg2~=2.6",
            "gunicorn>=19.7,<21.0",
        ],
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
