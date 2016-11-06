Update Readme
=============

Don't forget to update following sections in README.md:

Dependencies
------------

  * Valac (only in case of `./configure --with-dbus-launcher`)
  * Python >= 3.4
  * [Nuvola SDK](https://github.com/tiliado/nuvolasdk)
  * GNU Make
  * SVG optimizer: [Scour](https://github.com/codedread/scour)
  * SVG converter: Lasem, librsvg, GraphicsMagick, ImageMagick

Installation
------------

 1. Run `./configure` to generate `Makefile` and `metadata.json` from details in `metadata.in.json`. Recognized options:
      - `--prefix`: Specify a custom build prefix instead of `/usr/local`. Example: `./configure --prefix=/usr`
      - `--with-dbus-launcher`: Build a small launcher (`nuvola-app-{APP ID with dashes}`) to invoke the application
         via a D-Bus service activation mechanism. Requires Nuvola Player 3.1.
      - `--with-desktop-launcher`: Build a desktop launcher to invoke the application.
         Required for Nuvola Player 3.1. Not compatible with Nuvola Player 3.0.
 2. Run `make all` to build the project.
 3. Run `make install` to install the project. Recognized variables:
      - `DEST`: A custom installation destination (defaults to the filesystem root).
         Example: `make DEST=/tmp/build/package install`
 4. Run `make uninstall` to uninstall the project. Recognized variables:
      - `DEST`: A custom installation destination (defaults to the filesystem root).
         Example: `make DEST=/tmp/build/package uninstall`
