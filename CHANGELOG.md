Nuvola SDK Change Log
=====================

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
