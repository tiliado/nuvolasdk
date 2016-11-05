
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
	print("Unknown command '%s'." % cmd)
	return 1
