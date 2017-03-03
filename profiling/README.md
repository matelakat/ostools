Some OpenStack component was slow for some reason. To find out where is our CPU
time is burnt, we need to do some profiling. Here are the scripts that were
used:

## Extract SQL queries

 - patch oslo using `patch_oslo.sh`.
 - stop the api service, and set the number of workers to 1.
 - start the api service,
 - extract SQL statements from the log using:


    ssh node1 tail -n 0 -f /var/log/cinder/api.log | python extract_sql_from_logs.py

You can also specify `--include-data`, so data will be substituted.
