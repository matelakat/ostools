import csv
import os
import datetime
import sys
import re
import collections


FNAME_RE = re.compile(r'^cinder_db_stats_(?P<date>\d{8})\.txt$')


def get_fnames(path):
    fnames = []
    for fname in os.listdir(path):
        match = FNAME_RE.match(fname)
        if match:
            date = datetime.datetime.strptime(match.group('date'), '%d%m%Y')
            fnames.append((date, os.path.join(path, fname)))

    return sorted(fnames)


class StatRow:
    def __init__(self, row):
        self.table_name = row[0]
        self.seq = int(row[1])
        self.idx = int(row[2])
        self.rows = int(row[3])


class TableStats:
    def __init__(self, rows):
        self.rows = [StatRow(row.split()) for row in rows]

    @classmethod
    def load(cls, fname):
        with open(fname, 'r') as f:
            return TableStats([row.strip() for row in f])

    @property
    def table_names(self):
        return [row.table_name for row in self.rows]

    def get(self, name):
        for row in self.rows:
            if row.table_name == name:
                return row


def make_diff(table_a, table_b):
    for table_name in table_b.table_names:
        if table_name in table_a.table_names:
            b_row = table_b.get(table_name)
            a_row = table_a.get(table_name)
            new_seq_scans = b_row.seq - a_row.seq
            yield dict(
                table_name=table_name,
                idx=b_row.idx - a_row.idx,
                seq=new_seq_scans,
                rows=b_row.rows - a_row.rows,
                score=new_seq_scans * b_row.rows,
            )
        else:
            raise NotImplementedError()


def as_csv(data, all_dates, all_table_names):
    sorted_dates = sorted(all_dates)
    writer = csv.writer(sys.stdout)
    writer.writerow(
        ['Table Name'] + [date.strftime('%Y-%m-%d') for date in sorted_dates])
    for table_name in sorted(all_table_names):
        row = [table_name]
        for date in sorted(all_dates):
            row.append(data[table_name][date])
        writer.writerow(row)


def main():
    data = collections.defaultdict(dict)
    all_table_names = set()
    all_dates = set()
    path_to_data = sys.argv[1]
    prev_statistics = None
    for date, fname in get_fnames(path_to_data):
        actual_statistics = TableStats.load(fname)

        if prev_statistics:
            all_dates.add(date)
            diff = list(make_diff(prev_statistics, actual_statistics))
            for diff_entry in diff:
                table_name = diff_entry['table_name']
                data[table_name][date] = diff_entry['score']
                all_table_names.add(table_name)

        prev_statistics = actual_statistics

    as_csv(data, all_dates, all_table_names)


if __name__ == "__main__":
    main()
