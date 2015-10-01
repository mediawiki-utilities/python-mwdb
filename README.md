# MediaWiki database

This library provides a set of utilities for connecting to and querying a
MediaWiki database.

* **Installation:** ``pip install mwdb``
* **Documentation:** https://pythonhosted.org/mwdb
* **Repositiory:** https://github.com/mediawiki-utilities/python-mwdb
* **License:** MIT

## Example

    >>> import mwdb
    >>> enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
    ...                     "?read_default_file=~/replica.my.cnf")
    >>>
    >>> with enwiki.session() as session:
    ...     print(session.query(enwiki.user)
    ...           .filter_by(user_name="EpochFail")
    ...           .first())
    ...
    (6396742, b'EpochFail', b'', None, None, None, None, None, None, None,
    None, None, b'20080208222802', None, 4270, None)
    >>> result = enwiki.execute("SELECT * FROM user WHERE user_id=:user_id",
    ...                         {'user_id': 6396742})
    >>>
    >>> print(result.fetchone())
    (6396742, b'EpochFail', b'', None, None, None, None, None, None, None,
    None, None, b'20080208222802', None, 4270, None)

## Authors
* Aaron Halfaker -- https://github.com/halfak
