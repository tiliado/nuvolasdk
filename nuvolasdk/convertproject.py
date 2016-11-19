"""
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

import argparse

from nuvolasdk.shkit import *
from nuvolasdk import defaults

def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Converts an old-style project to a SDK project.'
	)
	return parser
	
def convert_project(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	sdk_data = joinpath(fdirname(__file__), "data")
	pushdir(directory)
	
	METADATA_JSON = "metadata.json"
	metadata_in = "metadata.in.json"
	if fexists(METADATA_JSON) and not fexists(metadata_in):
		print("Renaming %s to %s" % (METADATA_JSON, metadata_in))
		rename(METADATA_JSON, metadata_in)
	
	metadata = readjson(metadata_in)
	try:
		build = metadata["build"]
	except KeyError:
		metadata["build"] = defaults.BUILD_JSON
		print("Adding the build section to metadata.in.json")
		writejson(metadata_in, metadata)
	
	print("Creating new configure script")
	configure = joinpath(directory, "configure")
	fwrite(configure, defaults.CONFIGURE_SCRIPT)
	fchmod(configure, fstat(configure).st_mode|0o111)
	MAKEFILE = "Makefile"
	makefile = joinpath(directory, MAKEFILE)
	if fexists(makefile) and not fexists(makefile + ".old"):
		print("Making a backup of the Makefile")
		try:
			rename(makefile, makefile + ".old")
		except FileNotFoundError as e:
			pass
	print("Removing obsolete scripts")
	rmf("svg-convert.sh", "svg-optimize.sh")
	
	cp(joinpath(sdk_data, "Update.README.md"), "Update.README.md")
	GITIGNORE = ".gitignore"
	try:
		gitignore = fread(GITIGNORE).splitlines()
		if gitignore and not gitignore[-1]:
			del(gitignore[-1])
	except Exception:
		gitignore = []
	
	expected_rules = set(s for s in defaults.GITIGNORE.splitlines() if s)
	for rule in gitignore:
		expected_rules.discard(rule)
	
	if expected_rules:
		for rule in sorted(expected_rules):
			gitignore.append(rule)
		gitignore.append("")
		print("Updating .gitignore")
		fwrite(GITIGNORE, "\n".join(gitignore))
	
	print("Trying to update git repo")
	try_run('git add metadata.in.json')
	try_run('git add configure')
	try_run('git add .gitignore')
	try_run('git rm -f --cached Makefile')
	try_run('git rm -f --cached metadata.json')
	try_run('git rm -f --cached svg-convert.sh')
	try_run('git rm -f --cached svg-optimize.sh')
	
	print("Finished!")
	print("\nTasks to do:\n")
	print("  - Update README.md according to Update.README.md and the remove this template")
	print("  - Remove Makefile.old if it has been created")

if __name__ == "__main__":
	convert_project(".")
