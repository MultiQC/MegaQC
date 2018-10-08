#!/usr/bin/env python
"""
MegaQC is a web application that collects results from multiple runs of MultiQC and allows bulk visualisation.

See the MultiQC website for installation instructions and documentation: https://megaqc.info/

MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and Denis Moreno at SciLifeLab Sweden (http://www.scilifelab.se)
"""

import os
from setuptools import setup

version = '0.1dev1'
dl_version = 'master' if 'dev' in version else 'v{}'.format(version)

dev_reqs = [
    # MegaQC
    "argon2-cffi>=16.3.0",
    "click>=5.0",
    "Flask-APScheduler>=1.7.0",
    "Flask-Caching>=1.0.0",
    "Flask-DebugToolbar>=0.10.1",
    "Flask-Login>=0.4.0",
    "Flask-SQLAlchemy==2.2",
    "Flask-WTF==0.14.2",
    "Flask==1.0.2",
    "future==0.16.0",
    "itsdangerous>=0.24",
    "Jinja2>=2.9.5",
    "markdown>=2.6.11",
    "numpy==1.14.3",
    "passlib==1.7.1",
    "plotly==2.0.15",
    "pyyaml==3.12",
    "SQLAlchemy>=1.1.5",
    "Werkzeug==0.14.1",
    "WTForms>=2.1",

    # Testing
    "pytest==3.0.6",
    "WebTest==2.0.26",
    "factory-boy==2.8.1",
    "livereload==2.5.1",

    # Lint and code style
    #"flake8==3.3.0",
    #flake8-blind-except==0.1.1",
    #"flake8-debugger==1.4.0",
    #"flake8-docstrings==1.0.3",
    #"flake8-isort==2.1.3",
    #"flake8-quotes==0.9.0",
    #"isort==4.2.5",
    #"pep8-naming==0.4.1",
]

prod_reqs = dev_reqs + [
    "psycopg2-binary>=2.6.2",
    "gunicorn>=19.7.1",
]
install_requires = prod_reqs if os.environ.get('MEGAQC_PRODUCTION') else dev_reqs


print("""-----------------------------------
 Installing MegaQC version {}
-----------------------------------

""".format(version))

setup(
    name = 'megaqc',
    version = version,
    author = 'Phil Ewels',
    author_email = 'phil.ewels@scilifelab.se',
    description = "Collect and visualise data across multiple MultiQC runs",
    long_description = __doc__,
    keywords = ['bioinformatics', 'biology', 'sequencing', 'NGS', 'next generation sequencing', 'quality control'],
    url = 'https://megaqc.info/',
    download_url = 'https://github.com/ewels/MegaQC/releases',
    license = 'GPLv3',
    packages = ['megaqc'],
    include_package_data = True,
    zip_safe = False,
    scripts = ['scripts/megaqc'],
    install_requires = install_requires,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)

print("""
--------------------------------
 MegaQC installation complete!
--------------------------------
For help in running MultiQC, please see the documentation available
at http://multiqc.info/db
""")
