#!/usr/bin/env python3

from distutils.core import setup

LONG_DESC = """\
SDK for building Nuvola Player's web app scripts
"""

setup(
	name = "nuvolasdk",
	version = "0.0.1",
	author = "Jiří Janoušek",
	author_email = "janousek.jiri@gmail.com",
	url = "https://tiliado.eu/nuvolaplayer/",
	description = "SDK for building Nuvola Player's web app scripts",
	long_description = LONG_DESC,
	packages = ['nuvolasdk'],
	package_data = {'nuvolasdk': ['data/*', 'data/template/*']},
	scripts = ['scripts/nuvolasdk'],
	classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only"
    ]
)
	
