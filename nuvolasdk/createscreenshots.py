"""
Copyright 2014-2018 Jiří Janoušek <janousek.jiri@gmail.com>

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
from nuvolasdk import imaging
from nuvolasdk import screenshots
from nuvolasdk import utils

def create_arg_parser(prog):
	parser = argparse.ArgumentParser(
		prog = prog,
		description = 'Creates combined screenshots.'
	)
	parser.add_argument("--kind", help='The kind the app belongs to (e.g. audio, video, other).', type=str)
	parser.add_argument("--fill", help='The fill color for areas not covered by the web view snapshot."', type=str)
	parser.add_argument('-o', "--output-dir", help='The output directory to place screenshots to.', type=str)
	parser.add_argument('-i', "--input", help='The input web view screenshot.', type=str, required=True)
	return parser

def run(directory, prog, argv):
	args = create_arg_parser(prog).parse_args(argv)
	output_dir = abspath(args.output_dir or directory)
	kind = args.kind or screenshots.DEFAULT_KIND
	web_view_screenshot = abspath(args.input)
	screenshots_dir = utils.get_sdk_data_dir('screenshots')
	mkdirs(output_dir)
	for base, bounds, fill, _caption in screenshots.BASE_SCREENSHOTS[kind]:
		input_path = joinpath(screenshots_dir, base)
		output_path = joinpath(output_dir, base)
		print("'%s' → '%s'" % (input_path, output_path))
		img = imaging.combine_images(input_path, web_view_screenshot, bounds, args.fill or fill)
		img.save(output_path, 'PNG', optimize=True)

	path = joinpath(output_dir, defaults.SCREENSHOTS_DIR_TIMESTAMP)
	print("Timestamp file: '%s'" % path)
	fwrite(path, datetime.datetime.now().isoformat())
	return 0
