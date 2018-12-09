
import psycopg2
import os
from subprocess import call

class OsmosisPostgis:

    OSMOSIS_PG_FILES_PATH = os.path.join(os.getcwd(), 'osmosis_scripts')
    INPUT_BASE_PATH = os.path.join(os.getcwd(), 'osc_data')

    def __init__(self):
        self.connect_to_pg()

    def connect_to_pg(self):
        self.connection = psycopg2.connect(database=os.environ['HOTOSM_START_DB'], user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        self.connection.autocommit = True

    def prepare_db(self, db_name):
        cursor = self.connection.cursor()
        
        sql_query = 'CREATE DATABASE {}'.format(db_name)
        cursor.execute(sql_query, (db_name,))
        
        connection = psycopg2.connect(database=db_name, user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        connection.autocommit = True
        
        cursor = connection.cursor()

        cursor.execute('CREATE EXTENSION POSTGIS')
        cursor.execute('CREATE EXTENSION HSTORE')

        with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6.sql"), "r") as f:
            cursor.execute(f.read())
        with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_action.sql"), "r") as f:
            cursor.execute(f.read())
        with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_bbox.sql"), "r") as f:
            cursor.execute(f.read())
        with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_linestring.sql"), "r") as f:
            cursor.execute(f.read())
        
        cursor.close()
        connection.close()

    def write_osc_to_pg_using_osmosis(self, db_name, osc_file_name):
        file_param = 'file={}'.format(os.path.join(OsmosisPostgis.INPUT_BASE_PATH, osc_file_name))
        database_param = 'database={}'.format(db_name)
        user_param = 'user={}'.format(os.environ['HOTOSM_DB_USER'])
        password_param = 'password={}'.format(os.environ['HOTOSM_DB_PASS'])

        ret = call(['osmosis', '--read-xml-change', file_param, '--wpc', database_param, user_param, password_param])
        # ret 0 - ok
        # ret > 0 - fail with code
        # ret < 0 - killed by signal
        return ret

    