# Discover indexes in a database

This simple script will output the name of the table, and then the columns
indexed, for each index. This was used to find out the differences betweeen
a mysql and a postgresql installation.

## Example


    idxdiscover postgresql:///cinder > master.postgres.indexes
    idxdiscover mysql+pymysql://cinder:cinderpass@localhost/cinder > master.mysql.indexes
