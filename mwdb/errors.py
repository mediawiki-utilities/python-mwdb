"""
.. autoclass:: mwdb.errors.TableDoesNotExist
"""


class TableDoesNotExist(RuntimeError):
    """
    A table cannot be found in the schema.
    """
    pass
