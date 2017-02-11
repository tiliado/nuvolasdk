"""
shkit.py - Shell Kit - write shell script alternatives easily in Python 3 

Copyright 2014-2016 Jiří Janoušek <janousek.jiri@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import subprocess as _subprocess
import shlex as _shlex
import os as _os
from os.path import (
	expanduser, abspath, join as joinpath, isfile, isdir,
	exists as fexists, basename as fbasename, dirname as fdirname)
from os import unlink, chdir, rename, mkdir, listdir, stat as fstat, chmod as fchmod, rmdir
from shutil import rmtree, copy2 as cp, copytree
from glob import glob
from fnmatch import fnmatch as globmatch
from time import strftime
import re as _re
from pprint import pprint
import json as _json
from collections import OrderedDict

shquote = _shlex.quote
cptree = copytree
mv = rename

def run(command, *, verbose=False):
	if verbose:
		print(">", command)
	argv = _shlex.split(command)
	return _subprocess.check_call(argv)

def try_run(command, *, verbose=False):
	try:
		run(command, verbose=verbose)
		return True
	except Exception:
		return False

def shell(command, *, verbose=False):
	if verbose:
		print(">", command)
	return _subprocess.check_call(command, shell=True)

def runtuple(*args, verbose=False):
	return run(" ".join(args), verbose=verbose)

def getstdout(command, *, verbose=False):
	if verbose:
		print(">", command)
	argv = _shlex.split(command)
	try:
		return _subprocess.check_output(argv, stderr=_subprocess.STDOUT).decode("utf-8")
	except _subprocess.CalledProcessError as e:
		e.output = e.output.decode("utf-8")
		raise e

def fread(path, encoding="utf-8"):
	with open(str(path), "r", encoding=encoding) as f:
		return f.read()

def fwrite(path, text, encoding="utf-8"):
	with open(str(path), "wt", encoding=encoding) as f:
		f.write(text)

def fappend(path, text, encoding="utf-8"):
	with open(str(path), "at", encoding=encoding) as f:
		f.write(text)
	
def rmftree(path):
	if not fexists(path):
		return
	return rmtree(path)

def rmf(*paths):
	for path in paths:
		if fexists(path):
			unlink(path)

def mkdirs(name, exists_ok=True, **kwargs):
	return _os.makedirs(name, exist_ok=exists_ok, **kwargs)

def listfiles(path):
	return [child for child in listdir(path) if isfile(joinpath(path, child))]

def purgedir(path):
	rmftree(path)
	mkdirs(path)

_DOLLAR_REPLACE = _re.compile(r"\$\{([a-zA-Z0-9_]+)\}")
_PERCENT_REPLACE = _re.compile(r"%\{([a-zA-Z0-9_]+)\}")

def file_replace(pattern, path, data):
	with open(path, "r", encoding="utf-8") as f:
		text = f.read()
	
	def replace_func(match):
		key = match.group(1)
		return str(data.get(key))
	
	text = pattern.sub(replace_func, text)
	fwrite(path, text)

def dollar_replace(path, data):
	return file_replace(_DOLLAR_REPLACE, path, data)

def percent_replace(path, data):
	return file_replace(_PERCENT_REPLACE, path, data)

def pwd():
	return abspath(".")

_dirstack = []
def pushdir(path=None):
	abs_path = abspath(path or ".")
	_dirstack.append(abs_path)
	if path:
		chdir(abs_path)

def popdir():
	try:
		chdir(_dirstack.pop())
	except IndexError:
		raise ValueError("No dir on the dir stack")

def readjson(path, **kwargs):
	with open(path, encoding="utf-8") as f:
		return _json.load(f, object_pairs_hook=OrderedDict, **kwargs)

def writejson2(path, data, **kwargs):
	with open(path, "w", encoding="utf-8") as f:
		return _json.dump(data, f, **kwargs)

def writejson(path, data):
	return writejson2(path, data, indent=4, sort_keys=False, separators=(', ', ': '), ensure_ascii=False)
