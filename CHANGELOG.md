Nuvola SDK Change Log
=====================

* Circle CI jobs now use Fedora 29.
* Per-application screenshots are used in AppStream metadata. Issue: tiliado/nuvolasdk#5

4.13.0 - October 14th, 2018
---------------------------

* The demo player example was updated with shuffle/repeat functionality.
  Issue: tiliado/nuvolaruntime#20, tiliado/nuvolaruntime#21
* new-project, convert-project: CircleCI configuration was added to run `nuvolasdk check-project` when a new commit
  is pushed. Look at [Tiliado projet at CircleCI](https://circleci.com/gh/tiliado) to see the results.
  Issue: tiliado/nuvolaruntime#420

4.12.0 - July 21st, 2018
------------------------

* New dependency for building Nuvola scripts: [Pillow](https://pypi.org/project/Pillow/) >= 4.3
* check-project: Added check that `metadata.in.json` use two spaces for indentation and no trailing whitespace.
* convert-project: Save `metadata.in.json` with correct indentation and no trailing whitespace.
* new-project: README.md template was updated.
* convert-project: Create `template--README.md` & `template--README.md.diff` to help with the update of README.md.
* new-project: The `integrate.js` template uses Standard JS code style.
* convert-project: Convert `integrate.js` to Standard JS code style.
* check-project: Check that `integrate.js` uses Standard JS code style.
* convert-project: API number in metadata is upgraded to that of Nuvola SDK.
* Makefile generator: If `src/webview.png` image is found, it is used to generate screenshots combining that web view
  snapshot image with base Nuvola screenshots. The resulting images can be found in the screenshots subdirectory.
  More screenshot types will be added in the next development cycle. Issue: tiliado/nuvolasdk#5

4.11.0 - May 8th, 2018
----------------------

* Compute micro version from git and add it to `metadata.json`
* Update gitignore generator.
* Two spaces are use for the indentation of JSON files.

4.10.0 - March 4th, 2018
------------------------

* Nuvola 3.0 compatibility mode was removed.
* The `nuvola-app-xxx` binary launcher was replaced with a shell script, which is now always included.
  It requires Nuvola 4.10. Consequently, `--with-dbus-launcher` configure option was removed.
* Individual apps now use the `eu.tiliado.WebRuntimeApp...` unique id.
* AppStream Addon XML metadata are generated. Issue: tiliado/nuvolasdk#1

4.9.0 - December 17th, 2017
----------------------

  * Default API version is 4.9.
  * Sync version with Nuvola Runtime.

4.7.0 - September 1st, 2017
------------------------

  * desktop launcher: Spaces around the equals sign were removed because they confuse kbuildsycoca5.
    Issue: tiliado/nuvolaruntime#365 Upstream ticket: https://bugs.kde.org/show_bug.cgi?id=310674
  * Added individual version info properties - `nuvolasdk.VERSION_MAJOR/MINOR/MICRO`.
  * new-project: New `metadata.in.json` files use the latest Nuvola SDK version.

4.6.0 - July 29th, 2017
-----------------------

  * genmakefile: Add `-link` suffix to compat symlinks to workaround Debian not being able to replace a directory
    with a symlink. Issue: tiliado/nuvolaruntime#362
  * dbus launcher: Rename Diorite to Drt.
  * Added version info - nuvolasdk.VERSION.
  * genmakefile: It is possible to specify required Nuvola SDK version.

4.5.0 - June 23rd, 2017
-----------------------

  * new-project, convert-project: User is asked for git name and git email if they are not set.
  * Happy Songs demo was updated to include progress bar and volume level.
  * genmakefile: Wrong dbus launcher command in desktop file was fixed. Issue: tiliado/nuvolaruntime#348
  * genmakefile: Legacy nuvolaplayer3_xxx icon symlinks are created only in Nuvola 3.0.x compat mode.
    Issue: tiliado/nuvolasdk#3
  * Fixed compatibility with Nuvola 4.5.0.

4.4.0 - May 27th, 2017
----------------------

  * Versioning scheme is synchronized with Nuvola Apps Runtime.
  * DBus Launcher has been ported to use the high level Start-up API of Nuvola and a data service have been removed
    because it is no longer used.
  * Compatibility with Nuvola Player 3.0.x must be enabled with the --compat flag passed to ./configure.
  * Web apps scripts are installed into the PREFIX/share/nuvolaruntime/web_apps directory used by Nuvola 4.4+
    but legacy symlinks in the PREFIX/share/nuvolaplayer3/web_apps directory are also provided for Nuvola 3.x.

1.4.0 - April 30th, 2017
------------------------

  * Makefile generator: Also install tar-gzipped files in flatpak build mode.
  * Makefile generator: DBus Launcher requires Nuvola libraries as it now executes a standalone
    Nuvola App Runner process instead of calling the Nuvola Master process to do so. Required
    for Flatpak and Snap packaging.
  * DBus launcher: Require X11.
  * Check project: Check whether licenses are in SPDX format
  * appdata: use SPDX format for license field
  * appdata: update screenshots and description.
  * DBus Launcher: Port to Nuvola 3.1.3.

1.3.0 - February 26th, 2017
---------------------------

  * Makefile generator: The `--with-desktop-launcher` option has been removed and the launcher
    is always created. Requires Nuvola Player 3.0.7 or 3.1.x.
  * Makefile generator: Set a proper StartupWMClass in desktop files.

1.2.0 - February 11th, 2017
---------------------------

  * New command 'create-appdata' to create AppStream metadata.
  * Makefile generator: Added new ./configure option '--with-appdata-xml' to generate AppStream metadata.
  * DBus launcher created a data provider for the flatpak build of Nuvola.
  * It is possible to run nuvolasdk as `python3 -m nuvolasdk ...`. This way is now used in generated Makefiles.
  * Makefile ends with an erro if the generated metadada.json file is older then the source metadata.in.json file.
  * Convert project: Also adds missing icons.

1.1.0 - December 4th, 2016
--------------------------

  * check-project: `make clean` isn't run if there is no Makefile.
  * data-dir: New command to print the Nuvola SDK data directory.
  * Added `examples/home.html` to the data directory. It is a dumb
    example of a streaming service to be used in a tutorial.

1.0.0 - December 3rd, 2016
--------------------------

  * Initial release.
