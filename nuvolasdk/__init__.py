
import os.path

from nuvolasdk.genmakefile import gen_makefile
from nuvolasdk.convertproject import convert_project
import nuvolasdk.newproject

def print_help(prog):
	print('Help')
	print('====\n')
	print('usage: %s help|-h|--help' % prog)
	print('\nShows this help.\n')
	print('New project')
	print('===========\n')
	nuvolasdk.newproject.create_arg_parser(prog + " new-project").print_help()
	print('\nConvert project')
	print('===============\n')
	nuvolasdk.convertproject.create_arg_parser(prog + " convert-project").print_help()
	
def run(wd, argv):
	prog = os.path.basename(argv[0])
	if len(argv) == 1:
		print("Error: Not enough arguments.\n")
		print_help(prog)
		return 1
	cmd = argv[1]
	if cmd == "convert-project":
		convert_project(wd, prog + " " + cmd, argv[2:])
		return 0
	if cmd == "new-project":
		nuvolasdk.newproject.new_project(wd, prog + " " + cmd, argv[2:])
		return 0	
	if cmd in ('-h', '--help', 'help'):
		print_help(prog)
		return 0
	
	print("Error: Unknown command '%s'.\n" % cmd)
	print_help()
	return 2
