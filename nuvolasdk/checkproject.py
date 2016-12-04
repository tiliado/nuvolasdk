"""
Copyright 2016 Jiří Janoušek <janousek.jiri@gmail.com>

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
from nuvolasdk import utils

def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Check whether the project is well-formed.'
	)
	return parser

def run(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	sdk_data = joinpath(fdirname(__file__), "data")
	pushdir(directory)
	n_errors = 0
	
	if fexists("Makefile"):
		print("Cleaning the project...")
		try_run('make clean')
		print("")
	
	print("Checking the project...")
	
	F_METADATA_IN_JSON = "metadata.in.json"
	F_CONFIGURE = "configure"
	F_CHANGELOG_MD = "CHANGELOG.md"
	F_README_MD = "README.md"
	F_CONTRIBUTING_MD = "CONTRIBUTING.md"
	F_INTEGRATE_JS = "integrate.js"
	F_GITIGNORE = ".gitignore"
	
	files = (
		F_METADATA_IN_JSON, F_INTEGRATE_JS, F_CONFIGURE,
		F_CHANGELOG_MD, F_README_MD, F_CONTRIBUTING_MD, F_GITIGNORE
	)
	
	for filename in files:
		if not fexists(filename):
			print("Error: A file '%s' is missing." % filename)
			n_errors += 1
	
	if not utils.get_license_files():
		print("Error: No license files (LICENSE*) have been found.")
		n_errors += 1
	
	METADATA_JSON = "metadata.json"
	if fexists(F_METADATA_IN_JSON):
		metadata = readjson(F_METADATA_IN_JSON)
		try:
			app_id = metadata["id"]
			if not utils.validate_app_id(app_id):
				print('Error: metadata.json file contains invalid "id" property: "%s"' % app_id)
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "id" property.')
			n_errors += 1
		
		try:
			app_name = metadata["name"].strip()
			if not app_name:
				print('Error: metadata.json file contains invalid "name" property: "%s"' % app_name)
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "name" property.')
			n_errors += 1
		
		prop_name = "version_major"
		try:
			version_major = metadata[prop_name]
			if not isinstance(version_major, int) or version_major < 1:
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, version_major))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
		
		prop_name = "version_minor"
		try:
			version_minor = metadata[prop_name]
			if not isinstance(version_minor, int) or version_minor < 0:
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, version_minor))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
		
		prop_name = "api_major"
		try:
			api_major = metadata[prop_name]
			if not isinstance(api_major, int) or api_major < 3:
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, api_major))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
		
		prop_name = "api_minor"
		try:
			api_minor = metadata[prop_name]
			if not isinstance(api_minor, int) or api_minor < 0:
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, api_minor))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
		
		prop_name = "maintainer_link"
		try:
			maintainer_link = metadata[prop_name]
			if not maintainer_link.strip() or not maintainer_link.startswith("https://github.com/"):
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, maintainer_link))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
			
		prop_name = "maintainer_name"
		try:
			maintainer_name = metadata[prop_name]
			if not maintainer_name.strip():
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, maintainer_name))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
			
		prop_name = "license"
		try:
			license = metadata[prop_name]
			if not license.strip():
				print('Error: metadata.json file contains invalid "%s" property: "%s"' % (prop_name, license))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % prop_name)
			n_errors += 1
		
		prop_name = "categories"
		try:
			categories = metadata[prop_name]
			for err in utils.check_desktop_categories(categories):
				print('Error: metadata.json file contains invalid "%s" property: %s' % (prop_name, err))
				n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "%s" property.' % categories)
			n_errors += 1
		
		
		
		try:
			build = metadata["build"]
			try:
				for icon in build["icons"]:
					path, *sizes = icon.split(' ')
					if not fexists(path):
						print('Error: Icon "%s" does not exist.' % path)
						n_errors += 1
					for size in sizes:
						size = size.strip()
						if size.lower() != "scalable":
							try:
								int(size)
							except ValueError:
								print('Error: Invalid icon size "%s".' % size)
								n_errors += 1
			except KeyError:
				print('Error: metadata.json file must contain the build.icons property.')
				n_errors += 1
			for pattern in build.get("extra_data", []):
				files = glob(pattern)
				if not files:
					print('Error: metadata.json - build - extra_data pattern "%s" does not match any files.' % pattern)
					n_errors += 1
		except KeyError:
			print('Error: metadata.json file must contain the "build" property.')
			n_errors += 1
	
	
	if n_errors > 0:
		print("\n-----------------------------------------------------\n%s errors have been found." % n_errors)
		return 2
	
	print("No errors have been found.")
	return 0
	
