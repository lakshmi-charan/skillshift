# SQLAlchemy 2.0 - Major Migration Guide (selected sections)

Sources (verbatim excerpts, fetched 2026-09-29):
- https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_0_0/doc/build/changelog/migration_20.rst
- https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_0_0/doc/build/changelog/migration_14.rst (section referenced by the 2.0 guide for the Row API; last part of this document)
License: SQLAlchemy documentation, MIT License (https://github.com/sqlalchemy/sqlalchemy). Verbatim excerpt.

Sections are cut programmatically; the rationale ("**Discussion**") paragraphs are omitted.

```rst
Library-level (but not driver level) "Autocommit" removed from both Core and ORM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

In SQLAlchemy 1.x, the following statements will automatically commit
the underlying DBAPI transaction, but in SQLAlchemy
2.0 this will not occur::

    conn = engine.connect()

    # won't autocommit in 2.0
    conn.execute(some_table.insert().values(foo="bar"))

Nor will this autocommit::

    conn = engine.connect()

    # won't autocommit in 2.0
    conn.execute(text("INSERT INTO table (foo) VALUES ('bar')"))

The common workaround for custom DML that requires commit, the "autocommit"
execution option, will be removed::


    conn = engine.connect()

    # won't autocommit in 2.0
    conn.execute(text("EXEC my_procedural_thing()").execution_options(autocommit=True))

**Migration to 2.0**

The method that is cross-compatible with :term:`1.x style` and :term:`2.0
style` execution is to make use of the :meth:`_engine.Connection.begin` method,
or the :meth:`_engine.Engine.begin` context manager::

    with engine.begin() as conn:
        conn.execute(some_table.insert().values(foo="bar"))
        conn.execute(some_other_table.insert().values(bat="hoho"))

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(some_table.insert().values(foo="bar"))
            conn.execute(some_other_table.insert().values(bat="hoho"))

    with engine.begin() as conn:
        conn.execute(text("EXEC my_procedural_thing()"))

When using :term:`2.0 style` with the :paramref:`_sa.create_engine.future`
flag, "commit as you go" style may also be used, as the
:class:`_engine.Connection` features **autobegin** behavior, which takes place
when a statement is first invoked in the absence of an explicit call to
:meth:`_engine.Connection.begin`::

    with engine.connect() as conn:
        conn.execute(some_table.insert().values(foo="bar"))
        conn.execute(some_other_table.insert().values(bat="hoho"))

        conn.commit()

When :ref:`2.0 deprecations mode <migration_20_deprecations_mode>` is enabled,
a warning will emit when the deprecated "autocommit" feature takes place,
indicating those places where an explicit transaction should be noted.


"Implicit" and "Connectionless" execution, "bound metadata" removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

The ability to associate an :class:`_engine.Engine` with a :class:`_schema.MetaData`
object, which then makes available a range of so-called "connectionless"
execution patterns, is removed::

    from sqlalchemy import MetaData

    metadata_obj = MetaData(bind=engine)  # no longer supported

    metadata_obj.create_all()  # requires Engine or Connection

    metadata_obj.reflect()  # requires Engine or Connection

    t = Table("t", metadata_obj, autoload=True)  # use autoload_with=engine

    result = engine.execute(t.select())  # no longer supported

    result = t.select().execute()  # no longer supported

**Migration to 2.0**

For schema level patterns, explicit use of an :class:`_engine.Engine`
or :class:`_engine.Connection` is required.   The :class:`_engine.Engine`
may still be used directly as the source of connectivity for a
:meth:`_schema.MetaData.create_all` operation or autoload operation.
For executing statements, only the :class:`_engine.Connection` object
has a :meth:`_engine.Connection.execute` method (in addition to
the ORM-level :meth:`_orm.Session.execute` method)::


    from sqlalchemy import MetaData

    metadata_obj = MetaData()

    # engine level:

    # create tables
    metadata_obj.create_all(engine)

    # reflect all tables
    metadata_obj.reflect(engine)

    # reflect individual table
    t = Table("t", metadata_obj, autoload_with=engine)


    # connection level:


    with engine.connect() as connection:
        # create tables, requires explicit begin and/or commit:
        with connection.begin():
            metadata_obj.create_all(connection)

        # reflect all tables
        metadata_obj.reflect(connection)

        # reflect individual table
        t = Table("t", metadata_obj, autoload_with=connection)

        # execute SQL statements
        result = conn.execute(t.select())


execute() method more strict, execution options are more prominent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

The argument patterns that may be used with the :meth:`_engine.Connection`
execute method in SQLAlchemy 2.0 are highly simplified, removing many previously
available argument patterns.  The new API in the 1.4 series is described at
:meth:`_engine.Connection`. The examples below illustrate the patterns that
require modification::


    connection = engine.connect()

    # direct string SQL not supported; use text() or exec_driver_sql() method
    result = connection.execute("select * from table")

    # positional parameters no longer supported, only named
    # unless using exec_driver_sql()
    result = connection.execute(table.insert(), ("x", "y", "z"))

    # **kwargs no longer accepted, pass a single dictionary
    result = connection.execute(table.insert(), x=10, y=5)

    # multiple *args no longer accepted, pass a list
    result = connection.execute(
        table.insert(), {"x": 10, "y": 5}, {"x": 15, "y": 12}, {"x": 9, "y": 8}
    )

**Migration to 2.0**

The new :meth:`_engine.Connection.execute` method now accepts a subset of the
argument styles that are accepted by the 1.x :meth:`_engine.Connection.execute`
method, so the following code is cross-compatible between 1.x and 2.0::


    connection = engine.connect()

    from sqlalchemy import text

    result = connection.execute(text("select * from table"))

    # pass a single dictionary for single statement execution
    result = connection.execute(table.insert(), {"x": 10, "y": 5})

    # pass a list of dictionaries for executemany
    result = connection.execute(
        table.insert(), [{"x": 10, "y": 5}, {"x": 15, "y": 12}, {"x": 9, "y": 8}]
    )


Result rows act like named tuples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

Version 1.4 introduces an :ref:`all new Result object <change_result_14_core>`
that in turn returns :class:`_engine.Row` objects, which behave like named
tuples when using "future" mode::

    engine = create_engine(..., future=True)  # using future mode

    with engine.connect() as conn:
        result = conn.execute(text("select x, y from table"))

        row = result.first()  # suppose the row is (1, 2)

        "x" in row  # evaluates to False, in 1.x / future=False, this would be True

        1 in row  # evaluates to True, in 1.x / future=False, this would be False

**Migration to 2.0**

Application code or test suites that are testing for a particular key
being present in a row would need to test the ``row.keys()`` collection
instead.  This is however an unusual use case as a result row is typically
used by code that already knows what columns are present within it.


select() no longer accepts varied constructor arguments, columns are passed positionally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**synopsis**

The :func:`_sql.select` construct as well as the related method :meth:`_sql.FromClause.select`
will no longer accept keyword arguments to build up elements such as the
WHERE clause, FROM list and ORDER BY.   The list of columns may now be
sent positionally, rather than as a list.  Additionally, the :func:`_sql.case` construct
now accepts its WHEN criteria positionally, rather than as a list::

    # select_from / order_by keywords no longer supported
    stmt = select([1], select_from=table, order_by=table.c.id)

    # whereclause parameter no longer supported
    stmt = select([table.c.x], table.c.id == 5)

    # whereclause parameter no longer supported
    stmt = table.select(table.c.id == 5)

    # list emits a deprecation warning
    stmt = select([table.c.x, table.c.y])

    # list emits a deprecation warning
    case_clause = case(
        [(table.c.x == 5, "five"), (table.c.x == 7, "seven")],
        else_="neither five nor seven",
    )

**Migration to 2.0**

Only the "generative" style of :func:`_sql.select` will be supported.  The list
of columns / tables to SELECT from should be passed positionally.  The
:func:`_sql.select` construct in SQLAlchemy 1.4 accepts both the legacy
styles and the new styles using an auto-detection scheme, so the code below
is cross-compatible with 1.4 and 2.0::

    # use generative methods
    stmt = select(1).select_from(table).order_by(table.c.id)

    # use generative methods
    stmt = select(table).where(table.c.id == 5)

    # use generative methods
    stmt = table.select().where(table.c.id == 5)

    # pass columns clause expressions positionally
    stmt = select(table.c.x, table.c.y)

    # case conditions passed positionally
    case_clause = case(
        (table.c.x == 5, "five"), (table.c.x == 7, "seven"), else_="neither five nor seven"
    )


ORM Query  - Joining / loading on relationships uses attributes, not strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

This refers to patterns such as that of :meth:`_query.Query.join` as well as
query options like :func:`_orm.joinedload` which currently accept a mixture of
string attribute names or actual class attributes.   The string forms
will all be removed in 2.0::

    # string use removed
    q = session.query(User).join("addresses")

    # string use removed
    q = session.query(User).options(joinedload("addresses"))

    # string use removed
    q = session.query(Address).filter(with_parent(u1, "addresses"))

**Migration to 2.0**

Modern SQLAlchemy 1.x versions support the recommended technique which
is to use mapped attributes::

    # compatible with all modern SQLAlchemy versions

    q = session.query(User).join(User.addresses)

    q = session.query(User).options(joinedload(User.addresses))

    q = session.query(Address).filter(with_parent(u1, User.addresses))

The same techniques apply to :term:`2.0-style` style use::

    # SQLAlchemy 1.4 / 2.0 cross compatible use

    stmt = select(User).join(User.addresses)
    result = session.execute(stmt)

    stmt = select(User).options(joinedload(User.addresses))
    result = session.execute(stmt)

    stmt = select(Address).where(with_parent(u1, User.addresses))
    result = session.execute(stmt)


Session "subtransaction" behavior removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Synopsis**

The "subtransaction" pattern that was often used with autocommit mode is
also deprecated in 1.4.  This pattern allowed the use of the
:meth:`_orm.Session.begin` method when a transaction were already begun,
resulting in a construct called a "subtransaction", which was essentially
a block that would prevent the :meth:`_orm.Session.commit` method from actually
committing.

**Migration to 2.0**


To provide backwards compatibility for applications that make use of this
pattern, the following context manager or a similar implementation based on
a decorator may be used::


    import contextlib


    @contextlib.contextmanager
    def transaction(session):
        if not session.in_transaction():
            with session.begin():
                yield
        else:
            yield

The above context manager may be used in the same way the
"subtransaction" flag works, such as in the following example::


    # method_a starts a transaction and calls method_b
    def method_a(session):
        with transaction(session):
            method_b(session)


    # method_b also starts a transaction, but when
    # called from method_a participates in the ongoing
    # transaction.
    def method_b(session):
        with transaction(session):
            session.add(SomeObject("bat", "lala"))


    Session = sessionmaker(engine)

    # create a Session and call method_a
    with Session() as session:
        method_a(session)

To compare towards the preferred idiomatic pattern, the begin block should
be at the outermost level.  This removes the need for individual functions
or methods to be concerned with the details of transaction demarcation::

    def method_a(session):
        method_b(session)


    def method_b(session):
        session.add(SomeObject("bat", "lala"))


    Session = sessionmaker(engine)

    # create a Session and call method_a
    with Session() as session:
        with session.begin():
            method_a(session)
```

## From "What's New in SQLAlchemy 1.4?" (migration_14.rst)

```rst
RowProxy is no longer a "proxy"; is now called Row and behaves like an enhanced named tuple
-------------------------------------------------------------------------------------------

The :class:`.RowProxy` class, which represents individual database result rows
in a Core result set, is now called :class:`.Row` and is no longer a "proxy"
object; what this means is that when the :class:`.Row` object is returned, the
row is a simple tuple that contains the data in its final form, already having
been processed by result-row handling functions associated with datatypes
(examples include turning a date string from the database into a ``datetime``
object, a JSON string into a Python ``json.loads()`` result, etc.).

The immediate rationale for this is so that the row can act more like a Python
named tuple, rather than a mapping, where the values in the tuple are the
subject of the ``__contains__`` operator on the tuple, rather than the keys.
With :class:`.Row` acting like a named tuple, it is then suitable for use as as
replacement for the ORM's :class:`.KeyedTuple` object, leading to an eventual
API where both the ORM and Core deliver result sets that  behave identically.
Unification of major patterns within ORM and Core is a major goal of SQLAlchemy
2.0, and release 1.4 aims to have most or all of the underlying architectural
patterns in place in order to support this process.   The note in
:ref:`change_4710_orm` describes the ORM's use of the :class:`.Row` class.

For release 1.4, the :class:`.Row` class provides an additional subclass
``LegacyRow``, which is used by Core and provides a backwards-compatible
version of :class:`.RowProxy` while emitting deprecation warnings for those API
features and behaviors that will be moved.  ORM :class:`_query.Query` now makes use
of :class:`.Row` directly as a replacement for :class:`.KeyedTuple`.

The ``LegacyRow`` class is a transitional class where the
``__contains__`` method is still testing against the keys, not the values,
while emitting a deprecation warning when the operation succeeds.
Additionally, all the other mapping-like methods on the previous
:class:`.RowProxy` are deprecated, including ``LegacyRow.keys()``,
``LegacyRow.items()``, etc.  For mapping-like behaviors from a :class:`.Row`
object, including support for these methods as well as a key-oriented
``__contains__`` operator, the API going forward will be to first access a
special attribute :attr:`.Row._mapping`, which will then provide a complete
mapping interface to the row, rather than a tuple interface.

Rationale: To behave more like a named tuple rather than a mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The difference between a named tuple and a mapping as far as boolean operators
can be summarized.   Given a "named tuple" in pseudo code as:

.. sourcecode:: text

    row = (id: 5,  name: 'some name')

The biggest cross-incompatible difference is the behavior of ``__contains__``::

    "id" in row  # True for a mapping, False for a named tuple
    "some name" in row  # False for a mapping, True for a named tuple

In 1.4, when a ``LegacyRow`` is returned by a Core result set, the above
``"id" in row`` comparison will continue to succeed, however a deprecation
warning will be emitted.   To use the "in" operator as a mapping, use the
:attr:`.Row._mapping` attribute::

    "id" in row._mapping

SQLAlchemy 2.0's result object will feature a ``.mappings()`` modifier so that
these mappings can be received directly::

    # using sqlalchemy.future package
    for row in result.mappings():
        row["id"]
```
