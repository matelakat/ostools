Some OpenStack component was slow for some reason. To find out where is our CPU
time is burnt, we need to do some profiling. Here are the scripts that were
used:

## Extract SQL queries

First, I had to patch oslo using `patch_oslo.sh`.

