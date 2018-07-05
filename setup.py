#!/usr/bin/env python3

from nuvolasdk import version
from setuptools import setup
import os

version.write_version(os.path.dirname(__file__))

LONG_DESC = """\
SDK for building Nuvola Apps scripts.

Documentation: https://github.com/tiliado/nuvolasdk
"""


pkg_data = []
for root, dirs, files in os.walk('nuvolasdk/data'):
	pkg_data.extend(os.path.join(root, path)[10:] for path in files)

setup(
	name = "nuvolasdk",
	version = version.BASE_VERSION,
	author = "Jiří Janoušek",
	author_email = "janousek.jiri@gmail.com",
	url = "https://github.com/tiliado/nuvolasdk",
	description = "SDK for building Nuvola Apps scripts",
	keywords = 'nuvola sdk development',
	long_description = LONG_DESC,
	license = 'BSD',
	packages = ['nuvolasdk'],
	package_data = {
		'nuvolasdk': pkg_data
	},
	scripts = ['scripts/nuvolasdk'],
	classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only"
    ],
    install_requires=[
        'Pillow >= 4.3.0',
    ],
)

