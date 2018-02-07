"""
Copyright 2016-2018 Jiří Janoušek <janousek.jiri@gmail.com>

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
from nuvolasdk import utils
from nuvolasdk import xmltree
from nuvolasdk.shkit import *


def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Creates AppStream AddonData XML file.'
	)
	parser.add_argument("-m", "--meta", help='Path to a metadata.json file', default="metadata.json", type=str)
	parser.add_argument("-o", "--output", help='Path to an output file', default=None, type=str)
	parser.add_argument("--genuine", help='Genuine build.', default=False, action='store_true')
	return parser


def run(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	meta = readjson(joinpath(directory, args.meta))
	output = args.output
	xml = create_addon_data_xml(meta, args.genuine)
	if output:
		fwrite(joinpath(directory, output), xml)
	else:
		sys.stdout.write(xml)


def create_addon_data_xml(meta, genuine):
	app_id = meta["id"]
	dashed_id = utils.get_dashed_app_id(app_id)
	tree = xmltree.TreeBuilder()
	with tree("component", type="addon"):
		tree.add("id", "nuvola-app-" + dashed_id)
		tree.add("extends", utils.get_nuvola_unique_id(genuine) + ".desktop")
		tree.add("metadata_license", "CC0-1.0")
		tree.add("project_license", licenses.get_spdx_expression(meta["license"], ignore_unknown=True))
		tree.add("name", meta["name"])
		tree.add("summary", "%s running in Web Apps Runtime." % meta["name"])
		tree.add("url", "https://tiliado.eu/nuvolaplayer/", type="homepage")
		tree.add("url", "https://github.com/tiliado/nuvolaplayer/wiki/Bug-Reporting-Guidelines", type="bugtracker")
		tree.add("updatecontact", "janousek.jiri@gmail.com")
	return tree.dump()
