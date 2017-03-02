#!/bin/bash
set -eux
cat oslo_db_enable_sql_statement_logging.patch |
    patch -d /usr/lib/python2.7/site-packages/oslo_db/sqlalchemy && patch -p0
