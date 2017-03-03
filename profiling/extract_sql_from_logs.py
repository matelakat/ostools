import re
import sys
import datetime
import argparse


DATE_PATTERN = '^\d{4}-\d{2}-\d{2}.*$'
SQL_STARTERS = '(?P<statement_start>SELECT|INSERT|UPDATE|DELETE )'
SQL_STARTERS_PATTERN = re.compile(SQL_STARTERS)
SQL_PATTERN = re.compile(
    r'sqlalchemy\.engine\.base\.Engine.*[]] {0}'.format(SQL_STARTERS)
)


def parse_params(params_line):
    dict_starts_at = params_line.find('{')
    assert dict_starts_at >= 0
    dict_text = params_line[dict_starts_at:]
    return eval(dict_text)


def to_psql(value):
    if type(value) == int:
        return str(value)
    elif type(value) == str:
        return "'" + value + "'"
    elif type(value) == bool:
        return 'TRUE' if value else 'FALSE'
    elif type(value) == datetime.datetime:
        return "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"
    elif type(value) == type(None):
        return 'NULL'

    raise NotImplementedError(
        'Data type {0} not implemented'.format(type(value))
    )


def make_params(params_line):
    params = parse_params(params_line)

    result = dict()

    for k, value in params.items():
        result[k] = to_psql(value)

    return result


def get_query(query_lines):
    first_line = query_lines[0]
    query_starts_at = (
        SQL_STARTERS_PATTERN.search(first_line).start('statement_start')
    )
    query_first_line = first_line[query_starts_at:]
    query = ' '.join(
        [query_first_line] + query_lines[1:]
    ) + ';'
    return query


class LineParser:
    def __init__(self):
        self.state = 'start'
        self.query_lines = []
        self.query = None
        self.query_parameters = None

    def parse_line(self, line):
        """
        Parse a log line, return True if a query has completed with this line
        """
        if self.state == 'start':
            if not re.match(DATE_PATTERN, line):
                return
            if SQL_PATTERN.search(line):
                self.state = 'in_query'
                self.query_lines = [line]
        elif self.state == 'in_query':
            if re.match(DATE_PATTERN, line):
                self.query_parameters = line
                self.query = get_query(self.query_lines)
                self.state = 'start'
                return True
            else:
                self.query_lines.append(line)


def main():
    parser = argparse.ArgumentParser(
        description='extract SQL queries from a log file'
    )
    parser.add_argument('--include-data', action='store_true', default=False)
    parameters = parser.parse_args()

    line_parser = LineParser()
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if line_parser.parse_line(line):
            params = make_params(line_parser.query_parameters)
            if parameters.include_data:
                print(line_parser.query % params)
            else:
                print(line_parser.query)


if __name__ == "__main__":
    main()
