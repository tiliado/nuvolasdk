#!/bin/sh
_nuvolasdk="$(dirname $0)/nuvolasdk"
_wd="$PWD"
for dir in "$@"; do
	cd "$_wd"
	cd "$dir"
	echo "=========== Directory: $dir"
	"$_nuvolasdk" check-project
	echo
done
	
