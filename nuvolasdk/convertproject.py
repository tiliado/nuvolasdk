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

from nuvolasdk.shkit import *
from nuvolasdk.defaults import BUILD_JSON

def convert_project(directory):
	sdk_data = joinpath(fdirname(__file__), "data")
	pushdir(directory)
	
	metadata = "metadata.json"
	metadata_in = "metadata.in.json"
	if fexists(metadata) and not fexists(metadata_in):
		print("Renaming %s to %s" % (metadata, metadata_in))
		rename(metadata, metadata_in)
	
	metadata = readjson(metadata_in)
	try:
		build = metadata["build"]
	except KeyError:
		metadata["build"] = BUILD_JSON
		print("Adding the build section to metadata.in.json")
		writejson(metadata_in, metadata)
	
	print("Creating new configure script")
	configure = joinpath(directory, "configure")
	fwrite(configure, "#!/usr/bin/env python3\nimport nuvolasdk\nnuvolasdk.gen_makefile()\n")
	fchmod(configure, fstat(configure).st_mode|0o111)
	makefile = joinpath(directory, "Makefile")
	if fexists(makefile) and not fexists(makefile + ".old"):
		print("Making a backup of the Makefile")
		try:
			rename(makefile, makefile + ".old")
		except FileNotFoundError as e:
			pass
	print("Removing obsolete scripts")
	rmf("svg-convert.sh", "svg-optimize.sh")
	print("Don't forget to update README.md. See file Update.README.md for details.")
	cp(joinpath(sdk_data, "Update.README.md"), "Update.README.md")
	print("Finished!")

if __name__ == "__main__":
	convert_project(".")
