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

import sys
from nuvolasdk.shkit import *
from nuvolasdk import defaults
from nuvolasdk import utils
from nuvolasdk import VERSION

def gen_makefile(required_version=VERSION):
	if not utils.check_version(required_version):
		print("This project requires Nuvola SDK >= %s but version %s is installed." % (required_version, VERSION))
		sys.exit(1)

	prefix = "/usr/local"
	flatpak_build = False
	create_appdata = False
	genuine = False
	metadata = readjson("metadata.in.json")
	build_json = metadata.get("build", {})
	build_screenshots = isfile(defaults.WEB_VIEW_IMAGE)

	major, minor, micro, revision = utils.compute_version_from_git(
		metadata["version_major"], metadata.get("version_minor", 0), metadata.get("version_micro", 0))
	metadata["version_major"] = major
	metadata["version_minor"] = minor
	metadata["version_micro"] = micro
	metadata["version_revision"] = revision

	for arg in sys.argv[1:]:
		try:
			name, value = arg.split("=", 1)
		except ValueError:
			name = arg
			value = None
		if name == "--libdir":
			pass
		elif name == "--prefix":
			prefix = value
		elif name in ("CFLAGS", "CXXFLAGS"):
			pass
		elif name == "--with-appdata-xml":
			create_appdata = True
		elif name == "--flatpak-build":
			flatpak_build = True
		elif name == "--genuine":
			genuine = True
		else:
			print("Warning: Unknown option: ", arg)

	if flatpak_build:
		create_appdata = True

	app_id = metadata["id"]
	app_name = metadata["name"]
	app_id_dashed = utils.get_dashed_app_id(app_id)
	app_id_unique = utils.get_unique_app_id(app_id, genuine)
	app_id_dbus = utils.get_dbus_app_id(app_id, genuine)
	sdk_data = utils.get_sdk_data_dir()

	all_files = defaults.BASE_INSTALL_FILES[:]
	all_files.extend(utils.get_license_files())
	for entry in build_json.get("extra_data", []):
		all_files.extend(glob(entry))

	files = ' '.join(all_files)

	makefile = [
		defaults.GENERATED_MAKEFILE % VERSION,
		"APP_ID = ", app_id, "\n",
		"APP_NAME = ", app_name, "\n",
		"APP_ID_DASHED = ", app_id_dashed, "\n",
		"APP_ID_UNIQUE = ", app_id_unique, "\n",
		"APP_ID_DBUS = ", app_id_dbus, "\n",
		"APP_NAME = ", app_name, "\n",
		"NUVOLA_SDK_DATA = ", sdk_data, "\n",
		'FILES = ', ' '.join(all_files), '\n',
		'ICONS_DIR ?= icons\n',
		'PREFIX ?= ', prefix, '\n',
		'DESTDIR ?= \n',
		'DATADIR ?= $(PREFIX)/share\n',
		'BINDIR ?= $(PREFIX)/bin\n',
		'WEB_APPS_DIR ?= $(DATADIR)/nuvolaruntime/web_apps\n',
		'OLD_APPS_DIR ?= $(DATADIR)/nuvolaplayer3/web_apps\n',
		'APP_DATA_DIR ?= $(WEB_APPS_DIR)/$(APP_ID)\n',
		'HICOLOR_DIR = $(DATADIR)/icons/hicolor\n',
		'\n',
	]
	install = [
		'install: all\n',
		'\tinstall -vCd $(DESTDIR)$(APP_DATA_DIR)/$(ICONS_DIR)\n',
		'\tcp -rv -t $(DESTDIR)$(APP_DATA_DIR) $(FILES)\n',
	]
	uninstall = [
		'uninstall:\n',
		'\trm -rfv $(DESTDIR)$(APP_DATA_DIR)\n',
	]


	launcher_cmd = 'nuvola-app-$(APP_ID_DASHED)'
	all_files.extend((launcher_cmd, '$(APP_ID_DBUS).service'))
	install.extend((
		'\tinstall -vCd $(DESTDIR)$(BINDIR)\n',
		'\tinstall -vC -t $(DESTDIR)$(BINDIR) %s\n' % launcher_cmd,
		'\tinstall -vCd $(DESTDIR)$(DATADIR)/dbus-1/services\n',
		'\tcp -vf -t $(DESTDIR)$(DATADIR)/dbus-1/services $(APP_ID_DBUS).service\n',
	))
	uninstall.extend((
		'\trm -fv $(DESTDIR)$(BINDIR)/%s\n' % launcher_cmd,
	))


	all_files.append('$(APP_ID_UNIQUE).desktop')
	install.extend((
		'\tinstall -vCd $(DESTDIR)$(DATADIR)/applications\n',
		'\tcp -vf -t $(DESTDIR)$(DATADIR)/applications $(APP_ID_UNIQUE).desktop\n',
	))
	uninstall.append('\trm -fv $(DESTDIR)$(DATADIR)/applications/$(APP_ID_UNIQUE).desktop\n')

	if create_appdata:
		all_files.append('$(APP_ID_UNIQUE).appdata.xml')
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(DATADIR)/metainfo\n',
			'\tcp -vf -t $(DESTDIR)$(DATADIR)/metainfo $(APP_ID_UNIQUE).appdata.xml\n',
		))
		uninstall.append('\trm -fv $(DESTDIR)$(DATADIR)/metainfo/$(APP_ID_UNIQUE).appdata.xml\n')
	else:
		all_files.append('nuvola-app-$(APP_ID_DASHED).metainfo.xml')
		install.extend((
			'\tinstall -vCd $(DESTDIR)$(DATADIR)/metainfo\n',
			'\tcp -vf -t $(DESTDIR)$(DATADIR)/metainfo nuvola-app-$(APP_ID_DASHED).metainfo.xml\n',
		))
		uninstall.append('\trm -fv $(DESTDIR)$(DATADIR)/metainfo/nuvola-app-$(APP_ID_DASHED).metainfo.xml\n')

	if build_screenshots:
		all_files.append('screenshots/%s' % defaults.SCREENSHOTS_DIR_TIMESTAMP)

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
				install.append('\tmkdir -pv $(DESTDIR)$(HICOLOR_DIR)/scalable/apps || true\n')
				install.append('\tcp -v %s $(DESTDIR)$(HICOLOR_DIR)/scalable/apps/$(APP_ID_UNIQUE).svg\n' % dest)
				install.append('\tcp -v -t $(DESTDIR)$(APP_DATA_DIR)/$(ICONS_DIR) %s\n' % dest)
				uninstall.append('\trm -fv $(DESTDIR)$(HICOLOR_DIR)/scalable/apps/$(APP_ID_UNIQUE).svg\n')
			else:
				src = '$(ICONS_DIR)/' + fbasename(path)
				dest = "$(ICONS_DIR)/%s.png" % size
				icons.append('%s : %s | $(ICONS_DIR)\n\tsh $(NUVOLA_SDK_DATA)/svg-convert.sh $< %s $@\n' % (dest, src, size))
				install.append('\tmkdir -pv $(DESTDIR)$(HICOLOR_DIR)/%sx%s/apps || true\n' % (size, size))
				install.append('\tcp -v %s $(DESTDIR)$(HICOLOR_DIR)/%sx%s/apps/$(APP_ID_UNIQUE).png\n' % (dest, size, size))
				install.append('\tcp -v -t $(DESTDIR)$(APP_DATA_DIR)/$(ICONS_DIR) %s\n' % dest)
				uninstall.append('\trm -fv $(DESTDIR)$(HICOLOR_DIR)/%sx%s/apps/$(APP_ID_UNIQUE).png\n' % (size, size))

			all_files.append(dest)

	makefile.extend([
		'all: ', " ".join(all_files), '\n\n',
		'metadata.json: metadata.in.json\n',
		'\t$(error metadata.in.json is newer that metadata.json. Run ./configure again.)\n',
	])


	makefile.extend((
		'%s: $(NUVOLA_SDK_DATA)/launch_app.sh\n' % launcher_cmd,
		'\tsed -e "s#@@APP_DIR@@#$(APP_DATA_DIR)#g"',
		'  $< > $@\n',
		'\tchmod a+x $@\n',
	))
	makefile.extend((
		'$(APP_ID_DBUS).service:\n',
		'\techo "[D-BUS Service]" > $@\n',
		'\techo "Name=$(APP_ID_DBUS)" >> $@\n',
		'\techo "Exec=%s --gapplication-service" >> $@\n' % launcher_cmd,
	))

	if create_appdata:
		makefile.extend((
			'$(APP_ID_UNIQUE).appdata.xml: metadata.json\n',
			'\tpython3 -m nuvolasdk create-appdata %s -o $@ -m $<\n' % ('--genuine' if genuine else ''),
		))
	else:
		makefile.extend((
			'nuvola-app-$(APP_ID_DASHED).metainfo.xml: metadata.json\n',
			'\tpython3 -m nuvolasdk create-addondata %s -o $@ -m $<\n' % ('--genuine' if genuine else ''),
		))

	makefile.extend((
		'$(APP_ID_UNIQUE).desktop: $(NUVOLA_SDK_DATA)/launcher.desktop\n',
		'\tsed -e "s/@@APP_NAME@@/$(APP_NAME)/g" -e "s/@@APP_ID@@/$(APP_ID)/g"',
		' -e "s/@@EXEC@@/%s/g"' % launcher_cmd,
		' -e "s/@@CATEGORIES@@/%s/g"' % metadata["categories"],
		' -e "s/@@ICON@@/$(APP_ID_UNIQUE)/g" -e "s/@@APP_UID@@/$(APP_ID_UNIQUE)/g" '
		' $< > $@\n',
	))

	if build_screenshots:
		makefile.extend((
			'screenshots/%s: %s\n' % (defaults.SCREENSHOTS_DIR_TIMESTAMP, defaults.WEB_VIEW_IMAGE),
			'\tpython3 -m nuvolasdk create-screenshots -o screenshots -i $<\n',
		))
		all_files.append('screenshots/%s' % defaults.SCREENSHOTS_DIR_TIMESTAMP)

	makefile.extend(icons)
	makefile.extend(install)
	makefile.extend(uninstall)

	makefile.extend((
		"clean:\n",
		'\trm -fv nuvola-app-$(APP_ID_DASHED)\n',
		'\trm -fv $(APP_ID_UNIQUE).desktop\n',
		('\trm -fv $(APP_ID_UNIQUE).appdata.xml\n' if create_appdata else
		'\trm -fv nuvola-app-$(APP_ID_DASHED).metainfo.xml\n'),
		'\trm -fv $(APP_ID_DBUS).service\n' if flatpak_build else "",
		'\trm -fv $(APP_ID).tar.gz\n' if flatpak_build else "",
		"\trm -rvf icons\n",
		"\trm -rvf screenshots\n" if build_screenshots else "",
		"distclean: clean\n",
		"\trm -vf Makefile metadata.json\n"
	));

	fwrite("Makefile", "".join(makefile))

	del(metadata["build"])
	metadata["has_dbus_launcher"] = True
	metadata["has_desktop_launcher"] = True
	metadata["sdk_version"] = VERSION
	writejson("metadata.json", metadata)

	print("Nuvola SDK %s Makefile written. Run `make all` and then `make install`." % VERSION)

