# Build Database for OpenStack Components

Skip the migrations, ask sqlalchemy to directly create the database. This is
a tool to validate the models.

Please note that it is assuming that inside the models module you have a
symbol called BASE, which is the declarative base.


## Example

To build the database for cinder, use this:

    dbbuild postgresql:///cinder cinder.db.sqlalchemy.models
