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

import sys
from nuvolasdk.shkit import *
from nuvolasdk import defaults
from nuvolasdk import utils

def gen_makefile():
	prefix = "/usr/local"
	dbus_launcher = False
	desktop_launcher = False
	flatpak_build = False
	create_appdata = False
	metadata = readjson("metadata.in.json")
	build_json = metadata.get("build", {})
	
	for arg in sys.argv[1:]:
		try:
			name, value = arg.split("=", 1)
		except ValueError:
			name = arg
			value=None
		if name == "--libdir":
			pass
		elif name == "--prefix":
			prefix = value
		elif name in ("CFLAGS", "CXXFLAGS"):
			pass
		elif name == "--with-dbus-launcher":
			dbus_launcher = True
		elif name == "--with-appdata-xml":
			create_appdata = True
		elif name == "--with-desktop-launcher":
			desktop_launcher = True
		elif name == "--flatpak-build":
			flatpak_build = True
		else:
			print("Warning: Unknown option: ", arg)
	
	if flatpak_build:
		dbus_launcher = True
		desktop_launcher = True
		create_appdata = True
	
	app_id = metadata["id"]
	app_name = metadata["name"]
	app_id_dashed = utils.get_dashed_app_id(app_id)
	app_id_unique = utils.get_unique_app_id(app_id)
	
	sdk_data = joinpath(fdirname(__file__), "data")
	
	all_files = defaults.BASE_INSTALL_FILES[:]
	all_files.extend(utils.get_license_files())
	for entry in build_json.get("extra_data", []):
		all_files.extend(glob(entry))
	
	files = ' '.join(all_files)
	flatpak_archive = all_files[:]
	
	install = [
		'install: all\n',
	]
	uninstall = [
		'uninstall:\n',
		'\trm -rfv $(APP_DIR)\n'
	]
	
	if not flatpak_build:
		install.extend([
		'\tinstall -vCd $(APP_DIR)/$(ICONS_DIR)\n',
		'\tcp -v -t $(APP_DIR) $(FILES)\n',
		])
	
	if dbus_launcher:
		dbus_launcher_cmd = 'nuvola-app-$(APP_ID_DASHED)'
		all_files.append(dbus_launcher_cmd)
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(PREFIX)/bin\n',
			'\tinstall -vC -t $(DESTDIR)$(PREFIX)/bin %s\n' % dbus_launcher_cmd,
		))
		uninstall.append('\trm -fv $(DESTDIR)$(PREFIX)/bin/%s\n' % dbus_launcher_cmd)
	else:
		dbus_launcher_cmd = None
	
	if flatpak_build:
		all_files.append('$(APP_ID_UNIQUE).data.service')
		all_files.append('$(APP_ID).tar.gz')
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(PREFIX)/share/dbus-1/services\n',
			'\tcp -vf -t $(DESTDIR)$(PREFIX)/share/dbus-1/services $(APP_ID_UNIQUE).data.service\n',
			'\tmkdir -p $(WEB_APPS)\n',
			'\tcp -vf -t $(WEB_APPS) $(APP_ID).tar.gz\n',
		))
		uninstall.append('\trm -fv $(DESTDIR)$(PREFIX)/share/dbus-1/services/$(APP_ID_UNIQUE).data.service\n')
		uninstall.append('\trm -fv $(WEB_APPS)/$(APP_ID).tar.gz\n')
	if desktop_launcher:
		all_files.append('$(APP_ID_UNIQUE).desktop')
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(PREFIX)/share/applications\n',
			'\tcp -vf -t $(DESTDIR)$(PREFIX)/share/applications $(APP_ID_UNIQUE).desktop\n',
		))
		uninstall.append('\trm -fv $(DESTDIR)$(PREFIX)/share/applications/$(APP_ID_UNIQUE).desktop\n')
	
	if create_appdata:
		all_files.append('$(APP_ID_UNIQUE).appdata.xml')
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(PREFIX)/share/metainfo\n',
			'\tcp -vf -t $(DESTDIR)$(PREFIX)/share/metainfo $(APP_ID_UNIQUE).appdata.xml\n',
			'\tinstall -vCd $(DESTDIR)$(PREFIX)/share/appdata\n',
			'\tcp -vf -t $(DESTDIR)$(PREFIX)/share/appdata $(APP_ID_UNIQUE).appdata.xml\n',
		))
		uninstall.append('\trm -fv $(DESTDIR)$(PREFIX)/share/metainfo/$(APP_ID_UNIQUE).appdata.xml\n')
		uninstall.append('\trm -fv $(DESTDIR)$(PREFIX)/share/appdata/$(APP_ID_UNIQUE).appdata.xml\n')
		
	icons_spec = build_json.get("icons", defaults.BUILD_JSON["icons"])
	icons = [
		'$(ICONS_DIR):\n',
		'\tmkdir -p $@\n'
		'$(ICONS_DIR)/%.svg: src/%.svg | $(ICONS_DIR)\n',
		'\tsh $(NUVOLA_SDK_DATA)/svg-optimize.sh $< $@\n'
		]

	for icon in icons_spec:
		path, *sizes = icon.split(' ')
		for size in sizes:
			if size.upper() == "SCALABLE":
				src = '$(ICONS_DIR)/' + fbasename(path)
				dest = "$(ICONS_DIR)/scalable.svg"
				icons.append('%s : %s | $(ICONS_DIR)\n\tcp -v $< $@\n' % (dest, src))
				install.append('\tmkdir -pv $(HICOLOR_DIR)/scalable/apps || true\n')
				install.append('\tcp -v %s $(HICOLOR_DIR)/scalable/apps/$(APP_ID_UNIQUE).svg\n' % dest)
				uninstall.append('\trm -fv $(HICOLOR_DIR)/scalable/apps/$(APP_ID_UNIQUE).svg\n')
				if not flatpak_build:
					install.append('\tcp -v -t $(APP_DIR)/$(ICONS_DIR) %s\n' % dest)
					install.append('\tln -s -f -v -T ../../../../nuvolaplayer3/web_apps/$(APP_ID)/%s $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/nuvolaplayer3_$(APP_ID).svg\n' % dest)
					uninstall.append('\trm -fv $(HICOLOR_DIR)/scalable/apps/nuvolaplayer3_$(APP_ID).svg\n')
				
			else:
				src = '$(ICONS_DIR)/' + fbasename(path)
				dest = "$(ICONS_DIR)/%s.png" % size
				icons.append('%s : %s | $(ICONS_DIR)\n\tsh $(NUVOLA_SDK_DATA)/svg-convert.sh $< %s $@\n' % (dest, src, size))
				install.append('\tmkdir -pv $(HICOLOR_DIR)/%sx%s/apps || true\n' % (size, size))
				install.append('\tcp -v %s $(HICOLOR_DIR)/%sx%s/apps/$(APP_ID_UNIQUE).png\n' % (dest, size, size))
				uninstall.append('\trm -fv $(HICOLOR_DIR)/%sx%s/apps/$(APP_ID_UNIQUE).png\n' % (size, size))
				if not flatpak_build:
					install.append('\tln -s -f -v -T ../../../../nuvolaplayer3/web_apps/$(APP_ID)/%s $(DESTDIR)$(PREFIX)/share/icons/hicolor/%sx%s/apps/nuvolaplayer3_$(APP_ID).png\n' % (dest, size, size))
					install.append('\tcp -v -t $(APP_DIR)/$(ICONS_DIR) %s\n' % dest)
					uninstall.append('\trm -fv $(HICOLOR_DIR)/%sx%s/apps/nuvolaplayer3_$(APP_ID).png\n' % (size, size))
				
			all_files.append(dest)
			flatpak_archive.append(dest)

	makefile = [
		defaults.GENERATED_MAKEFILE,
		"APP_ID = ", app_id, "\n",
		"APP_NAME = ", app_name, "\n",
		"APP_ID_DASHED = ", app_id_dashed, "\n",
		"APP_ID_UNIQUE = ", app_id_unique, "\n",
		"APP_NAME = ", app_name, "\n",
		"NUVOLA_SDK_DATA = ", sdk_data, "\n",
		'FILES = ', files, '\n',
		'ICONS_DIR ?= icons\n',
		'PREFIX ?= ', prefix, '\n',
		'DESTDIR ?= \n',
		'WEB_APPS = $(DESTDIR)$(PREFIX)/share/nuvolaplayer3/web_apps\n',
		'APP_DIR = $(WEB_APPS)/$(APP_ID)\n',
		'HICOLOR_DIR = $(DESTDIR)$(PREFIX)/share/icons/hicolor\n',
		'\n',
		'all: ', " ".join(all_files), '\n\n',
		'metadata.json: metadata.in.json\n',
		'\t$(error metadata.in.json is newer that metadata.json. Run ./configure again.)\n',
	]
	
	if dbus_launcher:
		makefile.extend((
			'%s: $(NUVOLA_SDK_DATA)/launch_app.vala\n' % dbus_launcher_cmd,
			'\tvalac --pkg gio-2.0 --pkg gtk+-3.0',
			' --pkg gio-unix-2.0 -D FLATPAK' if flatpak_build else '',
			' -X "-DNUVOLASDK_APP_ID=\\"$(APP_ID)\\""',
			' -X "-DNUVOLASDK_UNIQUE_ID=\\"$(APP_ID_UNIQUE)\\""',
			' -X "-DNUVOLASDK_FLATPAK_BUILD=%d"' % flatpak_build,
			' -o $@ $<\n',
		))
	
	if create_appdata:
		makefile.extend((
			'$(APP_ID_UNIQUE).appdata.xml: metadata.json\n',
			'\tpython3 -m nuvolasdk create-appdata -o $@ -m $<\n',
		))
	if desktop_launcher:
		makefile.extend((
			'$(APP_ID_UNIQUE).desktop: $(NUVOLA_SDK_DATA)/launcher.desktop\n',
			'\tsed -e "s/@@APP_NAME@@/$(APP_NAME)/g" -e "s/@@APP_ID@@/$(APP_ID)/g"',
			' -e "s/@@EXEC@@/%s/g"' % (dbus_launcher_cmd if dbus_launcher else "nuvolaplayer3 -a $(APP_ID)"),
			' -e "s/@@CATEGORIES@@/%s/g"' % metadata["categories"],
			' -e "s/@@ICON@@/$(APP_ID_UNIQUE)/g" -e "s/@@APP_ID_DASHED@@/$(APP_ID_DASHED)/g" '
			' $< > $@\n',
		))
	makefile.extend(icons)
	
	if flatpak_build:
		makefile.extend((
			'$(APP_ID_UNIQUE).data.service:\n',
			'\techo "[D-BUS Service]" > $@\n',
			'\techo "Name=$(APP_ID_UNIQUE).data" >> $@\n',
			'\techo "Exec=%s --data" >> $@\n' % dbus_launcher_cmd,
			'$(APP_ID).tar.gz: ', " ".join(flatpak_archive), '\n',
			'\ttar -cvzf $@ ', " ".join(flatpak_archive), '\n',
		))
	
	
	makefile.extend(install)
	makefile.extend(uninstall)
	makefile.extend((
		"clean:\n",
		'\trm -fv nuvola-app-$(APP_ID_DASHED)\n' if dbus_launcher else "",
		'\trm -fv $(APP_ID_UNIQUE).desktop\n' if desktop_launcher else "",
		'\trm -fv $(APP_ID_UNIQUE).appdata.xml\n' if create_appdata else "",
		'\trm -fv $(APP_ID_UNIQUE).data.service\n' if flatpak_build else "",
		'\trm -fv $(APP_ID).tar.gz\n' if flatpak_build else "",
		"\trm -rvf icons\n",
		"distclean: clean\n",
		"\trm -vf Makefile metadata.json\n"
	));
	
	fwrite("Makefile", "".join(makefile))
	
	del(metadata["build"])
	metadata["has_dbus_launcher"] = dbus_launcher
	metadata["has_desktop_launcher"] = desktop_launcher
	writejson("metadata.json", metadata)
	
	print("Makefile written. Run `make all` and then `make install`.")
		
