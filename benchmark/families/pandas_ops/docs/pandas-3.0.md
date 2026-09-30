# pandas 3.0.0: What's new (string dtype, Copy-on-Write, removals)

Source: https://raw.githubusercontent.com/pandas-dev/pandas/v3.0.0/doc/source/whatsnew/v3.0.0.rst (verbatim excerpt, fetched 2026-09-29)

```rst
What's new in 3.0.0 (January 21, 2026)
--------------------------------------
```

[... lines omitted from this excerpt ...]

```rst
Dedicated string data type by default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Historically, pandas represented string columns with NumPy ``object`` data type.
This representation has numerous problems: it is not specific to strings (any
Python object can be stored in an ``object``-dtype array, not just strings) and
it is often not very efficient (both performance wise and for memory usage).

Starting with pandas 3.0, a dedicated string data type is enabled by default
(backed by PyArrow under the hood, if installed, otherwise falling back to being
backed by NumPy ``object``-dtype). This means that pandas will start inferring
columns containing string data as the new ``str`` data type when creating pandas
objects, such as in constructors or IO functions.

Old behavior:

.. code-block:: python

    >>> ser = pd.Series(["a", "b"])
    0    a
    1    b
    dtype: object

New behavior:

.. code-block:: python

    >>> ser = pd.Series(["a", "b"])
    0    a
    1    b
    dtype: str

The string data type that is used in these scenarios will mostly behave as NumPy
object would, including missing value semantics and general operations on these
columns.

The main characteristic of the new string data type:

- Inferred by default for string data (instead of object dtype)
- The ``str`` dtype can only hold strings (or missing values), in contrast to
  ``object`` dtype. (setitem with non string fails)
- The missing value sentinel is always ``NaN`` (``np.nan``) and follows the same
  missing value semantics as the other default dtypes.

Those intentional changes can have breaking consequences, for example when checking
for the ``.dtype`` being object dtype or checking the exact missing value sentinel.
See the :ref:`string_migration_guide` for more details on the behaviour changes
and how to adapt your code to the new default.

.. seealso::

    `PDEP-14: Dedicated string data type for pandas 3.0 <https://pandas.pydata.org/pdeps/0014-string-dtype.html>`__
```

[... lines omitted from this excerpt ...]

```rst
Consistent copy/view behaviour with Copy-on-Write
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The new "copy-on-write" behaviour in pandas 3.0 brings changes in behavior in
how pandas operates with respect to copies and views. A summary of the changes:

1. The result of *any* indexing operation (subsetting a DataFrame or Series in any way,
   i.e. including accessing a DataFrame column as a Series) or any method returning a
   new DataFrame or Series, always *behaves as if* it were a copy in terms of user
   API.
2. As a consequence, if you want to modify an object (DataFrame or Series), the only way
   to do this is to directly modify that object itself.

The main goal of this change is to make the user API more consistent and
predictable. There is now a clear rule: *any* subset or returned
series/dataframe **always** behaves as a copy of the original, and thus never
modifies the original (before pandas 3.0, whether a derived object would be a
copy or a view depended on the exact operation performed, which was often
confusing).

Because every single indexing step now behaves as a copy, this also means that
**"chained assignment"** (updating a DataFrame with multiple setitem steps)
**will stop working**. Because this now consistently never works, the
``SettingWithCopyWarning`` is removed,  and defensive ``.copy()`` calls to
silence the warning are no longer needed.

The new behavioral semantics are explained in more detail in the
:ref:`user guide about Copy-on-Write <copy_on_write>`.

A secondary goal is to improve performance by avoiding unnecessary copies. As
mentioned above, every new DataFrame or Series returned from an indexing
operation or method *behaves* as a copy, but under the hood pandas will use
views as much as possible, and only copy when needed to guarantee the "behaves
as a copy" behaviour (this is the actual "copy-on-write" mechanism used as an
implementation detail).

Some of the behaviour changes described above are breaking changes in pandas
3.0. When upgrading to pandas 3.0, it is recommended to first upgrade to pandas
2.3 to get deprecation warnings for a subset of those changes. The
:ref:`migration guide <copy_on_write.migration_guide>` explains the upgrade
process in more detail.

.. seealso::

    `PDEP-7: Consistent copy/view semantics in pandas with Copy-on-Write <https://pandas.pydata.org/pdeps/0007-copy-on-write.html>`__

Setting the option ``mode.copy_on_write`` no longer has any impact. The option is deprecated
and will be removed in pandas 4.0.
```

[... lines omitted from this excerpt ...]

```rst
Removal of prior version deprecations/changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enforced deprecation of aliases ``M``, ``Q``, ``Y``, etc. in favour of ``ME``, ``QE``, ``YE``, etc. for offsets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Renamed the following offset aliases (:issue:`57986`):

+-------------------------------+------------------+------------------+
| offset                        | removed alias    | new alias        |
+===============================+==================+==================+
|:class:`MonthEnd`              |      ``M``       |     ``ME``       |
+-------------------------------+------------------+------------------+
|:class:`BusinessMonthEnd`      |      ``BM``      |     ``BME``      |
+-------------------------------+------------------+------------------+
|:class:`SemiMonthEnd`          |      ``SM``      |     ``SME``      |
+-------------------------------+------------------+------------------+
|:class:`CustomBusinessMonthEnd`|      ``CBM``     |     ``CBME``     |
+-------------------------------+------------------+------------------+
|:class:`QuarterEnd`            |      ``Q``       |     ``QE``       |
+-------------------------------+------------------+------------------+
|:class:`BQuarterEnd`           |      ``BQ``      |     ``BQE``      |
+-------------------------------+------------------+------------------+
|:class:`YearEnd`               |      ``Y``       |     ``YE``       |
+-------------------------------+------------------+------------------+
|:class:`BYearEnd`              |      ``BY``      |     ``BYE``      |
+-------------------------------+------------------+------------------+
```

[... lines omitted from this excerpt ...]

```rst
Other Removals
^^^^^^^^^^^^^^
- :meth:`.DataFrameGroupBy.idxmin`, :meth:`.DataFrameGroupBy.idxmax`, :meth:`.SeriesGroupBy.idxmin`, and :meth:`.SeriesGroupBy.idxmax` will now raise a ``ValueError`` when a group has all NA values, or when used with ``skipna=False`` and any NA value is encountered (:issue:`10694`, :issue:`57745`)
- :func:`concat` no longer ignores empty objects when determining output dtypes (:issue:`39122`)
- :func:`concat` with all-NA entries no longer ignores the dtype of those entries when determining the result dtype (:issue:`40893`)
- :func:`read_excel`, :func:`read_json`, :func:`read_html`, and :func:`read_xml` no longer accept raw string or byte representation of the data. That type of data must be wrapped in a :py:class:`StringIO` or :py:class:`BytesIO` (:issue:`53767`)
```

[... lines omitted from this excerpt ...]

```rst
- Enforced deprecation of string ``A`` denoting frequency in :class:`.YearEnd` and strings ``A-DEC``, ``A-JAN``, etc. denoting annual frequencies with various fiscal year ends (:issue:`57699`)
- Enforced deprecation of string ``BAS`` denoting frequency in :class:`.BYearBegin` and strings ``BAS-DEC``, ``BAS-JAN``, etc. denoting annual frequencies with various fiscal year starts (:issue:`57793`)
- Enforced deprecation of string ``BA`` denoting frequency in :class:`.BYearEnd` and strings ``BA-DEC``, ``BA-JAN``, etc. denoting annual frequencies with various fiscal year ends (:issue:`57793`)
- Enforced deprecation of strings ``H``, ``BH``, and ``CBH`` denoting frequencies in :class:`.Hour`, :class:`.BusinessHour`, :class:`.CustomBusinessHour` (:issue:`59143`)
- Enforced deprecation of strings ``H``, ``BH``, and ``CBH`` denoting units in :class:`Timedelta` (:issue:`59143`)
- Enforced deprecation of strings ``T``, ``L``, ``U``, and ``N`` denoting frequencies in :class:`Minute`, :class:`Milli`, :class:`Micro`, :class:`Nano` (:issue:`57627`)
- Enforced deprecation of strings ``T``, ``L``, ``U``, and ``N`` denoting units in :class:`Timedelta` (:issue:`57627`)
```

[... lines omitted from this excerpt ...]

```rst
- Removed :meth:`DateOffset.is_anchored` and :meth:`offsets.Tick.is_anchored` (:issue:`56594`)
- Removed ``DataFrame.applymap``, ``Styler.applymap`` and ``Styler.applymap_index`` (:issue:`52364`)
- Removed ``DataFrame.bool`` and ``Series.bool`` (:issue:`51756`)
- Removed ``DataFrame.first`` and ``DataFrame.last`` (:issue:`53710`)
- Removed ``DataFrame.swapaxes`` and ``Series.swapaxes`` (:issue:`51946`)
```
