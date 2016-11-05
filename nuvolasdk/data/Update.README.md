Update Readme
=============

Don't forget to update following sections in README.md:

Dependencies
------------

  * Python >= 3.4
  * Nuvola SDK
  * GNU Make
  * SVG optimizer: [Scour](https://github.com/codedread/scour)
  * SVG converter: Lasem, librsvg, GraphicsMagick, ImageMagick

Installation
------------

 1. Run `./configure` to generate `Makefile` from details in `metadata.json` and `build.json`. Recognized options:
      - `--prefix`: Specify a custom build prefix instead of `/usr/local`. Example: `./configure --prefix=/usr`
 2. Run `make all` to build icons.
 3. Run `make install` to install the script. Recognized variables:
      - `DEST`: A custom installation destination (defaults to the filesystem root).
         Example: `make DEST=/tmp/build/package install`
 4. Run `make uninstall` to uninstall the script. Recognized variables:
      - `DEST`: A custom installation destination (defaults to the filesystem root).
         Example: `make DEST=/tmp/build/package uninstall`
