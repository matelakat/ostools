We are doing this query on a daily basis:


    COPY (
        SELECT
            relname,
            seq_scan,
            idx_scan,
            n_live_tup rows_in_table
        FROM
            pg_stat_user_tables
        ORDER BY
            n_live_tup DESC
    ) TO STDOUT;


And storing them to a directory.

We then diff those results, so the difference means the scans since the last
day. This script will output the score for each table in each day, where score
is the number of sequential scans * number of rows in the database:


    python daily_statistics.py /path/to/stats/files

