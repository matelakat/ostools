import collections
import sys

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import reflection


def strrepr(data):
    return "'" + data + "'"


class Indentor(object):
    def __init__(self):
        self.depth = 0

    def __add__(self, other):
        return '    ' * self.depth + other

    def inc(self):
        self.depth += 1

    def dec(self):
        self.depth -= 1


def index_name_for(table_name, column_name):
    return '_'.join([table_name, column_name, 'idx'])


def formatted(indexes):
    table_names = sorted(indexes.keys())

    indentor = Indentor()

    yield '{\n'

    for table_name in table_names:
        indentor.inc()
        yield indentor + strrepr(table_name) + ': {\n'
        indentor.inc()
        column_names = sorted(indexes[table_name])
        for column_name in column_names:
            yield indentor + strrepr(
                index_name_for(table_name, column_name)
            ) + ': (\n'
            indentor.inc()
            yield indentor + strrepr(column_name) + ',\n'
            indentor.dec()
            yield indentor + '),\n'
        indentor.dec()
        yield indentor + '},\n'
        indentor.dec()

    yield '}\n'


def main():
    required_indexes = collections.defaultdict(list)
    migrate_engine = create_engine(sys.argv[1])
    meta = MetaData()
    meta.bind = migrate_engine
    inspector = reflection.Inspector.from_engine(migrate_engine)
    for table_name in inspector.get_table_names():
        table = Table(table_name, meta, autoload=True)
        indexes = inspector.get_indexes(table_name)
        for column_dict in inspector.get_columns(table_name):
            column_name = column_dict['name']
            column = getattr(table.c, column_name)
            if column.foreign_keys:
                assert len(column.foreign_keys) == 1
                for idx in indexes:
                    if idx['column_names'] == [column_name]:
                        break
                else:
                    required_indexes[table_name] += [column_name]

    for data in formatted(required_indexes):
        sys.stdout.write(data)


if __name__ == "__main__":
    main()
