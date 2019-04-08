#!/bin/sh
exec docker run -v `pwd`:/workdir --privileged tiliado/nuvolasdk-ci
