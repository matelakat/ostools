import sys
from cinder.db.sqlalchemy import models
from sqlalchemy import Index, schema
import inspect


def table_args_code(cls, idx):
    yield '    __table_args__ = ('
    idx_names = sorted(idx.keys())
    for idx_name in idx_names:
        column, = idx[idx_name]
        yield "        Index('{name}', '{column}'),".format(
            name=idx_name,
            column=column
        )
    yield "        {'mysql_engine': 'InnoDB'}"
    yield '    )'


def replace(fname, original_lines, amended_lines):
    original_content = ''.join(original_lines)
    amended_content = ''.join(amended_lines)

    with open(fname, 'rb') as orig_file:
        contents = orig_file.read()

    assert original_content in contents

    new_contents = contents.replace(original_content, amended_content)

    with open(fname, 'wb') as new_file:
        new_file.write(new_contents)


def fix_a_dict(cls, idx):
    fname = inspect.getfile(cls)
    if fname.endswith('.pyc'):
        fname = fname[:-1]
    original_lines, line_number = inspect.getsourcelines(cls)
    source = ''.join(original_lines)
    assert '__table_args__' not in source

    amended_lines = []
    for line in original_lines:
        amended_lines.append(line)
        if '__tablename__' in line:
            for new_line in table_args_code(cls, idx):
                amended_lines.append(new_line + '\n')

    replace(fname, original_lines, amended_lines)


def check_tuple(cls, table_args, idx):
    existing_indexes = [
        table_arg for table_arg in table_args if isinstance(table_arg, Index)
    ]

    existing_constraints = [
        table_arg for table_arg in table_args
        if isinstance(table_arg, schema.UniqueConstraint)
    ]

    for idx_name, idx_cols in idx.items():
        for existing_idx in existing_indexes:
            if existing_idx.name == idx_name:
                break
        else:
            for existing_constraint in existing_constraints:
                column, = idx_cols
                if column in existing_constraint.columns:
                    print idx_name, 'already covered by a constraint'
                    break
            else:
                print 'Missing from', cls.__name__, idx_name, idx_cols


def count_missing_indexes(missing_indexes):
    idx_counter = 0
    for idx in missing_indexes.values():
        idx_counter += len(idx)

    return idx_counter


def main():
    missing_indexes = sys.argv[1]
    with open(missing_indexes) as f:
        missing_indexes = eval(f.read())

    print count_missing_indexes(missing_indexes)

    clsmembers = inspect.getmembers(models, inspect.isclass)

    for name, cls in clsmembers:
        if not hasattr(cls, '__tablename__'):
            continue

        table_name = cls.__tablename__

        if table_name not in missing_indexes:
            continue

        idx = missing_indexes[table_name]
        table_args = cls.__table_args__

        assert table_args

        if isinstance(table_args, dict):
            assert table_args == {'mysql_engine': 'InnoDB'}
            fix_a_dict(cls, idx)
        elif isinstance(table_args, tuple):
            check_tuple(cls, table_args, idx)
        else:
            raise NotImplementedError


if __name__ == "__main__":
    main()
