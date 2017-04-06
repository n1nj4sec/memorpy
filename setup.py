#!/usr/bin/env python
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2, 5):
    sys.exit("requires python 2.5 and up")
if sys.version_info[0] == 3:
	sys.exit("not compatible python 3")

here = os.path.dirname(__file__)

exec(open(os.path.join(here, 'memorpy', 'version.py')).read())
setup(name = "memorpy",
    version = version_string, #@UndefinedVariable,
    description = "Python library using ctypes to search/edit windows/linux programs memory",
    author = "Nicolas VERDIER",
    author_email = "contact@n1nj4.eu",
    maintainer_email = "contact@n1nj4.eu",
    license = "BSD",
    url = "https://github.com/n1nj4sec/memorpy",
    packages = [
        'memorpy',
    ],
    install_requires = [],
    platforms = ["POSIX", "Windows"],
    use_2to3 = False,
    zip_safe = False,
    long_description = open(os.path.join(here, "README.md"), "r").read(),
)


