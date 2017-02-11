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

import os.path

from nuvolasdk.genmakefile import gen_makefile
from nuvolasdk.convertproject import convert_project
import nuvolasdk.newproject
import nuvolasdk.convertproject
import nuvolasdk.checkproject
import nuvolasdk.datadir
import nuvolasdk.appdata

def print_help(prog):
	print('Help')
	print('====\n')
	print('usage: %s help|-h|--help' % prog)
	print('\nShows this help.\n')
	print('New project')
	print('===========\n')
	nuvolasdk.newproject.create_arg_parser(prog + " new-project").print_help()
	print('\nCheck project')
	print('===============\n')
	nuvolasdk.checkproject.create_arg_parser(prog + " check-project").print_help()
	print('\nConvert project')
	print('===============\n')
	nuvolasdk.convertproject.create_arg_parser(prog + " convert-project").print_help()
	print('\nPrint data dir')
	print('==============\n')
	nuvolasdk.datadir.create_arg_parser(prog + " data-dir").print_help()
	print('\nCreate app data XML')
	print('====================\n')
	nuvolasdk.appdata.create_arg_parser(prog + " create-appdata").print_help()
	
def run(wd, argv):
	prog = os.path.basename(argv[0])
	if prog.startswith("__main__"):
		prog = os.path.basename(os.path.dirname(argv[0]))
	if len(argv) == 1:
		print("Error: Not enough arguments.\n")
		print_help(prog)
		return 1
	cmd = argv[1]
	if cmd == "convert-project":
		convert_project(wd, prog + " " + cmd, argv[2:])
		return 0
	if cmd == "check-project":
		nuvolasdk.checkproject.run(wd, prog + " " + cmd, argv[2:])
		return 0
	if cmd == "new-project":
		nuvolasdk.newproject.new_project(wd, prog + " " + cmd, argv[2:])
		return 0	
	if cmd == "create-appdata":
		nuvolasdk.appdata.run(wd, prog + " " + cmd, argv[2:])
		return 0
	if cmd == "data-dir":
		nuvolasdk.datadir.run(wd, prog + " " + cmd, argv[2:])
		return 0
	if cmd in ('-h', '--help', 'help'):
		print_help(prog)
		return 0
	
	print("Error: Unknown command '%s'.\n" % cmd)
	print_help(prog)
	return 2
