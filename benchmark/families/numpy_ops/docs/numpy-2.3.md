# NumPy 2.3.0 release notes: expired deprecations

Source: https://raw.githubusercontent.com/numpy/numpy/v2.3.0/doc/source/release/2.3.0-notes.rst (verbatim excerpt, fetched 2026-09-29)

```rst
NumPy 2.3.0 Release Notes
```

[... lines omitted from this excerpt ...]

```rst
Expired deprecations
====================

* Remove deprecated macros like ``NPY_OWNDATA`` from Cython interfaces in favor
  of ``NPY_ARRAY_OWNDATA`` (deprecated since 1.7)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Remove ``numpy/npy_1_7_deprecated_api.h`` and C macros like ``NPY_OWNDATA``
  in favor of ``NPY_ARRAY_OWNDATA`` (deprecated since 1.7)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Remove alias ``generate_divbyzero_error`` to
  ``npy_set_floatstatus_divbyzero`` and ``generate_overflow_error`` to
  ``npy_set_floatstatus_overflow`` (deprecated since 1.10)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Remove ``np.tostring`` (deprecated since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Raise on ``np.conjugate`` of non-numeric types (deprecated since 1.13)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Raise when using ``np.bincount(...minlength=None)``, use 0 instead
  (deprecated since 1.14)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Passing ``shape=None`` to functions with a non-optional shape argument
  errors, use ``()`` instead (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Inexact matches for ``mode`` and ``searchside`` raise (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Setting ``__array_finalize__ = None`` errors (deprecated since 1.23)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* ``np.fromfile`` and ``np.fromstring`` error on bad data, previously they
  would guess (deprecated since 1.18)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* ``datetime64`` and ``timedelta64`` construction with a tuple no longer
  accepts an ``event`` value, either use a two-tuple of (unit, num) or a
  4-tuple of (unit, num, den, 1) (deprecated since 1.14)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* When constructing a ``dtype`` from a class with a ``dtype`` attribute, that
  attribute must be a dtype-instance rather than a thing that can be parsed as
  a dtype instance (deprecated in 1.19). At some point the whole construct of
  using a dtype attribute will be deprecated (see #25306)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Passing booleans as partition index errors (deprecated since 1.23)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Out-of-bounds indexes error even on empty arrays (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* ``np.tostring`` has been removed, use ``tobytes`` instead (deprecated since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Disallow make a non-writeable array writeable for arrays with a base that do
  not own their data (deprecated since 1.17)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* ``concatenate()`` with ``axis=None`` uses ``same-kind`` casting by default,
  not ``unsafe`` (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Unpickling a scalar with object dtype errors (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)

* The binary mode of ``fromstring`` now errors, use ``frombuffer`` instead
  (deprecated since 1.14)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Converting ``np.inexact`` or ``np.floating`` to a dtype errors (deprecated
  since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Converting ``np.complex``, ``np.integer``, ``np.signedinteger``,
  ``np.unsignedinteger``, ``np.generic`` to a dtype errors (deprecated since
  1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* The Python built-in ``round`` errors for complex scalars. Use ``np.round`` or
  ``scalar.round`` instead (deprecated since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* 'np.bool' scalars can no longer be interpreted as an index (deprecated since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Parsing an integer via a float string is no longer supported. (deprecated
  since 1.23) To avoid this error you can
  * make sure the original data is stored as integers.
  * use the ``converters=float`` keyword argument.
  * Use ``np.loadtxt(...).astype(np.int64)``

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)

* The use of a length 1 tuple for the ufunc ``signature`` errors. Use ``dtype``
  or  fill the tuple with ``None`` (deprecated since 1.19)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)
 
* Special handling of matrix is in np.outer is removed. Convert to a ndarray
  via ``matrix.A`` (deprecated since 1.20)

  (`gh-28254 <https://github.com/numpy/numpy/pull/28254>`__)

* Removed the ``np.compat`` package source code (removed in 2.0)

  (`gh-28961 <https://github.com/numpy/numpy/pull/28961>`__)
```
