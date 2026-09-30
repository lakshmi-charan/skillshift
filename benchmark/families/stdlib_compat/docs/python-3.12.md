# What's New In Python 3.12 -- section "Removed"

Source: https://raw.githubusercontent.com/python/cpython/v3.12.0/Doc/whatsnew/3.12.rst (verbatim excerpt, fetched 2026-09-29)
License: Python documentation, Copyright Python Software Foundation, PSF License / Zero-Clause BSD for code examples (https://docs.python.org/3/license.html). Verbatim excerpt; reStructuredText markup preserved.
Subsections omitted from this excerpt: ssl.

```rst
Removed
=======

asynchat and asyncore
---------------------

* These two modules have been removed
  according to the schedule in :pep:`594`,
  having been deprecated in Python 3.6.
  Use :mod:`asyncio` instead.
  (Contributed by Nikita Sobolev in :gh:`96580`.)

configparser
------------

* Several names deprecated in the :mod:`configparser` way back in 3.2 have
  been removed per :gh:`89336`:

  * :class:`configparser.ParsingError` no longer has a ``filename`` attribute
    or argument. Use the ``source`` attribute and argument instead.
  * :mod:`configparser` no longer has a ``SafeConfigParser`` class. Use the
    shorter :class:`~configparser.ConfigParser` name instead.
  * :class:`configparser.ConfigParser` no longer has a ``readfp`` method.
    Use :meth:`~configparser.ConfigParser.read_file` instead.

distutils
---------

* Remove the :py:mod:`!distutils` package. It was deprecated in Python 3.10 by
  :pep:`632` "Deprecate distutils module". For projects still using
  ``distutils`` and cannot be updated to something else, the ``setuptools``
  project can be installed: it still provides ``distutils``.
  (Contributed by Victor Stinner in :gh:`92584`.)

ensurepip
---------

* Remove the bundled setuptools wheel from :mod:`ensurepip`,
  and stop installing setuptools in environments created by :mod:`venv`.

  ``pip (>= 22.1)`` does not require setuptools to be installed in the
  environment. ``setuptools``-based (and ``distutils``-based) packages
  can still be used with ``pip install``, since pip will provide
  ``setuptools`` in the build environment it uses for building a
  package.

  ``easy_install``, ``pkg_resources``, ``setuptools`` and ``distutils``
  are no longer provided by default in environments created with
  ``venv`` or bootstrapped with ``ensurepip``, since they are part of
  the ``setuptools`` package. For projects relying on these at runtime,
  the ``setuptools`` project should be declared as a dependency and
  installed separately (typically, using pip).

  (Contributed by Pradyun Gedam in :gh:`95299`.)

enum
----

* Remove :mod:`enum`'s ``EnumMeta.__getattr__``, which is no longer needed for
  enum attribute access.
  (Contributed by Ethan Furman in :gh:`95083`.)

ftplib
------

* Remove :mod:`ftplib`'s ``FTP_TLS.ssl_version`` class attribute: use the
  *context* parameter instead.
  (Contributed by Victor Stinner in :gh:`94172`.)

gzip
----

* Remove the ``filename`` attribute of :mod:`gzip`'s :class:`gzip.GzipFile`,
  deprecated since Python 2.6, use the :attr:`~gzip.GzipFile.name` attribute
  instead. In write mode, the ``filename`` attribute added ``'.gz'`` file
  extension if it was not present.
  (Contributed by Victor Stinner in :gh:`94196`.)

hashlib
-------

* Remove the pure Python implementation of :mod:`hashlib`'s
  :func:`hashlib.pbkdf2_hmac()`, deprecated in Python 3.10. Python 3.10 and
  newer requires OpenSSL 1.1.1 (:pep:`644`): this OpenSSL version provides
  a C implementation of :func:`~hashlib.pbkdf2_hmac()` which is faster.
  (Contributed by Victor Stinner in :gh:`94199`.)

importlib
---------

* Many previously deprecated cleanups in :mod:`importlib` have now been
  completed:

  * References to, and support for :meth:`!module_repr()` has been removed.
    (Contributed by Barry Warsaw in :gh:`97850`.)

  * ``importlib.util.set_package``, ``importlib.util.set_loader`` and
    ``importlib.util.module_for_loader`` have all been removed. (Contributed by
    Brett Cannon and Nikita Sobolev in :gh:`65961` and :gh:`97850`.)

  * Support for ``find_loader()`` and ``find_module()`` APIs have been
    removed.  (Contributed by Barry Warsaw in :gh:`98040`.)

  * ``importlib.abc.Finder``, ``pkgutil.ImpImporter``, and ``pkgutil.ImpLoader``
    have been removed.  (Contributed by Barry Warsaw in :gh:`98040`.)

imp
---

* The :mod:`!imp` module has been removed.  (Contributed by Barry Warsaw in
  :gh:`98040`.)

  To migrate, consult the following correspondence table:

    =================================  =======================================
       imp                                importlib
    =================================  =======================================
    ``imp.NullImporter``               Insert ``None`` into ``sys.path_importer_cache``
    ``imp.cache_from_source()``        :func:`importlib.util.cache_from_source`
    ``imp.find_module()``              :func:`importlib.util.find_spec`
    ``imp.get_magic()``                :attr:`importlib.util.MAGIC_NUMBER`
    ``imp.get_suffixes()``             :attr:`importlib.machinery.SOURCE_SUFFIXES`, :attr:`importlib.machinery.EXTENSION_SUFFIXES`, and :attr:`importlib.machinery.BYTECODE_SUFFIXES`
    ``imp.get_tag()``                  :attr:`sys.implementation.cache_tag <sys.implementation>`
    ``imp.load_module()``              :func:`importlib.import_module`
    ``imp.new_module(name)``           ``types.ModuleType(name)``
    ``imp.reload()``                   :func:`importlib.reload`
    ``imp.source_from_cache()``        :func:`importlib.util.source_from_cache`
    ``imp.load_source()``              *See below*
    =================================  =======================================

  Replace ``imp.load_source()`` with::

        import importlib.util
        import importlib.machinery

        def load_source(modname, filename):
            loader = importlib.machinery.SourceFileLoader(modname, filename)
            spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
            module = importlib.util.module_from_spec(spec)
            # The module is always executed and not cached in sys.modules.
            # Uncomment the following line to cache the module.
            # sys.modules[module.__name__] = module
            loader.exec_module(module)
            return module

* Remove :mod:`!imp` functions and attributes with no replacements:

  * Undocumented functions:

    * ``imp.init_builtin()``
    * ``imp.load_compiled()``
    * ``imp.load_dynamic()``
    * ``imp.load_package()``

  * ``imp.lock_held()``, ``imp.acquire_lock()``, ``imp.release_lock()``:
    the locking scheme has changed in Python 3.3 to per-module locks.
  * ``imp.find_module()`` constants: ``SEARCH_ERROR``, ``PY_SOURCE``,
    ``PY_COMPILED``, ``C_EXTENSION``, ``PY_RESOURCE``, ``PKG_DIRECTORY``,
    ``C_BUILTIN``, ``PY_FROZEN``, ``PY_CODERESOURCE``, ``IMP_HOOK``.

io
--

* Remove :mod:`io`'s ``io.OpenWrapper`` and ``_pyio.OpenWrapper``, deprecated in Python
  3.10: just use :func:`open` instead. The :func:`open` (:func:`io.open`)
  function is a built-in function. Since Python 3.10, :func:`!_pyio.open` is
  also a static method.
  (Contributed by Victor Stinner in :gh:`94169`.)

locale
------

* Remove :mod:`locale`'s :func:`!locale.format` function, deprecated in Python 3.7:
  use :func:`locale.format_string` instead.
  (Contributed by Victor Stinner in :gh:`94226`.)

* ``smtpd``: The module has been removed according to the schedule in :pep:`594`,
  having been deprecated in Python 3.4.7 and 3.5.4.
  Use aiosmtpd_ PyPI module or any other
  :mod:`asyncio`-based server instead.
  (Contributed by Oleg Iarygin in :gh:`93243`.)

.. _aiosmtpd: https://pypi.org/project/aiosmtpd/

sqlite3
-------

* The following undocumented :mod:`sqlite3` features, deprecated in Python
  3.10, are now removed:

  * ``sqlite3.enable_shared_cache()``
  * ``sqlite3.OptimizedUnicode``

  If a shared cache must be used, open the database in URI mode using the
  ``cache=shared`` query parameter.

  The ``sqlite3.OptimizedUnicode`` text factory has been an alias for
  :class:`str` since Python 3.3. Code that previously set the text factory to
  ``OptimizedUnicode`` can either use ``str`` explicitly, or rely on the
  default value which is also ``str``.

  (Contributed by Erlend E. Aasland in :gh:`92548`.)

unittest
--------

* Remove many long-deprecated :mod:`unittest` features:

  .. _unittest-TestCase-removed-aliases:

  * A number of :class:`~unittest.TestCase` method aliases:

    ============================ =============================== ===============
       Deprecated alias           Method Name                     Deprecated in
    ============================ =============================== ===============
     ``failUnless``               :meth:`.assertTrue`             3.1
     ``failIf``                   :meth:`.assertFalse`            3.1
     ``failUnlessEqual``          :meth:`.assertEqual`            3.1
     ``failIfEqual``              :meth:`.assertNotEqual`         3.1
     ``failUnlessAlmostEqual``    :meth:`.assertAlmostEqual`      3.1
     ``failIfAlmostEqual``        :meth:`.assertNotAlmostEqual`   3.1
     ``failUnlessRaises``         :meth:`.assertRaises`           3.1
     ``assert_``                  :meth:`.assertTrue`             3.2
     ``assertEquals``             :meth:`.assertEqual`            3.2
     ``assertNotEquals``          :meth:`.assertNotEqual`         3.2
     ``assertAlmostEquals``       :meth:`.assertAlmostEqual`      3.2
     ``assertNotAlmostEquals``    :meth:`.assertNotAlmostEqual`   3.2
     ``assertRegexpMatches``      :meth:`.assertRegex`            3.2
     ``assertRaisesRegexp``       :meth:`.assertRaisesRegex`      3.2
     ``assertNotRegexpMatches``   :meth:`.assertNotRegex`         3.5
    ============================ =============================== ===============

    You can use https://github.com/isidentical/teyit to automatically modernise
    your unit tests.

  * Undocumented and broken :class:`~unittest.TestCase` method
    ``assertDictContainsSubset`` (deprecated in Python 3.2).

  * Undocumented :meth:`TestLoader.loadTestsFromModule
    <unittest.TestLoader.loadTestsFromModule>` parameter *use_load_tests*
    (deprecated and ignored since Python 3.2).

  * An alias of the :class:`~unittest.TextTestResult` class:
    ``_TextTestResult`` (deprecated in Python 3.2).

  (Contributed by Serhiy Storchaka in :gh:`89325`.)

webbrowser
----------

* Remove support for obsolete browsers from :mod:`webbrowser`.
  The removed browsers include: Grail, Mosaic, Netscape, Galeon, Skipstone,
  Iceape, Firebird, and Firefox versions 35 and below (:gh:`102871`).

xml.etree.ElementTree
---------------------

* Remove the ``ElementTree.Element.copy()`` method of the
  pure Python implementation, deprecated in Python 3.10, use the
  :func:`copy.copy` function instead.  The C implementation of :mod:`xml.etree.ElementTree`
  has no ``copy()`` method, only a ``__copy__()`` method.
  (Contributed by Victor Stinner in :gh:`94383`.)

zipimport
---------

* Remove :mod:`zipimport`'s ``find_loader()`` and ``find_module()`` methods,
  deprecated in Python 3.10: use the ``find_spec()`` method instead.  See
  :pep:`451` for the rationale.
  (Contributed by Victor Stinner in :gh:`94379`.)

Others
------

* Remove the ``suspicious`` rule from the documentation :file:`Makefile` and
  :file:`Doc/tools/rstlint.py`, both in favor of `sphinx-lint
  <https://github.com/sphinx-contrib/sphinx-lint>`_.
  (Contributed by Julien Palard in :gh:`98179`.)

* Remove the *keyfile* and *certfile* parameters from the
  :mod:`ftplib`, :mod:`imaplib`, :mod:`poplib` and :mod:`smtplib` modules,
  and the *key_file*, *cert_file* and *check_hostname* parameters from the
  :mod:`http.client` module,
  all deprecated since Python 3.6. Use the *context* parameter
  (*ssl_context* in :mod:`imaplib`) instead.
  (Contributed by Victor Stinner in :gh:`94172`.)

.. _whatsnew312-porting-to-python312:
```
