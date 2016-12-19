"""
A :class:`mwdb.Schema` represents a pool of connections to a database.  New
connections will be spawned as needed.  A :class:`mwdb.Schema`
can execite queries within the context of a :func:`mwdb.Schema.transaction` or
directly via :func:`mwdb.Schema.execute`.

.. autoclass:: mwdb.Schema
    :members:
    :member-order: bysource
"""
from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .errors import TableDoesNotExist


class Schema():

    INDEX_TABLE_MAP = {
        'archive_userindex': 'archive',
        'revision_userindex': 'revision',
        'logging_logindex': 'logging',
        'logging_userindex': 'logging',
        'recentchanges_userindex': 'recentchanges',
        'filearchive_userindex': 'filearchive',
        'ipblocks_ipindex': 'ipblocks',
        'oldimage_userindex': 'oldimage'
    }
    """
    Maps the weird view names on labs back to the table names in the
    production database.
    """

    ONLY_TABLES = (
        'abuse_filter', 'abuse_filter_action', 'abuse_filter_log',
        'archive', 'archive_userindex',
        'category', 'categorylinks',
        'change_tag',
        'ep_articles', 'ep_cas', 'ep_courses',
        'ep_events', 'ep_instructors', 'ep_oas', 'ep_orgs',
        'ep_revisions', 'ep_students', 'ep_users_per_course',
        'externallinks',
        'filearchive', 'filearchive_userindex',
        'flaggedimages', 'flaggedpage_config', 'flaggedpage_pending',
        'flaggedpages', 'flaggedrevs', 'flaggedrevs_promote',
        'flaggedrevs_statistics', 'flaggedrevs_stats', 'flaggedrevs_stats2',
        'flaggedrevs_tracking', 'flaggedtemplates', 'geo_tags',
        'global_block_whitelist',
        'image', 'imagelinks',
        'interwiki',
        'ipblocks', 'ipblocks_ipindex',
        'iwlinks',
        'l10n_cache', 'langlinks',
        'localisation', 'localisation_file_hash',
        'logging', 'logging_logindex', 'logging_userindex',
        'mark_as_helpful',
        'math',
        'module_deps',
        'msg_resource_links',
        'oldimage', 'oldimage_userindex',
        'ores_classification', 'ores_model',
        'page', 'page_assessments', 'page_assessments_projects',
        'page_props', 'page_restrictions',
        'pagelinks',
        'pagetriage_log', 'pagetriage_page', 'pagetriage_page_tags',
        'pagetriage_tags',
        'pif_edits',
        'protected_titles',
        'recentchanges', 'recentchanges_userindex',
        'redirect',
        'revision', 'revision_userindex',
        'site_identifiers', 'site_stats', 'sites',
        'tag_summary',
        'templatelinks',
        'transcode',
        'updatelog', 'updates',
        'user', 'user_former_groups', 'user_groups',    'user_properties',
        'user_properties_anon',
        'valid_tag',
        'watchlist_count',
        'wbc_entity_usage',
        'wikilove_image_log', 'wikilove_log')
    """
    A list of tables that will be loaded from the underlying schema.
    """

    def __init__(self, engine_or_url, only_tables=None, *args, **kwargs):
        """
        :Parameters:
            engine_or_url : :class:`sqlalchemy.engine.Engine` or `str`
                Either a ready-made :class:`sqlalchemy.engine.Engine` or a
                URL for an engine.
            *args
                Passed on to :func:`sqlalchemy.create_engine`.
            *kwargs
                Passed on to :func:`sqlalchemy.create_engine`.
        """

        if isinstance(engine_or_url, Engine):
            self.engine = engine_or_url
        else:
            # This option disables memory buffering of result sets.  By setting
            # it this way, we allow the user to disagree.
            execution_options = {'stream_results': True}
            execution_options.update(kwargs.get('execution_options', {}))
            kwargs['execution_options'] = execution_options

            self.engine = create_engine(engine_or_url, *args, **kwargs)

        self.meta = MetaData(bind=self.engine)
        self.meta.reflect(views=True, only=only_tables or self.ONLY_TABLES)
        self.public_replica = 'revision_userindex' in self.meta
        """
        `bool`
            `True` if the schema is part of a public replica with
            `_userindex` and `_logindex` views.
        """

        self.Session = sessionmaker(bind=self.engine)

    def __getattr__(self, table_name):

        if table_name in self.meta.tables:
            return self.meta.tables[table_name]
        else:
            if table_name in self.TABLE_MAP:
                return self.meta.tables[self.TABLE_MAP[table_name]]
            else:
                raise TableDoesNotExist(table_name)

    @contextmanager
    def transaction(self):
        """
        Provides a transactional scope around a series of operations on a
        :class:`sqlalchemy.Session` through the use of a
        `https://docs.python.org/3/reference/compound_stmts.html#the-with-statement <with statement>`_
        If any exception is raised within the context of a transation session,
        the changes will be rolled-back.  If the transactional session
        completes without error, the changes will committed.

        :Example:

            >>> import mwdb
            >>> enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
            ...                      "?read_default_file=~/replica.my.cnf")
            >>>
            >>> with enwiki.transation() as session:
            ...     print(session.query(enwiki.user)
            ...           .filter_by(user_name="EpochFail")
            ...           .first())
            ...
            (6396742, b'EpochFail', b'', None, None, None, None, None, None,
             None, None, None, b'20080208222802', None, 4270, None)
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def execute(self, clause, params=None, **kwargs):
        """
        Executes a a query and returns the result.

        :Example:

            >>> import mwdb
            >>> enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
            ...                     "?read_default_file=~/replica.my.cnf")
            >>>
            >>> result = enwiki.execute("SELECT * FROM user " +
            ...                         "WHERE user_id=:user_id",
            ...                         {'user_id': 6396742})
            >>>
            >>> print(result.fetchone())
            (6396742, b'EpochFail', b'', None, None, None, None, None, None,
             None, None, None, b'20080208222802', None, 4270, None)

        :Parameters:
            clause : `str`
                The query to execute.
            params : `dict` | `list` ( `dict` )
                A set of key/value pairs to substitute into the clause. If a
                list is provided, an executemany() will take place.
            **kwargs
                Passed on to :mod:`sqlalchemy`
        """
        with self.transaction() as session:
            return session.execute(clause, params=params, **kwargs)
