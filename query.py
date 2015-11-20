from itertools import groupby


class StaticQuery(object):
    @staticmethod
    def _order(key):
        return {
            Query._select: 0,
            Query._table: 1,
            Query._filter: 2,
        }[key.func]

    @staticmethod
    def _backrefs(back):
        while True:
            if back is None:
                break
            yield back
            back = back.backref

    @staticmethod
    def _table(refs):
        table = refs.next()
        result = 'FROM {}'.format(table.table)
        return result

    @staticmethod
    def _select(refs):
        selects = []
        for ref in refs:
            selects.extend(ref.args)
        result = 'SELECT {}'.format(', '.join(selects))
        return result

    @staticmethod
    def _filter(refs):
        filters = {}
        for ref in refs:
            filters.update(ref.kwargs)

        result = 'WHERE {}'.format(
            ' AND '.join(
                '{}=\'{}\''.format(key, value) for key, value in filters.items()
            )
        )
        return result


class Query(StaticQuery):
    def __init__(self, table=None, backref=None, func=None, args=None, kwargs=None):
        self.backref = backref
        self.table = table

        self.args = args
        self.kwargs = kwargs

        self.func = func
        if not func:
            self.func = Query._table

    def select(self, *args):
        return Query(backref=self, func=Query._select, args=args)

    def filter(self, **kwargs):
        return Query(backref=self, func=Query._filter, kwargs=kwargs)

    def build(self):
        backrefs = sorted(Query._backrefs(self), key=Query._order)
        groups = groupby(backrefs, lambda k: k.func)
        result = ' '.join(
            getattr(Query, key.__name__)(section) for key, section in groups
        )
        return result + ';'

print(Query('Person')
    .select('id')
    .select('name')
    .filter(name='Bill', age=18)
    .build()
)
