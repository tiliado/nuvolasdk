#!/bin/sh
set -x
docker login -u tiliadopull -p 1855d5dd-fb03-4fd7-8932-d8365b200b6b
docker pull tiliado/nuvolasdk-ci:circleci
docker pull tiliado/nuvolasdk-ci:latest
exec docker run -v `pwd`:/workdir --privileged tiliado/nuvolasdk-ci:latest
