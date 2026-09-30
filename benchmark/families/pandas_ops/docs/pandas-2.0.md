# pandas 2.0.0: What's new (removal of prior version deprecations)

Source: https://raw.githubusercontent.com/pandas-dev/pandas/v2.0.0/doc/source/whatsnew/v2.0.0.rst (verbatim excerpt, fetched 2026-09-29)

```rst
What's new in 2.0.0 (April 3, 2023)
-----------------------------------
```

[... lines omitted from this excerpt ...]

```rst
Removal of prior version deprecations/changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Removed :class:`Int64Index`, :class:`UInt64Index` and :class:`Float64Index`. See also :ref:`here <whatsnew_200.enhancements.index_can_hold_numpy_numeric_dtypes>` for more information (:issue:`42717`)
- Removed deprecated :attr:`Timestamp.freq`, :attr:`Timestamp.freqstr` and argument ``freq`` from the :class:`Timestamp` constructor and :meth:`Timestamp.fromordinal` (:issue:`14146`)
- Removed deprecated :class:`CategoricalBlock`, :meth:`Block.is_categorical`, require datetime64 and timedelta64 values to be wrapped in :class:`DatetimeArray` or :class:`TimedeltaArray` before passing to :meth:`Block.make_block_same_class`, require ``DatetimeTZBlock.values`` to have the correct ndim when passing to the :class:`BlockManager` constructor, and removed the "fastpath" keyword from the :class:`SingleBlockManager` constructor (:issue:`40226`, :issue:`40571`)
- Removed deprecated global option ``use_inf_as_null`` in favor of ``use_inf_as_na`` (:issue:`17126`)
- Removed deprecated module ``pandas.core.index`` (:issue:`30193`)
- Removed deprecated alias ``pandas.core.tools.datetimes.to_time``, import the function directly from ``pandas.core.tools.times`` instead (:issue:`34145`)
- Removed deprecated alias ``pandas.io.json.json_normalize``, import the function directly from ``pandas.json_normalize`` instead (:issue:`27615`)
- Removed deprecated :meth:`Categorical.to_dense`, use ``np.asarray(cat)`` instead (:issue:`32639`)
- Removed deprecated :meth:`Categorical.take_nd` (:issue:`27745`)
- Removed deprecated :meth:`Categorical.mode`, use ``Series(cat).mode()`` instead (:issue:`45033`)
- Removed deprecated :meth:`Categorical.is_dtype_equal` and :meth:`CategoricalIndex.is_dtype_equal` (:issue:`37545`)
- Removed deprecated :meth:`CategoricalIndex.take_nd` (:issue:`30702`)
- Removed deprecated :meth:`Index.is_type_compatible` (:issue:`42113`)
- Removed deprecated :meth:`Index.is_mixed`, check ``index.inferred_type`` directly instead (:issue:`32922`)
- Removed deprecated :func:`pandas.api.types.is_categorical`; use :func:`pandas.api.types.is_categorical_dtype` instead  (:issue:`33385`)
- Removed deprecated :meth:`Index.asi8` (:issue:`37877`)
- Enforced deprecation changing behavior when passing ``datetime64[ns]`` dtype data and timezone-aware dtype to :class:`Series`, interpreting the values as wall-times instead of UTC times, matching :class:`DatetimeIndex` behavior (:issue:`41662`)
- Enforced deprecation changing behavior when applying a numpy ufunc on multiple non-aligned (on the index or columns) :class:`DataFrame` that will now align the inputs first (:issue:`39239`)
- Removed deprecated :meth:`DataFrame._AXIS_NUMBERS`, :meth:`DataFrame._AXIS_NAMES`, :meth:`Series._AXIS_NUMBERS`, :meth:`Series._AXIS_NAMES` (:issue:`33637`)
- Removed deprecated :meth:`Index.to_native_types`, use ``obj.astype(str)`` instead (:issue:`36418`)
- Removed deprecated :meth:`Series.iteritems`, :meth:`DataFrame.iteritems`, use ``obj.items`` instead (:issue:`45321`)
- Removed deprecated :meth:`DataFrame.lookup` (:issue:`35224`)
- Removed deprecated :meth:`Series.append`, :meth:`DataFrame.append`, use :func:`concat` instead (:issue:`35407`)
- Removed deprecated :meth:`Series.iteritems`, :meth:`DataFrame.iteritems` and :meth:`HDFStore.iteritems` use ``obj.items`` instead (:issue:`45321`)
- Removed deprecated :meth:`DatetimeIndex.union_many` (:issue:`45018`)
- Removed deprecated ``weekofyear`` and ``week`` attributes of :class:`DatetimeArray`, :class:`DatetimeIndex` and ``dt`` accessor in favor of ``isocalendar().week`` (:issue:`33595`)
- Removed deprecated :meth:`RangeIndex._start`, :meth:`RangeIndex._stop`, :meth:`RangeIndex._step`, use ``start``, ``stop``, ``step`` instead (:issue:`30482`)
- Removed deprecated :meth:`DatetimeIndex.to_perioddelta`, Use ``dtindex - dtindex.to_period(freq).to_timestamp()`` instead (:issue:`34853`)
- Removed deprecated :meth:`.Styler.hide_index` and :meth:`.Styler.hide_columns` (:issue:`49397`)
- Removed deprecated :meth:`.Styler.set_na_rep` and :meth:`.Styler.set_precision` (:issue:`49397`)
- Removed deprecated :meth:`.Styler.where` (:issue:`49397`)
- Removed deprecated :meth:`.Styler.render` (:issue:`49397`)
- Removed deprecated argument ``col_space`` in :meth:`DataFrame.to_latex` (:issue:`47970`)
- Removed deprecated argument ``null_color`` in :meth:`.Styler.highlight_null` (:issue:`49397`)
- Removed deprecated argument ``check_less_precise`` in :meth:`.testing.assert_frame_equal`, :meth:`.testing.assert_extension_array_equal`, :meth:`.testing.assert_series_equal`,  :meth:`.testing.assert_index_equal` (:issue:`30562`)
- Removed deprecated ``null_counts`` argument in :meth:`DataFrame.info`. Use ``show_counts`` instead (:issue:`37999`)
- Removed deprecated :meth:`Index.is_monotonic`, and :meth:`Series.is_monotonic`; use ``obj.is_monotonic_increasing`` instead (:issue:`45422`)
- Removed deprecated :meth:`Index.is_all_dates` (:issue:`36697`)
```

[... lines omitted from this excerpt ...]

```rst
- Enforced deprecation disallowing passing ``numeric_only=True`` to :class:`Series` reductions (``rank``, ``any``, ``all``, ...) with non-numeric dtype (:issue:`47500`)
- Changed behavior of :meth:`.DataFrameGroupBy.apply` and :meth:`.SeriesGroupBy.apply` so that ``group_keys`` is respected even if a transformer is detected (:issue:`34998`)
- Comparisons between a :class:`DataFrame` and a :class:`Series` where the frame's columns do not match the series's index raise ``ValueError`` instead of automatically aligning, do ``left, right = left.align(right, axis=1, copy=False)`` before comparing (:issue:`36795`)
- Enforced deprecation ``numeric_only=None`` (the default) in DataFrame reductions that would silently drop columns that raised; ``numeric_only`` now defaults to ``False`` (:issue:`41480`)
- Changed default of ``numeric_only`` to ``False`` in all DataFrame methods with that argument (:issue:`46096`, :issue:`46906`)
- Changed default of ``numeric_only`` to ``False`` in :meth:`Series.rank` (:issue:`47561`)
- Enforced deprecation of silently dropping nuisance columns in groupby and resample operations when ``numeric_only=False`` (:issue:`41475`)
- Enforced deprecation of silently dropping nuisance columns in :class:`Rolling`, :class:`Expanding`, and :class:`ExponentialMovingWindow` ops. This will now raise a :class:`.errors.DataError` (:issue:`42834`)
- Changed behavior in setting values with ``df.loc[:, foo] = bar`` or ``df.iloc[:, foo] = bar``, these now always attempt to set values inplace before falling back to casting (:issue:`45333`)
- Changed default of ``numeric_only`` in various :class:`.DataFrameGroupBy` methods; all methods now default to ``numeric_only=False`` (:issue:`46072`)
- Changed default of ``numeric_only`` to ``False`` in :class:`.Resampler` methods (:issue:`47177`)
```
