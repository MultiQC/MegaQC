#!/usr/bin/env python
"""
MegaQC is a web application that collects results from multiple runs of MultiQC and allows bulk visualisation.

See the MultiQC website for installation instructions and documentation: http://multiqc.info/db/

MegaQC was written by Phil Ewels (http://phil.ewels.co.uk) and Denis Moreno at SciLifeLab Sweden (http://www.scilifelab.se)
"""

from setuptools import setup

version = '0.1dev'
dl_version = 'master' if 'dev' in version else 'v{}'.format(version)

try:
    with open("requirements/prod.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

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
    url = 'http://multiqc.info/db',
    download_url = 'https://github.com/MultiQC/MegaQC/tarball/{}'.format(dl_version),
    license = 'GPLv3',
    packages = ['megaqc'],
    include_package_data = True,
    zip_safe = False,
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
