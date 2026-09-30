# NumPy 2.0.0 release notes: Python API removals

Source: https://raw.githubusercontent.com/numpy/numpy/v2.0.0/doc/source/release/2.0.0-notes.rst (verbatim excerpt, fetched 2026-09-29)

```rst
NumPy 2.0.0 Release Notes
```

[... lines omitted from this excerpt ...]

```rst
NumPy 2.0 Python API removals
=============================

* ``np.geterrobj``, ``np.seterrobj`` and the related ufunc keyword argument
  ``extobj=`` have been removed.  The preferred replacement for all of these
  is using the context manager ``with np.errstate():``.

  (`gh-23922 <https://github.com/numpy/numpy/pull/23922>`__)

* ``np.cast`` has been removed. The literal replacement for
  ``np.cast[dtype](arg)`` is ``np.asarray(arg, dtype=dtype)``.

* ``np.source`` has been removed. The preferred replacement is
  ``inspect.getsource``.

* ``np.lookfor`` has been removed.

  (`gh-24144 <https://github.com/numpy/numpy/pull/24144>`__)

* ``numpy.who`` has been removed. As an alternative for the removed functionality, one
  can use a variable explorer that is available in IDEs such as Spyder or Jupyter Notebook.

  (`gh-24321 <https://github.com/numpy/numpy/pull/24321>`__)

* Warnings and exceptions present in `numpy.exceptions` (e.g,
  `~numpy.exceptions.ComplexWarning`,
  `~numpy.exceptions.VisibleDeprecationWarning`) are no longer exposed in the
  main namespace.
* Multiple niche enums, expired members and functions have been removed from
  the main namespace, such as: ``ERR_*``, ``SHIFT_*``, ``np.fastCopyAndTranspose``,
  ``np.kernel_version``, ``np.numarray``, ``np.oldnumeric`` and ``np.set_numeric_ops``.

  (`gh-24316 <https://github.com/numpy/numpy/pull/24316>`__)

* Replaced ``from ... import *`` in the ``numpy/__init__.py`` with explicit imports.
  As a result, these main namespace members got removed: ``np.FLOATING_POINT_SUPPORT``,
  ``np.FPE_*``, ``np.NINF``, ``np.PINF``, ``np.NZERO``, ``np.PZERO``, ``np.CLIP``,
  ``np.WRAP``, ``np.WRAP``, ``np.RAISE``, ``np.BUFSIZE``, ``np.UFUNC_BUFSIZE_DEFAULT``,
  ``np.UFUNC_PYVALS_NAME``, ``np.ALLOW_THREADS``, ``np.MAXDIMS``, ``np.MAY_SHARE_EXACT``,
  ``np.MAY_SHARE_BOUNDS``, ``add_newdoc``, ``np.add_docstring`` and
  ``np.add_newdoc_ufunc``.

  (`gh-24357 <https://github.com/numpy/numpy/pull/24357>`__)

* Alias ``np.float_`` has been removed. Use ``np.float64`` instead.

* Alias ``np.complex_`` has been removed. Use ``np.complex128`` instead.

* Alias ``np.longfloat`` has been removed. Use ``np.longdouble`` instead.

* Alias ``np.singlecomplex`` has been removed. Use ``np.complex64`` instead.

* Alias ``np.cfloat`` has been removed. Use ``np.complex128`` instead.

* Alias ``np.longcomplex`` has been removed. Use ``np.clongdouble`` instead.

* Alias ``np.clongfloat`` has been removed. Use ``np.clongdouble`` instead.

* Alias ``np.string_`` has been removed. Use ``np.bytes_`` instead.

* Alias ``np.unicode_`` has been removed. Use ``np.str_`` instead.

* Alias ``np.Inf`` has been removed. Use ``np.inf`` instead.

* Alias ``np.Infinity`` has been removed. Use ``np.inf`` instead.

* Alias ``np.NaN`` has been removed. Use ``np.nan`` instead.

* Alias ``np.infty`` has been removed. Use ``np.inf`` instead.

* Alias ``np.mat`` has been removed. Use ``np.asmatrix`` instead.

* ``np.issubclass_`` has been removed. Use the ``issubclass`` builtin instead.

* ``np.asfarray`` has been removed. Use ``np.asarray`` with a proper dtype instead.

* ``np.set_string_function`` has been removed. Use ``np.set_printoptions``
  instead with a formatter for custom printing of NumPy objects.

* ``np.tracemalloc_domain`` is now only available from ``np.lib``.

* ``np.recfromcsv`` and ``recfromtxt`` are now only available from ``np.lib.npyio``.

* ``np.issctype``, ``np.maximum_sctype``, ``np.obj2sctype``, ``np.sctype2char``,
  ``np.sctypes``, ``np.issubsctype`` were all removed from the
  main namespace without replacement, as they where niche members.

* Deprecated ``np.deprecate`` and ``np.deprecate_with_doc`` has been removed 
  from the main namespace. Use ``DeprecationWarning`` instead.

* Deprecated ``np.safe_eval`` has been removed from the main namespace. 
  Use ``ast.literal_eval`` instead.

  (`gh-24376 <https://github.com/numpy/numpy/pull/24376>`__)

* ``np.find_common_type`` has been removed. Use ``numpy.promote_types`` or
  ``numpy.result_type`` instead. To achieve semantics for the ``scalar_types``
  argument, use ``numpy.result_type`` and pass ``0``, ``0.0``, or ``0j`` as a
  Python scalar instead.

* ``np.round_`` has been removed. Use ``np.round`` instead.

* ``np.nbytes`` has been removed. Use ``np.dtype(<dtype>).itemsize`` instead.

  (`gh-24477 <https://github.com/numpy/numpy/pull/24477>`__)

* ``np.compare_chararrays`` has been removed from the main namespace. 
  Use ``np.char.compare_chararrays`` instead.

* The ``charrarray`` in the main namespace has been deprecated. It can be imported
  without a deprecation warning from ``np.char.chararray`` for now,
  but we are planning to fully deprecate and remove ``chararray`` in the future.

* ``np.format_parser`` has been removed from the main namespace. 
  Use ``np.rec.format_parser`` instead.

  (`gh-24587 <https://github.com/numpy/numpy/pull/24587>`__)

* Support for seven data type string aliases has been removed from ``np.dtype``:
  ``int0``, ``uint0``, ``void0``, ``object0``, ``str0``, ``bytes0`` and ``bool8``.

  (`gh-24807 <https://github.com/numpy/numpy/pull/24807>`__)

* The experimental ``numpy.array_api`` submodule has been removed. Use the main
  ``numpy`` namespace for regular usage instead, or the separate
  ``array-api-strict`` package for the compliance testing use case for which
  ``numpy.array_api`` was mostly used.

  (`gh-25911 <https://github.com/numpy/numpy/pull/25911>`__)
```

[... lines omitted from this excerpt ...]

```rst
* ``np.trapz`` has been deprecated. Use ``np.trapezoid`` or a ``scipy.integrate`` function instead.

* ``np.in1d`` has been deprecated. Use ``np.isin`` instead.

* Alias ``np.row_stack`` has been deprecated. Use ``np.vstack`` directly.
```

---

# NumPy 2.0 migration guide: changes to namespaces

Source: https://raw.githubusercontent.com/numpy/numpy/v2.0.0/doc/source/numpy_2_0_migration_guide.rst (verbatim excerpt, fetched 2026-09-29)

```rst
Main namespace
--------------

About 100 members of the main ``np`` namespace have been deprecated, removed, or
moved to a new place. It was done to reduce clutter and establish only one way to
access a given attribute. The table below shows members that have been removed:

======================  =================================================================
removed member          migration guideline
======================  =================================================================
add_docstring           It's still available as ``np.lib.add_docstring``.
add_newdoc              It's still available as ``np.lib.add_newdoc``.
add_newdoc_ufunc        It's an internal function and doesn't have a replacement.
alltrue                 Use ``all`` instead.
asfarray                Use ``np.asarray`` with a float dtype instead.
byte_bounds             Now it's available under ``np.lib.array_utils.byte_bounds``
cast                    Use ``np.asarray(arr, dtype=dtype)`` instead.
cfloat                  Use ``np.complex128`` instead.
clongfloat              Use ``np.clongdouble`` instead.
compat                  There's no replacement, as Python 2 is no longer supported.
complex\_               Use ``np.complex128`` instead.
cumproduct              Use ``np.cumprod`` instead.
DataSource              It's still available as ``np.lib.npyio.DataSource``.
deprecate               Emit ``DeprecationWarning`` with ``warnings.warn`` directly,
                        or use ``typing.deprecated``.
deprecate_with_doc      Emit ``DeprecationWarning`` with ``warnings.warn`` directly,
                        or use ``typing.deprecated``.
disp                    Use your own printing function instead.
fastCopyAndTranspose    Use ``arr.T.copy()`` instead.
find_common_type        Use ``numpy.promote_types`` or ``numpy.result_type`` instead. 
                        To achieve semantics for the ``scalar_types`` argument, 
                        use ``numpy.result_type`` and pass the Python values ``0``, 
                        ``0.0``, or ``0j``.
get_array_wrap
float\_                 Use ``np.float64`` instead.
geterrobj               Use the np.errstate context manager instead.
Inf                     Use ``np.inf`` instead.
Infinity                Use ``np.inf`` instead.
infty                   Use ``np.inf`` instead.
issctype                Use ``issubclass(rep, np.generic)`` instead.
issubclass\_            Use ``issubclass`` builtin instead.
issubsctype             Use ``np.issubdtype`` instead.
mat                     Use ``np.asmatrix`` instead.
maximum_sctype          Use a specific dtype instead. You should avoid relying
                        on any implicit mechanism and select the largest dtype of
                        a kind explicitly in the code.
NaN                     Use ``np.nan`` instead.
nbytes                  Use ``np.dtype(<dtype>).itemsize`` instead.
NINF                    Use ``-np.inf`` instead.
NZERO                   Use ``-0.0`` instead.
longcomplex             Use ``np.clongdouble`` instead.
longfloat               Use ``np.longdouble`` instead.
lookfor                 Search NumPy's documentation directly.
obj2sctype              Use ``np.dtype(obj).type`` instead.
PINF                    Use ``np.inf`` instead.
product                 Use ``np.prod`` instead.
PZERO                   Use ``0.0`` instead.
recfromcsv              Use ``np.genfromtxt`` with comma delimiter instead.
recfromtxt              Use ``np.genfromtxt`` instead.
round\_                 Use ``np.round`` instead.
safe_eval               Use ``ast.literal_eval`` instead.
sctype2char             Use ``np.dtype(obj).char`` instead.
sctypes                 Access dtypes explicitly instead.
seterrobj               Use the np.errstate context manager instead.
set_numeric_ops         For the general case, use ``PyUFunc_ReplaceLoopBySignature``. 
                        For ndarray subclasses, define the ``__array_ufunc__`` method 
                        and override the relevant ufunc.
set_string_function     Use ``np.set_printoptions`` instead with a formatter 
                        for custom printing of NumPy objects.
singlecomplex           Use ``np.complex64`` instead.
string\_                Use ``np.bytes_`` instead.
sometrue                Use ``any`` instead.
source                  Use ``inspect.getsource`` instead.
tracemalloc_domain      It's now available from ``np.lib``.
unicode\_               Use ``np.str_`` instead.
who                     Use an IDE variable explorer or ``locals()`` instead.
======================  =================================================================

If the table doesn't contain an item that you were using but was removed in ``2.0``,
then it means it was a private member. You should either use the existing API or,
in case it's infeasible, reach out to us with a request to restore the removed entry.

The next table presents deprecated members, which will be removed in a release after ``2.0``:

================= =======================================================================
deprecated member migration guideline
================= =======================================================================
in1d              Use ``np.isin`` instead.
row_stack         Use ``np.vstack`` instead (``row_stack`` was an alias for ``vstack``).
trapz             Use ``np.trapezoid`` or a ``scipy.integrate`` function instead.
================= =======================================================================
```

[... lines omitted from this excerpt ...]

```rst
ndarray and scalar methods
--------------------------

A few methods from ``np.ndarray`` and ``np.generic`` scalar classes have been removed.
The table below provides replacements for the removed members:

======================  ========================================================
expired member          migration guideline
======================  ========================================================
newbyteorder            Use ``arr.view(arr.dtype.newbyteorder(order))`` instead.
ptp                     Use ``np.ptp(arr, ...)`` instead.
setitem                 Use ``arr[index] = value`` instead.
======================  ========================================================
```
