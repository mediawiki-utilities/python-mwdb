# MediaWiki database

This library provides a set of utilities for connecting to and querying a
MediaWiki database.  

* **Installation:** ``pip install mwdb``
* **Documentation:** https://pythonhosted.org/mwdb
* **Repositiory:** https://github.com/mediawiki-utilities/python-mwdb
* **License:** MIT

The `Schema()` object is a thin wrapper around a
sqlalchemy `Engine` and `Meta` adapts to the local database setup.  When using
`Schema()` member table ORM, the internal mapping will translate between
public replicas views (e.g. ``revision_userindex``, ``logging_userindex`` and
``logging_logindex``) transparently.  This allows you to write one query that
will run as expected on either schema.

At the moment, the `execute()` method does not make any such conversion, but a
helper attribute `public_replica` that is `True` when querying a views via
public replica and `False` when querying the production database.

## Example

    >>> import mwdb
    >>> enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
    ...                      "?read_default_file=~/replica.my.cnf")
    >>> enwiki.public_replica
    True
    >>>
    >>> with enwiki.transaction() as session:
    ...     print(session.query(enwiki.revision_userindex)
    ...           .filter_by(rev_user_text="EpochFail")
    ...           .count())
    ...
    4302
    >>> result = enwiki.execute("SELECT COUNT(*) FROM revision_userindex " +
    ...                         "WHERE rev_user=:user_id",
    ...                         {'user_id': 6396742})

    >>>
    >>> print(result.fetchone())
    (4302,)

## Authors
* Aaron Halfaker -- https://github.com/halfak
