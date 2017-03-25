"""
Copyright 2016-2017 Jiří Janoušek <janousek.jiri@gmail.com>

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
import sys

from nuvolasdk import licenses
from nuvolasdk import screenshots
from nuvolasdk import utils
from nuvolasdk import xmltree
from nuvolasdk.shkit import *


DESCRIPTION = """
Nuvola is a runtime for semi-sandboxed web apps providing more native user experience and tighter
integration with Linux desktop environments than usual web browsers can offer. It tries to feel and look
like a native application as much as possible.
Nuvola mostly specializes on music streaming web apps (e.g. Google Play Music, Spotify, Amazon Music, Deezer,
and more), but progress is being made to support generic web apps (e.g. Google Calendar, Google Keep, etc.).

Features of Nuvola: desktop launchers, integration with media applets (e.g. in GNOME Shell and Ubuntu sound menu),
Unity launcher quick list actions, lyrics fetching, Last.fm audio scrobbler, tray icon, desktop notifications,
media keys binding, password manager, remote control over HTTP and more. Some features may be availably only to
users with premium or patron plans available at https://tiliado.eu/nuvolaplayer/funding/

Users of the official Flatpak builds available at https://nuvola.tiliado.eu are eligible for user support
free of charge. Users of third-party build should contact the customer care of their distributor or order
paid support provided by the Nuvola developer.
"""


def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Creates AppStream AppData XML file.'
	)
	parser.add_argument("-m", "--meta", help='Path to a metadata.json file', default="metadata.json", type=str)
	parser.add_argument("-o", "--output", help='Path to an output file', default=None, type=str)
	return parser


def run(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	meta = readjson(joinpath(directory, args.meta))
	output = args.output
	xml = create_app_data_xml(meta)
	if output:
		fwrite(joinpath(directory, output), xml)
	else:
		sys.stdout.write(xml)


def create_app_data_xml(meta):
	app_id = meta["id"]
	uid = utils.get_unique_app_id(app_id)
	dbus_launcher = utils.get_dbus_launcher_name(app_id)
	
	tree = xmltree.TreeBuilder()
	with tree("component", type="desktop"):
		tree.add("id", uid + ".desktop")
		tree.add("metadata_license", "CC0-1.0")
		tree.add("project_license", licenses.get_spdx_expression(meta["license"], ignore_unknown=True))
		tree.add("name", "%s (Nuvola app)" % meta["name"])
		tree.add("summary", "%s - Sandboxed web application" % meta["name"])
		with tree("description"):
			tree.add("p", "%s (Nuvola app) is a semi-sandboxed web application running in the Nuvola Apps runtime." % meta["name"])
			for para in DESCRIPTION.strip().split("\n\n"):
				tree.add("p", para)
		with tree("screenshots"):
			for i, (url, caption) in enumerate(screenshots.SCREENSHOTS):
				args = {"type": "default"} if i == 0 else {} 
				with tree("screenshot", **args):
					tree.add("image", url)
					tree.add("caption", caption)
		tree.add("url", "https://tiliado.eu/nuvolaplayer/", type="homepage")
		tree.add("url", "https://github.com/tiliado/nuvolaplayer/wiki/Bug-Reporting-Guidelines", type="bugtracker")
		tree.add("url", "https://tiliado.github.io/nuvolaplayer/documentation/3.1/explore.html", type="help")
		tree.add("url", "https://tiliado.eu/nuvolaplayer/funding/", type="donation")
		
		tree.add("developer_name", meta["maintainer_name"])
		tree.add("updatecontact", "janousek.jiri@gmail.com")
		with tree("provides"):
			tree.add("dbus", uid, type="user")
			if meta.get("has_dbus_launcher"):
				tree.add("binary", dbus_launcher)
	return tree.dump()
