# SQLAlchemy 2.1 - selected changelog entries and migration notes

Sources (verbatim excerpts, fetched 2026-09-29):
- https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_0/doc/build/changelog/changelog_21.rst
- https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_1_0/doc/build/changelog/migration_21.rst
License: SQLAlchemy documentation, MIT License (https://github.com/sqlalchemy/sqlalchemy). Verbatim excerpt.

## From the 2.1 changelog (changelog_21.rst)

```rst
.. changelog::
    :version: 2.1.0b1
    :released: September 24, 2026
    :released: January 21, 2026

    .. change::
        :tags: change, sql
        :tickets: 10236

        The ``.c`` and ``.columns`` attributes on the :class:`.Select` and
        :class:`.TextualSelect` constructs, which are not instances of
        :class:`.FromClause`, have been removed completely, in addition to the
        ``.select()`` method as well as other codepaths which would implicitly
        generate a subquery from a :class:`.Select` without the need to explicitly
        call the :meth:`.Select.subquery` method.

        In the case of ``.c`` and ``.columns``, these attributes were never useful
        in practice and have caused a great deal of confusion, hence were
        deprecated back in version 1.4, and have emitted warnings since that
        version.   Accessing the columns that are specific to a :class:`.Select`
        construct is done via the :attr:`.Select.selected_columns` attribute, which
        was added in version 1.4 to suit the use case that users often expected
        ``.c`` to accomplish.  In the larger sense, implicit production of
        subqueries works against SQLAlchemy's modern practice of making SQL
        structure as explicit as possible.

        Note that this is **not related** to the usual :attr:`.FromClause.c` and
        :attr:`.FromClause.columns` attributes, common to objects such as
        :class:`.Table` and :class:`.Subquery`,  which are unaffected by this
        change.

        .. seealso::

            :ref:`change_4617` - original notes from SQLAlchemy 1.4

    .. change::
        :tags: sql
        :tickets: 12218

        Removed the automatic coercion of executable objects, such as
        :class:`_orm.Query`, when passed into :meth:`_orm.Session.execute`.
        This usage raised a deprecation warning since the 1.4 series.

    .. change::
        :tags: misc, changed
        :tickets: 12441

        Removed multiple api that were deprecated in the 1.3 series and earlier.
        The list of removed features includes:

        * The ``force`` parameter of ``IdentifierPreparer.quote`` and
          ``IdentifierPreparer.quote_schema``;
        * The ``threaded`` parameter of the cx-Oracle dialect;
        * The ``_json_serializer`` and ``_json_deserializer`` parameters of the
          SQLite dialect;
        * The ``collection.converter`` decorator;
        * The ``Mapper.mapped_table`` property;
        * The ``Session.close_all`` method;
        * Support for multiple arguments in :func:`_orm.defer` and
          :func:`_orm.undefer`.

    .. change::
        :tags: change, engine
        :tickets: 9647

        An empty sequence passed to any ``execute()`` method now
        raised a deprecation warning, since such an executemany
        is invalid.
        Pull request courtesy of Carlos Sousa.
```

## From "What's New in SQLAlchemy 2.1?" (migration_21.rst)

```rst
``filter_by()`` now searches across all FROM clause entities
-------------------------------------------------------------

The :meth:`_sql.Select.filter_by` method, available for both Core
:class:`_sql.Select` objects and ORM-enabled select statements, has been
enhanced to search for attribute names across **all entities present in the
FROM clause** of the statement, rather than only looking at the last joined
entity or first FROM entity.

This resolves a long-standing issue where the behavior of
:meth:`_sql.Select.filter_by` was sensitive to the order of operations. For
example, calling :meth:`_sql.Select.with_only_columns` after setting up joins
would reset which entity was searched, causing :meth:`_sql.Select.filter_by`
to fail even though the joined entity was still part of the FROM clause.

Example - previously failing case now works::

    from sqlalchemy import select, MetaData, Table, Column, Integer, String, ForeignKey

    metadata = MetaData()

    users = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(50)),
    )

    addresses = Table(
        "addresses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("users.id")),
        Column("email", String(100)),
    )

    # This now works in 2.1 - previously raised an error
    stmt = (
        select(users)
        .join(addresses)
        .with_only_columns(users.c.id)  # changes selected columns
        .filter_by(email="foo@bar.com")  # searches addresses table successfully
    )

Ambiguous Attribute Names
^^^^^^^^^^^^^^^^^^^^^^^^^^

When an attribute name exists in more than one entity in the FROM clause,
:meth:`_sql.Select.filter_by` now raises :class:`_exc.AmbiguousColumnError`,
indicating that :meth:`_sql.Select.filter` should be used instead with
explicit column references::

    # Both users and addresses have 'id' column
    stmt = select(users).join(addresses)

    # Raises AmbiguousColumnError in 2.1
    stmt = stmt.filter_by(id=5)

    # Use filter() with explicit qualification instead
    stmt = stmt.filter(addresses.c.id == 5)

The same behavior applies to ORM entities::

    from sqlalchemy.orm import Session

    stmt = select(User).join(Address)

    # If both User and Address have an 'id' attribute, this raises
    # AmbiguousColumnError
    stmt = stmt.filter_by(id=5)

    # Use filter() with explicit entity qualification
    stmt = stmt.filter(Address.id == 5)

Legacy Query Use is Unchanged
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The change to :meth:`.Select.filter_by` has **not** been applied to the
:meth:`.Query.filter_by` method of :class:`.Query`; as :class:`.Query` is
a legacy API, its behavior hasn't changed.

Migration Path
^^^^^^^^^^^^^^

Code that was previously working should continue to work without modification
in the vast majority of cases. The only breaking changes would be:

1. **Ambiguous names that were previously accepted**: If your code had joins
   where :meth:`_sql.Select.filter_by` happened to use an ambiguous column
   name but it worked because it searched only one entity, this will now
   raise :class:`_exc.AmbiguousColumnError`. The fix is to use
   :meth:`_sql.Select.filter` with explicit column qualification.

2. **Different entity selection**: In rare cases where the old behavior of
   selecting the "last joined" or "first FROM" entity was being relied upon,
   :meth:`_sql.Select.filter_by` might now find the attribute in a different
   entity. Review any :meth:`_sql.Select.filter_by` calls in complex
   multi-entity queries.

In most cases, this change is expected to make
:meth:`_sql.Select.filter_by` more intuitive to use.

:ticket:`8601`
```
