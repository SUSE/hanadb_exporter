"""
Setup script.

:author: xarbulu
:organization: SUSE Linux GmbH
:contact: xarbulu@suse.de

:since: 2018-11-13
"""

import os

from setuptools import find_packages
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

<<<<<<< HEAD
from hanadb_exporter import __version__

=======
import hanadb_exporter
>>>>>>> Update setup.py file

def read(fname):
    """
    Utility function to read the README file. README file is used to create
    the long description.
    """

    return open(os.path.join(os.path.dirname(__file__), fname)).read()

<<<<<<< HEAD
def read_dependencies(fname):
    """
    Read requirements
    """
    requirements = read(fname).splitlines()
    for requirement in requirements:
        # git repository url.
        if requirement.startswith("git+"):
            requirements.remove(requirement)
    return requirements

def read_links(fname):
    """
    Read links
    """
    links = read(fname).splitlines()
    for link in links:
        # git repository url.
        if not link.startswith(("git+", "svn+", "hg+")):
            links.remove(link)
    return links

VERSION = __version__
NAME = "hanadb_exporter"
DESCRIPTION = "SAP HANA database data exporter"
=======
VERSION = hanadb_exporter.__version__
NAME = "hanadb_exporter"
DESCRIPTION = "Prometheus exporter for HANA database"
>>>>>>> Update setup.py file

AUTHOR = "xarbulu"
AUTHOR_EMAIL = "xarbulu@suse.de"
URL = ""

LICENSE = read('LICENSE')

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Natural Language :: English",
    "Operating System :: Unix",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
]

SCRIPTS = ['bin/hanadb_exporter']

DEPENDENCIES = read_dependencies('requirements.txt')
LINKS = read_links('requirements.txt')

PACKAGE_DATA = {}
DATA_FILES = []


SETUP_PARAMS = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    long_description=read('README.md'),
    packages=find_packages(),
    package_data=PACKAGE_DATA,
    license=LICENSE,
    scripts=SCRIPTS,
    data_files=DATA_FILES,
    install_requires=DEPENDENCIES,
    dependency_links=LINKS,
    classifiers=CLASSIFIERS,
)

def main():
    """
    Setup.py main.
    """

    setup(**SETUP_PARAMS)

if __name__ == "__main__":
    main()
