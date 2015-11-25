"""SQL Query building class.

This modules defines a class which allow the building
of SQL queries in a functional style.
"""
from itertools import groupby


class Query(object):
    def __init__(self, table=None, **_kwargs):
        """A class for generating SQL queries.

        This class lazily builds SQL queries. Each method called
        on the class returns another `Query` object which will only
        get evaluated once the `build` method is called.

        Example:
            >>> print(Query('Person')
            >>>    .select('id', 'age')
            >>>    .filter(name='Bill')
            >>>    .order_by('name')
            >>>    .build()
            >>> )
            SELECT id, age FROM Person where name='Bill' ORDER BY name;

        Args:
            table (str): The name of the table to which the query will point
        """
        if table:
            self.func = Query._table

        self._backref = _kwargs.get('_backref', None)
        self._func = _kwargs.get('_func', None)
        self._args = _kwargs.get('_args', None)
        self._kwargs = _kwargs.get('_kwargs', None)

    def select(self, *args):
        """Set the columns that the query selects.

        Makes the query generated be a SELECT type command like:
            SELECT * FROM Table;

        *args (str): A variable sized list of column names to select
        """
        return Query(backref=self, func=Query._select, args=args)

    def filter(self, **kwargs):
        """Filter the results of the query.

        Limits the results by turning kwargs into `WHERE` conditions. This
        turns `.filter(name='value')` into `WHERE column_name='value'`.

        Args:
            kwargs: Arbitrary keyword args which maps {column_name: 'value'}
        """
        return Query(backref=self, func=Query._filter, kwargs=kwargs)

    def order_by(self, *args):
        """Order the results.

        Adds an `ORDER BY` clause to the query that orders the results.

        Args:
            args: A variable list of arguments to order the results by.
        """
        return Query(backref=self, func=Query._order_by, args=args)

    def build(self):
        """Evaluate the query.

        Returns:
            str: the evaluated query string.
        """
        backrefs = sorted(Query._backrefs(self), key=lambda b: id(b.func))
        groups = groupby(backrefs, lambda k: k.func)

        kwargs = {}
        for key, section in groups:
            kwargs[key.__name__[1:]] = getattr(Query, key.__name__)(section)

        result = '{select} {table}'
        if kwargs.get('filter'):
            result += ' {filter}'
        if kwargs.get('order_by'):
            result += ' {order_by}'
        result += ';'

        return result.format(**kwargs)

    @staticmethod
    def _backrefs(back):
        """Traverse through the backref links recursively.

        Recurses backwards on the `back` instance, yielding
        the `back` instance until `back._backref` is None.

        Returns:
            A generator object to iterate over the references to the
            composed previous instances of the `Query`.
        """
        while True:
            if back is None:
                break
            yield back
            back = back.backref

    @staticmethod
    def _args_get(refs):
        """Aggregate the iterable `refs.args` into a single iterable.

        Args:
            refs (Iterable): A list of lists of args which get aggregated
                             into a single list.

        Returns:
            A generator of all args from each `refs`s args.
        """
        for ref in refs:
            for arg in ref.args:
                yield arg

    @staticmethod
    def _kwargs_get(refs):
        """Aggregate the iterable `refs.kwargs` into a single .

        Args:
            refs (Iterable): A list of dicts of kwargs which get aggregated
                             into a key-value pair iterable.

        Returns:
            A generator key-value pairs from each `refs`s kwargs.
        """
        for ref in refs:
            for key, value in ref.kwargs.items():
                yield key, value

    @staticmethod
    def _table(refs):
        table = next(refs)
        result = '{}'.format(table.table)
        return result

    @staticmethod
    def _select(refs):
        selects = StaticQuery._args_get(refs)
        result = 'SELECT {} FROM'.format(', '.join(selects))
        return result

    @staticmethod
    def _filter(refs):
        filters = StaticQuery._kwargs_get(refs)
        result = 'WHERE {}'.format(
            ' AND '.join(
                '{}=\'{}\''.format(key, value) for key, value in filters.items()
            )
        )
        return result

    @staticmethod
    def _order_by(refs):
        selects = StaticQuery._args_get(refs)
        result = 'ORDER BY {}'.format(', '.join(selects))
        return result
