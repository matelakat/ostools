Given that postgresql does not create indexes automatically on foreign keys,
we found that some queries were slow. The aproach taken here is to inspect the
model and create indexes on all foreign keys.

## Discover indexes on cinder database


    oslo-config-generator \
        --config-file=cinder/config/cinder-config-generator.conf \
        --output-file=cinder-master.conf
    sudo -u postgres psql
    create database cindersample encoding 'utf-8';
    grant all on DATABASE cindersample to matelakat;


Set your database connection string in `cinder-master.conf`:


    connection = postgresql:///cindersample


Migrate the database:


    cinder-manage --config-file=cinder-master.conf db sync


Create a change script:


    python cinder/db/sqlalchemy/migrate_repo/manage.py script "add foreign key indexes"


Find out missing indexes (the script outputs a python structure that could be
used with the provided template for cinder):


    python discover_indexes.py postgresql://cindersample > missing_indexes.py


That will print out a dictionary, which you want to paste into the template:


    python template_migration.py


To fix models.py, use the `fix_models.py` script that will help you on the
repetitive tasks.


    python fix_models.py missing_indexes.py
