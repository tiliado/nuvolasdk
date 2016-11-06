Nuvola SDK
==========

SDK for building Nuvola Player's web app scripts

Dependencies
------------

  - Python >= 3.4

New-Style Projects
------------------

The build procedure of new-style projects is as follows:

1. Run `./configure` to generate `Makefile` and `metadata.json` from details in `metadata.in.json`.
2. Run `make all` to build icons.
3. Run `make install` to install the script.

SDK Usage
---------

### Create New Project

TODO

### Convert Project

```
nuvolasdk convert-project
```

Converts old-style projects without SDK to a new-style project with SDK. Notable changes:

  * The metadata file `metadata.json` has been renamed to `metadata.in.json` and contains a new `build` section.
  * A new script `configure` loads the SDK to read `metadata.in.json` in order to generate `Makefile` and
    `metadata.json` (without the `build` section but with new metadata from `configure` process.
  * The old `Makefile` is renamed to `Makefile.old` and can be safely removed once the new-style
    project build successfully.
  * The scripts `svg-convert.sh` and `svg-optimize.sh` are removed because they are included in the SDK.
