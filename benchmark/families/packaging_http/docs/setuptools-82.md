# setuptools changelog (NEWS.rst): v82.0.0 and v82.0.1

Source: https://raw.githubusercontent.com/pypa/setuptools/main/NEWS.rst (verbatim excerpt, fetched 2026-09-29)
License: MIT (https://github.com/pypa/setuptools/blob/main/LICENSE).
v82.0.0 was published to PyPI on 2026-02-08 (https://pypi.org/pypi/setuptools/82.0.0/json).

```rst
v82.0.1
=======

Bugfixes
--------

- Fix the loading of ``launcher manifest.xml`` file. (#5047)
- Replaced deprecated ``json.__version__`` with fixture in tests. (#5186)


Improved Documentation
----------------------

- Add advice about how to improve predictability when installing sdists. (#5168)


Misc
----

- #4941, #5157, #5169, #5175

v82.0.0
=======

Deprecations and Removals
-------------------------

- ``pkg_resources`` has been removed from Setuptools. Most common uses of ``pkg_resources`` have been superseded by the `importlib.resources <https://docs.python.org/3/library/importlib.resources.html>`_ and `importlib.metadata <https://docs.python.org/3/library/importlib.metadata.html>`_ projects. Projects and environments relying on ``pkg_resources`` for namespace packages or other behavior should depend on older versions of ``setuptools``. (#3085)
```
