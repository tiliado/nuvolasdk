Nuvola SDK CI Image
===================

  - Based on Fedora.
  - Installs Flatpak framework.
  - Installs [Nuvola ADK](https://github.com/tiliado/nuvolaruntime/wiki/Nuvola-App-Developer-Kit) flatpak packages.
  - Executes [nuvolasdk-ci script](./nuvolasdk-ci).

Build
-----

```
docker build -t tiliado/nuvolasdk-ci .
```

Publish
-------

```
docker push tiliado/nuvolasdk-ci
```

CircleCI
--------

A sample [CircleCI](https://circleci.com) configuration `.circleci/config.yml`:

```
version: 2
jobs:
  build:
    machine: # for docker --privileged
      image: circleci/classic:latest
    working_directory: ~/workdir
    steps:
      - checkout
      - run:
          name: Pull tiliado/nuvolasdk-ci
          command: docker pull tiliado/nuvolasdk-ci
      - run:
          name: Check project
          command: docker run -v `pwd`:/workdir --privileged tiliado/nuvolasdk-ci
      - store_artifacts:
          path: ~/workdir/keep
```
