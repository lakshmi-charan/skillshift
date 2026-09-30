# What's New In Python 3.12: ssl-related removals

Source: https://raw.githubusercontent.com/python/cpython/v3.12.0/Doc/whatsnew/3.12.rst
Fetched: 2026-09-29
License: CPython documentation, PSF License / Zero-Clause BSD for code. Verbatim excerpt.

Verbatim excerpt of the "Removed" section (subsections ssl, ftplib and Others).

```rst
Removed
=======

ssl
---

* Remove :mod:`ssl`'s :func:`!ssl.RAND_pseudo_bytes` function, deprecated in Python 3.6:
  use :func:`os.urandom` or :func:`ssl.RAND_bytes` instead.
  (Contributed by Victor Stinner in :gh:`94199`.)

* Remove the :func:`!ssl.match_hostname` function.
  It was deprecated in Python 3.7. OpenSSL performs
  hostname matching since Python 3.7, Python no longer uses the
  :func:`!ssl.match_hostname` function.
  (Contributed by Victor Stinner in :gh:`94199`.)

* Remove the :func:`!ssl.wrap_socket` function, deprecated in Python 3.7:
  instead, create a :class:`ssl.SSLContext` object and call its
  :class:`ssl.SSLContext.wrap_socket` method. Any package that still uses
  :func:`!ssl.wrap_socket` is broken and insecure. The function neither sends a
  SNI TLS extension nor validates server hostname. Code is subject to `CWE-295
  <https://cwe.mitre.org/data/definitions/295.html>`_: Improper Certificate
  Validation.
  (Contributed by Victor Stinner in :gh:`94199`.)

ftplib
------

* Remove :mod:`ftplib`'s ``FTP_TLS.ssl_version`` class attribute: use the
  *context* parameter instead.
  (Contributed by Victor Stinner in :gh:`94172`.)

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

```
