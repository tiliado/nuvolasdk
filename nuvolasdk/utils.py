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

import re
import unicodedata

from nuvolasdk import defaults
from nuvolasdk import shkit

APP_ID_RE = re.compile("^[a-z0-9]+(?:_[a-z0-9]+)*$")

DESKTOP_CATEGORIES = (
	"AudioVideo", "Audio", "Video", "Development", "Education", "Game",
	"Graphics", "Network", "Office", "Science", "Settings", "System", "Utility"
)

def remove_accents(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def validate_app_id(app_id):
	return bool(APP_ID_RE.match(app_id))

def app_id_from_name(app_name):
	app_id = "_".join(s for s in remove_accents(app_name.strip()).lower().split() if s)
	return app_id if validate_app_id(app_id) else None

def get_dashed_app_id(app_id):
	return app_id.replace("_", "-")

def get_unique_app_id(app_id):
	app_id_unique = ["eu.tiliado.NuvolaApp"]
	for part in app_id.split("_"):
		app_id_unique.append(part[0].upper())
		app_id_unique.append(part[1:].lower())
	return "".join(app_id_unique)	

def get_app_dir_name(app_id):
	return "nuvola-app-" + get_dashed_app_id(app_id)

def get_dbus_launcher_name(app_id):
	return get_app_dir_name(app_id)

def get_desktop_launcher_name(app_id):
	return get_unique_app_id(app_id) + ".desktop"

def get_gitignore_for_app_id(app_id):
	uid = get_unique_app_id(app_id)
	return ''.join((
		defaults.GITIGNORE,
		get_dbus_launcher_name(app_id) + '\n',
		get_desktop_launcher_name(app_id) + '\n',
		uid + '.data.service\n',
		uid + '.appdata.xml\n',
		app_id + '.tar.gz\n'))

def get_license_files():
	return shkit.glob("LICENSE*")

def check_desktop_categories(categories):
	errors = []
	if isinstance(categories, str):
		categories = [c.strip() for c in categories.split(";") if c.strip()]
	if not categories:
		errors.append("Categories field is empty.")
	else:
		audio_video = False
		audio = False
		video = False
		
		for category in categories:
			if category not in DESKTOP_CATEGORIES:
				errors.append('The desktop category "%s" is not valid.' % category)
			elif category == "AudioVideo":
				audio_video = True
			elif category == "Audio":
				audio = True
			elif category == "Video":
				video = True
		
		if audio and not audio_video:
			errors.append('If the desktop category "Audio" is specified, the desktop category AudioVideo must be specified too.')
		if video and not audio_video:
			errors.append('If the desktop category "Video" is specified, the desktop category AudioVideo must be specified too.')
	return errors
		
