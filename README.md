Nuvola SDK
==========

SDK for building Nuvola Apps Runtime's web app scripts.

Install Nuvola SDK
------------------

### Dependencies

  - Python >= 3.4

### Installation from PyPI

  * `pip3 install -U nuvolasdk`
  * or `sudo pip3 install -U nuvolasdk`

### Installation from Source Code

  * `python3 setup.py build`
  * `python3 setup.py install --prefix="$(PREFIX)" --root="$(DEST)"`


Build a Project Using Nuvola SDK
--------------------------------

### Dependencies

  * GNU Make
  * SVG optimizer: [Scour](https://github.com/codedread/scour)
  * SVG converter: Lasem, librsvg, GraphicsMagick, ImageMagick
  * [Pillow](https://pypi.org/project/Pillow/) >= 4.3


### Installation

 1. Run `./configure` to generate `Makefile` and `metadata.json` from details in `metadata.in.json`. Recognized options:
      - `--prefix`: Specify a custom build prefix instead of `/usr/local`. Example: `./configure --prefix=/usr`
 2. Run `make all` to build the project.
 3. Run `make install` to install the project. Recognized variables:
      - `DESTDIR`: A custom installation destination (defaults to the filesystem root).
         Example: `make DESTDIR=/tmp/build/package install`
 4. Run `make uninstall` to uninstall the project. Recognized variables:
      - `DESTDIR`: A custom installation destination (defaults to the filesystem root).
         Example: `make DESTDIR=/tmp/build/package uninstall`

Create a New Project Using Nuvola SDK
-------------------------------------

```
nuvolasdk new-project
```

When run without additional arguments, user will be asked to provide necessary metadata for the script.
In order to get information about available arguments run `nuvolasdk new-project --help`.

Check whether a project is well-formed
--------------------------------------

```
nuvolasdk check-project
```

Please run this check before a code review.

Convert or Upgrade Project to Use Nuvola SDK
--------------------------------------------

```
nuvolasdk convert-project
```

If used on new-style projects using Nuvola SDK, the project is updated to the latest standards.

If used on old-style projects without SDK, the project is converted to a new-style project with SDK. Notable changes:

  * The metadata file `metadata.json` has been renamed to `metadata.in.json` and contains a new `build` section.
  * A new script `configure` loads the SDK to read `metadata.in.json` in order to generate `Makefile` and
    `metadata.json` (without the `build` section but with new metadata from `configure` process.
  * The old `Makefile` is renamed to `Makefile.old` and can be safely removed once the new-style
    project build successfully.
  * The scripts `svg-convert.sh` and `svg-optimize.sh` are removed because they are included in the SDK.

Change Log
----------

See [CHANGELOG.md](./CHANGELOG.md).
