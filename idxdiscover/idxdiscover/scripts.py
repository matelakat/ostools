import argparse
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection


def discover_indexes(params):
    engine = create_engine(params.connection)
    insp = reflection.Inspector.from_engine(engine)

    for table_name in sorted(insp.get_table_names()):
        for index in sorted(insp.get_indexes(table_name), key=lambda x: x['name']):
            print ','.join([table_name] + sorted(index['column_names']))


def parse_args_or_die():
    parser = argparse.ArgumentParser(
        description='Discover indexes on a database'
    )
    parser.add_argument('connection', help='Connection URL')
    return parser.parse_args()


def main():
    params = parse_args_or_die()
    discover_indexes(params)
