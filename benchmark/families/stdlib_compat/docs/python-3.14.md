# What's New In Python 3.14 -- section "Removed"

Source: https://raw.githubusercontent.com/python/cpython/v3.14.0/Doc/whatsnew/3.14.rst (verbatim excerpt, fetched 2026-09-29)
License: Python documentation, Copyright Python Software Foundation, PSF License / Zero-Clause BSD for code examples (https://docs.python.org/3/license.html). Verbatim excerpt; reStructuredText markup preserved.

```rst
Removed
=======

argparse
--------

* Remove the *type*, *choices*, and *metavar* parameters
  of :class:`!BooleanOptionalAction`.
  These have been deprecated since Python 3.12.
  (Contributed by Nikita Sobolev in :gh:`118805`.)

* Calling :meth:`~argparse.ArgumentParser.add_argument_group`
  on an argument group now raises a :exc:`ValueError`.
  Similarly, :meth:`~argparse.ArgumentParser.add_argument_group`
  or :meth:`~argparse.ArgumentParser.add_mutually_exclusive_group`
  on a mutually exclusive group now both raise :exc:`ValueError`\ s.
  This 'nesting' was never supported, often failed to work correctly,
  and was unintentionally exposed through inheritance.
  This functionality has been deprecated since Python 3.11.
  (Contributed by Savannah Ostrowski in :gh:`127186`.)


ast
---

* Remove the following classes, which have been deprecated aliases of
  :class:`~ast.Constant` since Python 3.8 and have emitted
  deprecation warnings since Python 3.12:

  * :class:`!Bytes`
  * :class:`!Ellipsis`
  * :class:`!NameConstant`
  * :class:`!Num`
  * :class:`!Str`

  As a consequence of these removals, user-defined ``visit_Num``, ``visit_Str``,
  ``visit_Bytes``, ``visit_NameConstant`` and ``visit_Ellipsis`` methods
  on custom :class:`~ast.NodeVisitor` subclasses will no longer be called
  when the :class:`!NodeVisitor` subclass is visiting an AST.
  Define a ``visit_Constant`` method instead.

  (Contributed by Alex Waygood in :gh:`119562`.)

* Remove the following deprecated properties on :class:`ast.Constant`,
  which were present for compatibility with the now-removed AST classes:

  * :attr:`!Constant.n`
  * :attr:`!Constant.s`

  Use :attr:`!Constant.value` instead.
  (Contributed by Alex Waygood in :gh:`119562`.)


asyncio
-------

* Remove the following classes, methods, and functions,
  which have been deprecated since Python 3.12:

  * :class:`!AbstractChildWatcher`
  * :class:`!FastChildWatcher`
  * :class:`!MultiLoopChildWatcher`
  * :class:`!PidfdChildWatcher`
  * :class:`!SafeChildWatcher`
  * :class:`!ThreadedChildWatcher`
  * :meth:`!AbstractEventLoopPolicy.get_child_watcher`
  * :meth:`!AbstractEventLoopPolicy.set_child_watcher`
  * :func:`!get_child_watcher`
  * :func:`!set_child_watcher`

  (Contributed by Kumar Aditya in :gh:`120804`.)

* :func:`asyncio.get_event_loop` now raises a :exc:`RuntimeError`
  if there is no current event loop,
  and no longer implicitly creates an event loop.

  (Contributed by Kumar Aditya in :gh:`126353`.)

  .. TODO: move these patterns to the asyncio docs?
           quite long for What's New

  There's a few patterns that use :func:`asyncio.get_event_loop`, most
  of them can be replaced with :func:`asyncio.run`.

  If you're running an async function, simply use :func:`asyncio.run`.

  Before:

  .. code:: python

     async def main():
         ...


     loop = asyncio.get_event_loop()
     try:
         loop.run_until_complete(main())
     finally:
         loop.close()

  After:

  .. code:: python

    async def main():
        ...

    asyncio.run(main())

  If you need to start something, for example, a server listening on a socket
  and then run forever, use :func:`asyncio.run` and an
  :class:`asyncio.Event`.

  Before:

  .. code:: python

     def start_server(loop): ...

     loop = asyncio.get_event_loop()
     try:
         start_server(loop)
         loop.run_forever()
     finally:
         loop.close()

  After:

  .. code:: python

     def start_server(loop): ...

     async def main():
         start_server(asyncio.get_running_loop())
         await asyncio.Event().wait()

     asyncio.run(main())

  If you need to run something in an event loop, then run some blocking
  code around it, use :class:`asyncio.Runner`.

  Before:

  .. code:: python

     async def operation_one(): ...
     def blocking_code(): ...
     async def operation_two(): ...

     loop = asyncio.get_event_loop()
     try:
         loop.run_until_complete(operation_one())
         blocking_code()
         loop.run_until_complete(operation_two())
     finally:
         loop.close()

  After:

  .. code:: python

     async def operation_one(): ...
     def blocking_code(): ...
     async def operation_two(): ...

     with asyncio.Runner() as runner:
         runner.run(operation_one())
         blocking_code()
         runner.run(operation_two())


email
-----

* Remove :func:`email.utils.localtime`'s *isdst* parameter,
  which was deprecated in and has been ignored since Python 3.12.
  (Contributed by Hugo van Kemenade in :gh:`118798`.)


importlib.abc
-------------

* Remove deprecated :mod:`importlib.abc` classes:

  * :class:`!ResourceReader`
    (use :class:`~importlib.resources.abc.TraversableResources`)
  * :class:`!Traversable`
    (use :class:`~importlib.resources.abc.Traversable`)
  * :class:`!TraversableResources`
    (use :class:`~importlib.resources.abc.TraversableResources`)

  (Contributed by Jason R. Coombs and Hugo van Kemenade in :gh:`93963`.)


itertools
---------

* Remove support for copy, deepcopy, and pickle operations
  from :mod:`itertools` iterators.
  These have emitted a :exc:`DeprecationWarning` since Python 3.12.
  (Contributed by Raymond Hettinger in :gh:`101588`.)


pathlib
-------

* Remove support for passing additional keyword arguments
  to :class:`~pathlib.Path`.
  In previous versions, any such arguments are ignored.
  (Contributed by Barney Gale in :gh:`74033`.)

* Remove support for passing additional positional arguments to
  :meth:`.PurePath.relative_to` and :meth:`~pathlib.PurePath.is_relative_to`.
  In previous versions, any such arguments are joined onto *other*.
  (Contributed by Barney Gale in :gh:`78707`.)


pkgutil
-------

* Remove the :func:`!get_loader` and :func:`!find_loader` functions,
  which have been deprecated since Python 3.12.
  (Contributed by Bénédikt Tran in :gh:`97850`.)


pty
---

* Remove the :func:`!master_open` and :func:`!slave_open` functions,
  which have been deprecated since Python 3.12.
  Use :func:`pty.openpty` instead.
  (Contributed by Nikita Sobolev in :gh:`118824`.)


sqlite3
-------

* Remove :data:`!version` and :data:`!version_info` from
  the :mod:`sqlite3` module;
  use :data:`~sqlite3.sqlite_version` and :data:`~sqlite3.sqlite_version_info`
  for the actual version number of the runtime SQLite library.
  (Contributed by Hugo van Kemenade in :gh:`118924`.)

* Using a sequence of parameters with named placeholders now
  raises a :exc:`~sqlite3.ProgrammingError`,
  having been deprecated since Python 3.12.
  (Contributed by Erlend E. Aasland in :gh:`118928` and :gh:`101693`.)


urllib
------

* Remove the :class:`!Quoter` class from :mod:`urllib.parse`,
  which has been deprecated since Python 3.11.
  (Contributed by Nikita Sobolev in :gh:`118827`.)

* Remove the :class:`!URLopener` and :class:`!FancyURLopener` classes
  from :mod:`urllib.request`,
  which have been deprecated since Python 3.3.

  ``myopener.open()`` can be replaced with :func:`~urllib.request.urlopen`.
  ``myopener.retrieve()`` can be replaced with
  :func:`~urllib.request.urlretrieve`.
  Customisations to the opener classes can be replaced by passing
  customized handlers to :func:`~urllib.request.build_opener`.
  (Contributed by Barney Gale in :gh:`84850`.)
```
