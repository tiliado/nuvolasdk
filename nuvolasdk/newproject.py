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
import datetime

from nuvolasdk.shkit import *
from nuvolasdk import defaults
from nuvolasdk import utils

def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Creates a new web app script project.'
	)
	parser.add_argument("--id", help='Id of the web app script, e.g. "google_play_music"', type=str)
	parser.add_argument("--name", help='Name of the web app, e.g. "Google Play Music"', type=str)
	parser.add_argument("--url", help='URL of the main page of the web app, e.g. "https://deezer.com"', type=str)
	parser.add_argument("--maintainer-name", help='Name of the maintainer, e.g. "John Doe"', type=str)
	parser.add_argument("--maintainer-mail", help='Email of the maintainer, e.g. "john@doe.com"', type=str)
	parser.add_argument("--maintainer-github", help='Github profile of the maintainer, e.g. "john.doe"', type=str)
	return parser

def new_project(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	
	app_name = args.name.strip() if args.name else None
	while not app_name:
		try:
			app_name = input('Type name of the script,  e.g. "Google Play Music". Or press Ctrl-C to abort.\n').strip()
		except KeyboardInterrupt:
			return
	
	app_id = args.id.strip() if args.id else None
	if app_id and not utils.validate_app_id(app_id):
		print('Error: App id "%s" is not valid.' % app_id)
		app_id = None
	
	default_app_id = utils.app_id_from_name(app_name)
	while not app_id:
		try:
			if default_app_id:
				app_id = input('The automatically generated app id is "%s". Press Enter to accept it or type your own app id, e.g. "google_play_music". Or press Ctrl-C to abort.\n' % default_app_id).strip()
				if not app_id:
					app_id = default_app_id
					break
			else:
				app_id = input('Type app id, e.g. "google_play_music". Or press Ctrl-C to abort.\n').strip()
			if not utils.validate_app_id(app_id):
				print('Error: App id "%s" is not valid.' % app_id)
				app_id = None 
		except KeyboardInterrupt:
			return 1
	
	app_url = args.url.strip() if args.url else None
	while not app_url:
		try:
			app_url = input('Type URL of the main page of the web app, e.g. "https://deezer.com". Or press Ctrl-C to abort.\n').strip()
		except KeyboardInterrupt:
			return 1
			
	maintainer_name = args.maintainer_name.strip() if args.maintainer_name else None
	while not maintainer_name:
		try:
			maintainer_name = input('Type name of the maintainer, e.g. "John Doe". Or press Ctrl-C to abort.\n').strip()
		except KeyboardInterrupt:
			return 1
	
	maintainer_mail = args.maintainer_mail.strip() if args.maintainer_mail else None
	while not maintainer_mail:
		try:
			maintainer_mail = input('Type email of the maintainer, e.g. "john@doe.com". Or press Ctrl-C to abort.\n').strip()
		except KeyboardInterrupt:
			return 1
	
	maintainer_github = args.maintainer_github.strip() if args.maintainer_github else None
	while not maintainer_github:
		try:
			maintainer_github = input('Type Github profile of the maintainer, e.g. "john.doe". Or press Ctrl-C to skip.\n').strip()
		except KeyboardInterrupt:
			maintainer_github = 'FIXME'
			print("")
			break
		
	sdk_data = joinpath(fdirname(__file__), "data")
	app_dir_name = utils.get_app_dir_name(app_id)
	top_dir = joinpath(directory, app_dir_name)
	
	
	try:
		mkdirs(top_dir, False)
	except FileExistsError:
		print('Error: The directory "%s" already exists.' % top_dir)
		return 2
	
	rmdir(top_dir)
	print("Copying a template to " + top_dir)
	cptree(joinpath(sdk_data, "template"), top_dir)
	pushdir()
	pushdir(top_dir)
	
	F_GITIGNORE = ".gitignore"
	F_README_MD = "README.md"
	F_METADATA_IN_JSON = "metadata.in.json"
	F_CONFIGURE = "configure"
	F_INTEGRATE_JS = "integrate.js"
	F_CONTRIBUTING_MD = "CONTRIBUTING.md"
	F_CHANGELOG_MD = "CHANGELOG.md"
	new_files = [F_GITIGNORE, F_METADATA_IN_JSON, F_CONFIGURE]
	print("Creating files", *new_files)
	fwrite(F_GITIGNORE, utils.get_gitignore_for_app_id(app_id))
	metadata = defaults.METADATA_IN_JSON.copy()
	metadata["id"] = app_id
	metadata["name"] = app_name
	metadata["maintainer_name"] = maintainer_name
	metadata["maintainer_link"] = "https://github.com/" + maintainer_github
	metadata["home_url"] = app_url
	writejson(F_METADATA_IN_JSON, metadata)
	fwrite(F_CONFIGURE, defaults.CONFIGURE_SCRIPT)
	fchmod(F_CONFIGURE, fstat(F_CONFIGURE).st_mode|0o111)
	
	subst = {
		"maintainer_name": maintainer_name,
		"maintainer_mail": maintainer_mail,
		"year": datetime.date.today().year,
		"app_id": app_id,
		"app_id_dashed": utils.get_dashed_app_id(app_id),
		"app_name": app_name,
	}
	for path in F_INTEGRATE_JS, F_CHANGELOG_MD, F_README_MD, F_CONTRIBUTING_MD:
		print("Expanding variables in", path)
		dollar_replace(path, subst)
	
	print("Trying to init git repo")
	ok = try_run('git init')
	
	for name in new_files + ["src", F_INTEGRATE_JS, F_README_MD, F_CONTRIBUTING_MD, F_CHANGELOG_MD, "LICENSE*"]:
		if not try_run('git add -v ' + name):
			ok = False
	if ok:
		try_run('git commit -v -m "Initial commit"')
	print("Finished!\n")
	popdir()
	popdir()
	print(top_dir)
	run('ls -la "%s"' % top_dir)
	return 0
