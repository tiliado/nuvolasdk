
import os.path

from nuvolasdk.genmakefile import gen_makefile
from nuvolasdk.convertproject import convert_project

def run(wd, argv):
	if len(argv) == 1:
		print("Not enough arguments")
		return 1
	cmd = argv[1]
	if cmd == "convert-project":
		convert_project(wd)
		return 0
	if cmd == "new-project":
		import nuvolasdk.newproject
		nuvolasdk.newproject.new_project(wd, os.path.basename(argv[0]) + " install", argv[2:])
		return 0
	print("Unknown command '%s'." % cmd)
	return 1
