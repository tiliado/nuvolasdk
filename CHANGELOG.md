Nuvola SDK Change Log
=====================

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
