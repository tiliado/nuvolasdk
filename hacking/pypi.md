Publish to PyPI
===============


Configure
-------------

```
pip3 install twine
```

~/.pypirc

```
[distutils]
index-servers=
    pypi
    testpypi

[testpypi]
repository = https://testpypi.python.org/pypi
username = fenryxo

[pypi]
repository = https://pypi.python.org/pypi
username = fenryxo
```

Build
-----

```
python3 setup.py sdist
python3 setup.py bdist_wheel
```

Register
-------

```
twine register -r testpypi dist/nuvolasdk-*.whl
twine register -r pypi dist/nuvolasdk-*.whl
```

Publish
-------

```
twine upload -r testpypi dist/*
twine upload -r pypi dist/*
```
