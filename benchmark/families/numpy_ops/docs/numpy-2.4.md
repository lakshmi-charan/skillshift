# NumPy 2.4.0 release notes: expired deprecations

Source: https://raw.githubusercontent.com/numpy/numpy/v2.4.0/doc/source/release/2.4.0-notes.rst (verbatim excerpt, fetched 2026-09-29)

```rst
NumPy 2.4.0 Release Notes
```

[... lines omitted from this excerpt ...]

```rst
Expired deprecations
====================

Removed deprecated ``MachAr`` runtime discovery mechanism.
----------------------------------------------------------

(`gh-29836 <https://github.com/numpy/numpy/pull/29836>`__)

Raise ``TypeError`` on attempt to convert array with ``ndim > 0`` to scalar
---------------------------------------------------------------------------
Conversion of an array with ``ndim > 0`` to a scalar was deprecated in NumPy
1.25.  Now, attempting to do so raises ``TypeError``.  Ensure you extract a
single element from your array before performing this operation.

(`gh-29841 <https://github.com/numpy/numpy/pull/29841>`__)

Removed numpy.linalg.linalg and numpy.fft.helper
------------------------------------------------
The following were deprecated in NumPy 2.0 and have been moved to private
modules:

* ``numpy.linalg.linalg``
  Use ``numpy.linalg`` instead.

* ``numpy.fft.helper``
  Use ``numpy.fft`` instead.

(`gh-29909 <https://github.com/numpy/numpy/pull/29909>`__)

Removed ``interpolation`` parameter from quantile and percentile functions
--------------------------------------------------------------------------
The ``interpolation`` parameter was deprecated in NumPy 1.22.0 and has been
removed from the following functions:

* ``numpy.percentile``
* ``numpy.nanpercentile``
* ``numpy.quantile``
* ``numpy.nanquantile``

Use the ``method`` parameter instead.

(`gh-29973 <https://github.com/numpy/numpy/pull/29973>`__)

Removed ``numpy.in1d``
----------------------
``numpy.in1d`` has been deprecated since NumPy 2.0 and is now removed in favor of ``numpy.isin``.

(`gh-29978 <https://github.com/numpy/numpy/pull/29978>`__)

Removed ``numpy.ndindex.ndincr()``
----------------------------------
The ``ndindex.ndincr()`` method has been deprecated since NumPy 1.20 and is now
removed; use ``next(ndindex)`` instead.

(`gh-29980 <https://github.com/numpy/numpy/pull/29980>`__)

Removed ``fix_imports`` parameter from ``numpy.save``
-----------------------------------------------------
The ``fix_imports`` parameter was deprecated in NumPy 2.1.0 and is now removed.
This flag has been ignored since NumPy 1.17 and was only needed to support
loading files in Python 2 that were written in Python 3.

(`gh-29984 <https://github.com/numpy/numpy/pull/29984>`__)

Removal of four undocumented ``ndarray.ctypes`` methods
-------------------------------------------------------
Four undocumented methods of the ``ndarray.ctypes`` object have been removed:

* ``_ctypes.get_data()`` (use ``_ctypes.data`` instead)
* ``_ctypes.get_shape()`` (use ``_ctypes.shape`` instead)
* ``_ctypes.get_strides()`` (use ``_ctypes.strides`` instead)
* ``_ctypes.get_as_parameter()`` (use ``_ctypes._as_parameter_`` instead)

These methods have been deprecated since NumPy 1.21.

(`gh-29986 <https://github.com/numpy/numpy/pull/29986>`__)

Removed ``newshape`` parameter from ``numpy.reshape``
-----------------------------------------------------
The ``newshape`` parameter was deprecated in NumPy 2.1.0 and has been
removed from ``numpy.reshape``. Pass it positionally or use ``shape=``
on newer NumPy versions.

(`gh-29994 <https://github.com/numpy/numpy/pull/29994>`__)

Removal of deprecated functions and arguments
---------------------------------------------
The following long-deprecated APIs have been removed:

* ``numpy.trapz`` — deprecated since NumPy 2.0 (2023-08-18). Use ``numpy.trapezoid`` or
  ``scipy.integrate`` functions instead.

* ``disp`` function — deprecated from 2.0 release and no longer functional. Use
  your own printing function instead.

* ``bias`` and ``ddof`` arguments in ``numpy.corrcoef`` — these had no effect
  since NumPy 1.10.

(`gh-29997 <https://github.com/numpy/numpy/pull/29997>`__)

Removed ``delimitor`` parameter from ``numpy.ma.mrecords.fromtextfile()``
-------------------------------------------------------------------------
The ``delimitor`` parameter was deprecated in NumPy 1.22.0 and has been
removed from ``numpy.ma.mrecords.fromtextfile()``. Use ``delimiter`` instead.

(`gh-30021 <https://github.com/numpy/numpy/pull/30021>`__)

``numpy.array2string`` and ``numpy.sum`` deprecations finalized
---------------------------------------------------------------
The following long-deprecated APIs have been removed or converted to errors:

* The ``style`` parameter has been removed from ``numpy.array2string``.
  This argument had no effect since Numpy 1.14.0.  Any arguments following
  it, such as ``formatter`` have now been made keyword-only.

* Calling ``np.sum(generator)`` directly on a generator object now raises a
  ``TypeError``.  This behavior was deprecated in NumPy 1.15.0. Use
  ``np.sum(np.fromiter(generator))`` or the python ``sum`` builtin instead.

(`gh-30068 <https://github.com/numpy/numpy/pull/30068>`__)
```
