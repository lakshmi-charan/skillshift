# What's New In Python 3.13 -- section "Removed Modules And APIs"

Source: https://raw.githubusercontent.com/python/cpython/v3.13.0/Doc/whatsnew/3.13.rst (verbatim excerpt, fetched 2026-09-29)
License: Python documentation, Copyright Python Software Foundation, PSF License / Zero-Clause BSD for code examples (https://docs.python.org/3/license.html). Verbatim excerpt; reStructuredText markup preserved.

```rst
Removed Modules And APIs
========================


.. _whatsnew313-pep594:

PEP 594: Remove "dead batteries" from the standard library
----------------------------------------------------------

:pep:`594` proposed removing 19 modules from the standard library,
colloquially referred to as 'dead batteries' due to their
historic, obsolete, or insecure status.
All of the following modules were deprecated in Python 3.11,
and are now removed:

* :mod:`!aifc`
* :mod:`!audioop`
* :mod:`!chunk`
* :mod:`!cgi` and :mod:`!cgitb`

  * :class:`!cgi.FieldStorage` can typically be replaced with
    :func:`urllib.parse.parse_qsl` for ``GET`` and ``HEAD`` requests,
    and the :mod:`email.message` module or the :pypi:`multipart` library
    for ``POST`` and ``PUT`` requests.

  * :func:`!cgi.parse` can be replaced by calling
    :func:`urllib.parse.parse_qs` directly on the desired query string,
    unless the input is ``multipart/form-data``,
    which should be replaced as described below for :func:`!cgi.parse_multipart`.

  * :func:`!cgi.parse_header` can be replaced with the functionality
    in the :mod:`email` package, which implements the same MIME RFCs.
    For example, with :class:`email.message.EmailMessage`:

    .. code-block:: python

       from email.message import EmailMessage

       msg = EmailMessage()
       msg['content-type'] = 'application/json; charset="utf8"'
       main, params = msg.get_content_type(), msg['content-type'].params

  * :func:`!cgi.parse_multipart` can be replaced with the functionality
    in the :mod:`email` package, which implements the same MIME RFCs,
    or with the :pypi:`multipart` library.
    For example, the :class:`email.message.EmailMessage`
    and :class:`email.message.Message` classes.

* :mod:`!crypt` and the private :mod:`!_crypt` extension.
  The :mod:`hashlib` module may be an appropriate replacement
  when simply hashing a value is required.
  Otherwise, various third-party libraries on PyPI are available:

  * :pypi:`bcrypt`:
    Modern password hashing for your software and your servers.
  * :pypi:`passlib`:
    Comprehensive password hashing framework supporting over 30 schemes.
  * :pypi:`argon2-cffi`:
    The secure Argon2 password hashing algorithm.
  * :pypi:`legacycrypt`:
    :mod:`ctypes` wrapper to the POSIX crypt library call
    and associated functionality.
  * :pypi:`crypt_r`:
    Fork of the :mod:`!crypt` module,
    wrapper to the :manpage:`crypt_r(3)` library call
    and associated functionality.

* :mod:`!imghdr`:
  The :pypi:`filetype`, :pypi:`puremagic`, or :pypi:`python-magic` libraries
  should be used as replacements.
  For example, the :func:`!puremagic.what` function can be used
  to replace the :func:`!imghdr.what` function for all file formats
  that were supported by :mod:`!imghdr`.
* :mod:`!mailcap`:
  Use the :mod:`mimetypes` module instead.
* :mod:`!msilib`
* :mod:`!nis`
* :mod:`!nntplib`:
  Use the :pypi:`pynntp` library from PyPI instead.
* :mod:`!ossaudiodev`:
  For audio playback, use the :pypi:`pygame` library from PyPI instead.
* :mod:`!pipes`:
  Use the :mod:`subprocess` module instead.
* :mod:`!sndhdr`:
  The :pypi:`filetype`, :pypi:`puremagic`, or :pypi:`python-magic` libraries
  should be used as replacements.
* :mod:`!spwd`:
  Use the :pypi:`python-pam` library from PyPI instead.
* :mod:`!sunau`
* :mod:`!telnetlib`,
  Use the :pypi:`telnetlib3` or :pypi:`Exscript` libraries from PyPI instead.
* :mod:`!uu`:
  Use the :mod:`base64` module instead, as a modern alternative.
* :mod:`!xdrlib`

(Contributed by Victor Stinner and Zachary Ware in :gh:`104773` and :gh:`104780`.)


2to3
----

* Remove the :program:`2to3` program and the :mod:`!lib2to3` module,
  previously deprecated in Python 3.11.
  (Contributed by Victor Stinner in :gh:`104780`.)


builtins
--------

* Remove support for chained :class:`classmethod` descriptors
  (introduced in :gh:`63272`).
  These can no longer be used to wrap other descriptors,
  such as :class:`property`.
  The core design of this feature was flawed and led to several problems.
  To "pass-through" a :class:`classmethod`, consider using
  the :attr:`!__wrapped__` attribute that was added in Python 3.10.
  (Contributed by Raymond Hettinger in :gh:`89519`.)

* Raise a :exc:`RuntimeError` when calling :meth:`frame.clear`
  on a suspended frame (as has always been the case for an executing frame).
  (Contributed by Irit Katriel in :gh:`79932`.)


configparser
------------

* Remove the undocumented :class:`!LegacyInterpolation` class,
  deprecated in the docstring since Python 3.2,
  and at runtime since Python 3.11.
  (Contributed by Hugo van Kemenade in :gh:`104886`.)


importlib.metadata
------------------

* Remove deprecated subscript (:meth:`~object.__getitem__`) access for
  :ref:`EntryPoint <entry-points>` objects.
  (Contributed by Jason R. Coombs in :gh:`113175`.)


locale
------

* Remove the :func:`!locale.resetlocale` function, deprecated in Python 3.11.
  Use ``locale.setlocale(locale.LC_ALL, "")`` instead.
  (Contributed by Victor Stinner in :gh:`104783`.)


opcode
------

* Move :attr:`!opcode.ENABLE_SPECIALIZATION` to :attr:`!_opcode.ENABLE_SPECIALIZATION`.
  This field was added in 3.12, it was never documented,
  and is not intended for external use.
  (Contributed by Irit Katriel in :gh:`105481`.)

* Remove :func:`!opcode.is_pseudo`, :attr:`!opcode.MIN_PSEUDO_OPCODE`,
  and :attr:`!opcode.MAX_PSEUDO_OPCODE`, which were added in Python 3.12,
  but were neither documented nor exposed through :mod:`dis`,
  and were not intended to be used externally.
  (Contributed by Irit Katriel in :gh:`105481`.)


pathlib
-------

* Remove the ability to use :class:`~pathlib.Path` objects as context managers.
  This functionality was deprecated and has had no effect since Python 3.9.
  (Contributed by Barney Gale in :gh:`83863`.)


re
--

* Remove the undocumented, deprecated, and broken
  :func:`!re.template` function and :attr:`!re.TEMPLATE` / :attr:`!re.T` flag.
  (Contributed by Serhiy Storchaka and Nikita Sobolev in :gh:`105687`.)


tkinter.tix
-----------

* Remove the :mod:`!tkinter.tix` module, deprecated in Python 3.6.
  The third-party Tix library which the module wrapped is unmaintained.
  (Contributed by Zachary Ware in :gh:`75552`.)


turtle
------

* Remove the :meth:`!RawTurtle.settiltangle` method,
  deprecated in the documentation since Python 3.1
  and at runtime since Python 3.11.
  (Contributed by Hugo van Kemenade in :gh:`104876`.)


typing
------

* Remove the :mod:`!typing.io` and :mod:`!typing.re` namespaces,
  deprecated since Python 3.8.
  The items in those namespaces can be imported directly
  from the :mod:`typing` module.
  (Contributed by Sebastian Rittau in :gh:`92871`.)

* Remove the keyword-argument method of creating
  :class:`~typing.TypedDict` types, deprecated in Python 3.11.
  (Contributed by Tomas Roun in :gh:`104786`.)


unittest
--------

* Remove the following :mod:`unittest` functions, deprecated in Python 3.11:

  * :func:`!unittest.findTestCases`
  * :func:`!unittest.makeSuite`
  * :func:`!unittest.getTestCaseNames`

  Use :class:`~unittest.TestLoader` methods instead:

  * :meth:`~unittest.TestLoader.loadTestsFromModule`
  * :meth:`~unittest.TestLoader.loadTestsFromTestCase`
  * :meth:`~unittest.TestLoader.getTestCaseNames`

  (Contributed by Hugo van Kemenade in :gh:`104835`.)

* Remove the untested and undocumented :meth:`!TestProgram.usageExit`
  method, deprecated in Python 3.11.
  (Contributed by Hugo van Kemenade in :gh:`104992`.)


urllib
------

* Remove the *cafile*, *capath*, and *cadefault* parameters of the
  :func:`urllib.request.urlopen` function, deprecated in Python 3.6.
  Use the *context* parameter instead with an :class:`~ssl.SSLContext` instance.
  The :meth:`ssl.SSLContext.load_cert_chain` function
  can be used to load specific certificates,
  or let :func:`ssl.create_default_context` select
  the operating system's trusted certificate authority (CA) certificates.
  (Contributed by Victor Stinner in :gh:`105382`.)


webbrowser
----------

* Remove the untested and undocumented :class:`!MacOSX` class,
  deprecated in Python 3.11.
  Use the :class:`!MacOSXOSAScript` class (introduced in Python 3.2) instead.
  (Contributed by Hugo van Kemenade in :gh:`104804`.)

* Remove the deprecated :attr:`!MacOSXOSAScript._name` attribute.
  Use the :attr:`MacOSXOSAScript.name <webbrowser.controller.name>`
  attribute instead.
  (Contributed by Nikita Sobolev in :gh:`105546`.)
```
