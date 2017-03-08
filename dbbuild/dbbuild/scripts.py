import argparse
import importlib

from sqlalchemy import create_engine


def build_database(params):
    engine = create_engine(params.connection)

    models_module = importlib.import_module(params.models)
    base = getattr(models_module, 'BASE')
    base.metadata.create_all(engine)


def parse_args_or_die():
    parser = argparse.ArgumentParser(
        description='Recreate a database with sqlalchemy'
    )
    parser.add_argument('connection', help='Connection URL')
    parser.add_argument('models', help='import path to models')
    return parser.parse_args()


def main():
    params = parse_args_or_die()
    build_database(params)
