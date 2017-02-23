#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_db.sqlalchemy import utils
from oslo_log import log as logging
from sqlalchemy import MetaData

from cinder.i18n import _LI

LOG = logging.getLogger(__name__)


def ensure_indexed(migrate_engine, table_name, index_name, columns):
    if utils.index_exists_on_columns(migrate_engine, table_name, columns):
        LOG.info(_LI('Skipped adding %s because an equivalent index'
                     ' already exists.'), index_name)
    else:
        utils.add_index(migrate_engine, table_name, index_name, columns)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    for table_name, indexes in INDEXES_TO_CREATE.items():
        for index_name, columns in indexes.items():
            ensure_indexed(migrate_engine, table_name, index_name, columns)


INDEXES_TO_CREATE = "<Paste the output of database/discover_indexes.py here>"
