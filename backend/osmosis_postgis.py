
import psycopg2
import os
from subprocess import call

class OsmosisPostgis:
    """
    Functionality for creating a database for osc data that is then added with Osmosis to the database. 
    The osc data is from the GeoFabrik download service that contains the changes for the mapathon area (country) on the mapathon day.
    The data is used together with the project task data in the same database for finding the mapathon changes.
    """

    OSMOSIS_PG_FILES_PATH = os.path.join(os.getcwd(), 'osmosis_scripts')
    INPUT_BASE_PATH = os.path.join(os.getcwd(), 'osc_data')

    def __init__(self):
        self.connect_to_pg()

    def connect_to_pg(self):
        self.connection = psycopg2.connect(database=os.environ['HOTOSM_START_DB'], user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        self.connection.autocommit = True

    def prepare_db(self, db_name):

        ret = ''

        cursor = self.connection.cursor()
        
        # Check if the database already exists
        sql_query = "SELECT 1 AS exists FROM pg_database WHERE datname='{}'".format(db_name)
        cursor.execute(sql_query)
        row = cursor.fetchone()
        #print(row)
        if not row:
            sql_query = 'CREATE DATABASE {}'.format(db_name)
            cursor.execute(sql_query)
            
            connection = psycopg2.connect(database=db_name, user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
            connection.autocommit = True
            
            cursor_osmosis_db = connection.cursor()

            cursor_osmosis_db.execute('CREATE EXTENSION POSTGIS')
            cursor_osmosis_db.execute('CREATE EXTENSION HSTORE')

            with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6.sql"), "r") as f:
                cursor_osmosis_db.execute(f.read())
            with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_action.sql"), "r") as f:
                cursor_osmosis_db.execute(f.read())
            with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_bbox.sql"), "r") as f:
                cursor_osmosis_db.execute(f.read())
            with open(os.path.join(OsmosisPostgis.OSMOSIS_PG_FILES_PATH, "pgsnapshot_schema_0.6_linestring.sql"), "r") as f:
                cursor_osmosis_db.execute(f.read())
        
            connection.close()

            ret = 'created'

        cursor.close()
           
        return ret

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

    