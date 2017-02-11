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
		description = 'Converts an old-style project to a SDK project.'
	)
	return parser
	
def convert_project(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	sdk_data = joinpath(fdirname(__file__), "data")
	pushdir(directory)
	build_extra_data = []
	todos = []
	git_commands = []
	
	MAKEFILE = "Makefile"
	makefile = joinpath(directory, MAKEFILE)
	if fexists(makefile) and not fexists(makefile + ".old"):
		backup_makefile = True
		extra_data = []
		with open(makefile, "rt", encoding="utf-8") as f:
			for line in f:
				if line.strip() == defaults.GENERATED_MAKEFILE.strip():
					backup_makefile = False
					break
				if line.startswith("INSTALL_FILES"):
					__, files = line.split("=")
					for entry in files.split():
						entry = entry.strip()
						if entry and entry not in defaults.BASE_INSTALL_FILES:
							extra_data.append(entry)
		
		if backup_makefile:
			build_extra_data.extend(extra_data)
			print("Making a backup of the Makefile")
			try:
				rename(makefile, makefile + ".old")
				todos.append("If the script builds, remove the Makefile.old file.")
			except FileNotFoundError as e:
				pass
	
	
	METADATA_JSON = "metadata.json"
	metadata_in = "metadata.in.json"
	if fexists(METADATA_JSON) and not fexists(metadata_in):
		print("Renaming %s to %s" % (METADATA_JSON, metadata_in))
		rename(METADATA_JSON, metadata_in)
	
	metadata = readjson(metadata_in)
	metadata_changed = False
	try:
		app_id = metadata["id"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "id" property.')
	try:
		app_name = metadata["name"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "name" property.')
	
	try:
		version_major = metadata["version_major"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "version_major" property.')
	try:
		version_minor = metadata["version_minor"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "version_minor" property.')
	try:
		maintainer_name = metadata["maintainer_name"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "maintainer_name" property.')
	try:
		maintainer_link = metadata["maintainer_link"]
	except KeyError:
		raise ValueError('Error: metadata.json file must contain the "maintainer_link" property.')
	
	try:
		license = metadata["license"]
	except KeyError:
		license = None
		while not license:
			prompt = 'Enter license of your script (e.g. BSD-2-Clause)\n'
			license = input(prompt).strip()
		metadata["license"] = license
		metadata_changed = True
	
	subst = {
		"maintainer_name": maintainer_name,
		"year": datetime.date.today().year,
		"app_id": app_id,
		"app_id_dashed": utils.get_dashed_app_id(app_id),
		"app_name": app_name,
	}
		
	try:
		build = metadata["build"]
	except KeyError:
		metadata["build"] = {k: v for k, v in defaults.BUILD_JSON.items()}
		if build_extra_data:
			metadata["build"]["extra_data"] = build_extra_data
		print("Adding the build section to metadata.in.json")
		metadata_changed = True
	
	if metadata_changed:
		writejson(metadata_in, metadata)
	
	print("Creating new configure script")
	configure = joinpath(directory, "configure")
	fwrite(configure, defaults.CONFIGURE_SCRIPT)
	fchmod(configure, fstat(configure).st_mode|0o111)
	
	F_CHANGELOG_MD = "CHANGELOG.md"
	if not fexists(F_CHANGELOG_MD):
		print("Generating", F_CHANGELOG_MD)
		todos.append("Revise the content of the auto-generated file %s." % F_CHANGELOG_MD)
		changelog = ["%s Change Log" % app_name]
		changelog.append("=" * len(changelog[0]))
		changelog.append("")
		changelog.append("%s.%s - unreleased" % (version_major, version_minor))
		changelog.append("-" * len(changelog[-1]))
		changelog.append("  * Ported to use Nuvola SDK.")
		with open(F_CHANGELOG_MD, "wt", encoding="utf-8") as f:
			f.write("\n".join(changelog) + "\n")
	
	F_CONTRIBUTING_MD = "CONTRIBUTING.md"
	if not fexists(F_CONTRIBUTING_MD):
		print("Generating", F_CONTRIBUTING_MD)
		todos.append("Revise the content of the auto-generated file %s." % F_CONTRIBUTING_MD)
		cp(joinpath(sdk_data, "template", F_CONTRIBUTING_MD), F_CONTRIBUTING_MD)
		dollar_replace(F_CONTRIBUTING_MD, subst)
	
	F_README_MD = "README.md"
	if not fexists(F_README_MD):
		print("Generating", F_README_MD)
		todos.append("Revise the content of the auto-generated file %s." % F_README_MD)
		cp(joinpath(sdk_data, "template", F_README_MD), F_README_MD)
		copyright_details = 'copyright details (Copyright 2014-2016 Johny Bollen <johny@example.net>)'
		
		maintainer_mail = None
		while not maintainer_mail:
			prompt = 'Enter your contact e-mail to be used in %s.' % copyright_details
			prompt += "\n" + " " * (len(prompt) - 20) + "^" * 17 + "\n"
			maintainer_mail = input(prompt).strip()
		subst["maintainer_mail"] = maintainer_mail
		
		copyright_years = None
		while not copyright_years:
			prompt = 'Enter copyright years to be used in %s.' % copyright_details
			prompt += "\n" + " " * (len(prompt) - 44) + "^" * 9 + "\n"
			copyright_years = input(prompt).strip()
		subst["year"] = copyright_years
		
		dollar_replace(F_README_MD, subst)
	
	F_UPDATE_README_MD = "Update.README.md"
	cp(joinpath(sdk_data, F_UPDATE_README_MD), F_UPDATE_README_MD)
	
	D_SRC = "src"
	F_ICON_SVG = joinpath(D_SRC, "icon.svg")
	if isdir(D_SRC) and not isfile(F_ICON_SVG):
		print("The src directory has been renamed to src.old because it doesn't contain icon.svg")
		mv(D_SRC, D_SRC + ".old")
	if not isdir(D_SRC):
		print("Copying generic icons to " + "src")
		cptree(joinpath(sdk_data, "template", "src"), "src")
		git_commands.append("git add " + D_SRC)
		ICONS_COPYRIGHT = """
Copyright
---------

  - `src/icon*.svg`
    + Copyright 2011 Alexander King <alexanderddking@gmail.com>
    + Copyright 2011 Arturo Torres Sánchez <arturo.ilhuitemoc@gmail.com>
    + License: [CC-BY-3.0](./LICENSE-CC-BY.txt)
"""
		fappend(F_UPDATE_README_MD, ICONS_COPYRIGHT)
	
	
	for icon, *sizes in ("icon-sm.svg", 32, 48), ("icon-xs.svg", 16, 22, 24):
		f_icon = joinpath(D_SRC, icon)
		if not isfile(f_icon):
			todos.append("Optimize the '%s' icon for sizes %s." % (f_icon, ", ".join(str(i) for i in sizes)))
			print("Copy the icon %s as %s." % (F_ICON_SVG, f_icon))
			cp(F_ICON_SVG, f_icon)
			git_commands.append("git add " + f_icon)
			
	print("Removing obsolete scripts")
	rmf("svg-convert.sh", "svg-optimize.sh")

	GITIGNORE = ".gitignore"
	try:
		gitignore = fread(GITIGNORE).splitlines()
		if gitignore and not gitignore[-1]:
			del(gitignore[-1])
	except Exception:
		gitignore = []
	
	expected_rules = set(s for s in utils.get_gitignore_for_app_id(app_id).splitlines() if s)
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
	try_run('git add ' + F_CHANGELOG_MD)
	try_run('git add ' + F_CONTRIBUTING_MD)
	try_run('git add ' + F_README_MD)
	try_run('git rm -f --cached Makefile')
	try_run('git rm -f --cached metadata.json')
	try_run('git rm -f --cached svg-convert.sh')
	try_run('git rm -f --cached svg-optimize.sh')
	for cmd in git_commands:
		try_run(cmd)
	
	print("Finished!")
	print("\nTasks to do:\n")
	print("  - Update README.md according to Update.README.md and then remove this template.")
	for todo in todos:
		print("  -", todo)

if __name__ == "__main__":
	convert_project(".")
