"""
Copyright 2018-2020 Jiří Janoušek <janousek.jiri@gmail.com>

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

import os.path
import subprocess

BASE_VERSION = "4.17.0"
GIT_VERSION_FILE = 'nuvolasdk/git_version_info.py'

def get_git_version(path=None):
	if path is None:
		path = '.'
	if os.path.isdir(os.path.join(path, '.git')):
		try:
			output = subprocess.check_output(["git", "-C", path, "describe", "--tags", "--long"])
			return output.decode("utf-8").strip().split("-")
		except (subprocess.CalledProcessError, FileNotFoundError):
			return None
	return None


def compute_version_from_git(major, minor=0, micro=0, path=None):
	if isinstance(major, str):
		major, minor, micro, *other = [int(x) for x in major.split('.')]
	git_version = get_git_version(path)
	revision = None
	if git_version:
		revision = "%s-%s" % (git_version[1], git_version[2])
		commits = int(git_version[1])
		git_version = [int(i) for i in git_version[0].split(".")]
		while len(git_version) < 3:
			git_version.append(0)
		assert git_version == [major, minor, micro], "Mismatch between metadata version %s and git tag %s." % (
			[major, minor], git_version)
		micro += commits
	elif os.path.isfile(os.path.join(path or '.', GIT_VERSION_FILE)):
		from nuvolasdk.git_version_info import GIT_VERSION_INFO
		return GIT_VERSION_INFO
	return major, minor, micro, revision


VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO, REVISION = compute_version_from_git(
	BASE_VERSION, path=os.path.dirname(os.path.dirname(__file__)))
VERSION = "%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO)
VERSION_FULL = "%s (%s)" % (VERSION, REVISION or 'unknown')


def write_version(root_dir):
	with open(os.path.join(root_dir, GIT_VERSION_FILE), 'w') as f:
		f.write('GIT_VERSION_INFO = %r' % ((VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO, REVISION),))
