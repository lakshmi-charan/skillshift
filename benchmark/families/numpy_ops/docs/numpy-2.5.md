# NumPy 2.5.0 release notes: expired deprecations

Source: https://raw.githubusercontent.com/numpy/numpy/v2.5.0/doc/source/release/2.5.0-notes.rst (verbatim excerpt, fetched 2026-09-29)

```rst
NumPy 2.5.0 Release Notes
```

[... lines omitted from this excerpt ...]

```rst
Expired deprecations
====================

* ``numpy.distutils`` has been removed

  (`gh-30340 <https://github.com/numpy/numpy/pull/30340>`__)

* Passing ``None`` as dtype to ``np.finfo`` will now raise a ``TypeError``
  (deprecated since 1.25)

  (`gh-30460 <https://github.com/numpy/numpy/pull/30460>`__)

* ``numpy.cross`` no longer supports 2-dimensional vectors.
  (Deprecated since 2.0)

  (`gh-30461 <https://github.com/numpy/numpy/pull/30461>`__)

* ``numpy._core.numerictypes.maximum_sctype`` has been removed.
  (deprecated since 2.0)

  (`gh-30462 <https://github.com/numpy/numpy/pull/30462>`__)

* ``numpy.row_stack`` has been removed in favor of ``numpy.vstack``.
  (deprecated since 2.0)

  (`gh-30463 <https://github.com/numpy/numpy/pull/30463>`__)

* ``get_array_wrap`` has been removed.
  (deprecated since 2.0)

  (`gh-30463 <https://github.com/numpy/numpy/pull/30463>`__)

* ``recfromtxt`` and ``recfromcsv`` have been removed from ``numpy.lib._npyio``
  in favor of ``numpy.genfromtxt``.
  (deprecated since 2.0)

  (`gh-30467 <https://github.com/numpy/numpy/pull/30467>`__)

* The ``numpy.chararray`` re-export of ``numpy.char.chararray`` has been removed.
  (deprecated since 2.0)

  (`gh-30604 <https://github.com/numpy/numpy/pull/30604>`__)

* ``bincount`` now raises a ``TypeError`` for non-integer inputs.
  (deprecated since 2.1)

  (`gh-30610 <https://github.com/numpy/numpy/pull/30610>`__)

* The ``numpy.lib.math`` alias for the standard library ``math`` module has
  been removed.
  (deprecated since 1.25)

  (`gh-30612 <https://github.com/numpy/numpy/pull/30612>`__)

* Data type alias ``'a'`` was removed in favor of ``'S'``.
  (deprecated since 2.0)

  (`gh-30613 <https://github.com/numpy/numpy/pull/30613>`__)

* ``_add_newdoc_ufunc(ufunc, newdoc)`` has been removed in favor of
  ``ufunc.__doc__ = newdoc``.
  (deprecated since 2.2)

  (`gh-30614 <https://github.com/numpy/numpy/pull/30614>`__)
```
