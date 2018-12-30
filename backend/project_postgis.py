import psycopg2
import os
import json

class ProjectPostgis:

    def __init__(self):
        self.connect_to_pg()

    def connect_to_pg(self):
        self.connection = psycopg2.connect(database=os.environ['HOTOSM_START_DB'], user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        self.connection.autocommit = True

    def write_project_features_to_pg(self, db_name, project_polygon_feature_collection):

        connection = psycopg2.connect(database=db_name, user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        connection.autocommit = True

        cursor = connection.cursor()

        # TODO what if the table already exists?

        create_table_query = """ CREATE TABLE project_tasks
                        (
                            id SERIAL PRIMARY KEY,
                            geom GEOMETRY NOT NULL
                        );
                        """
        cursor.execute(create_table_query)

        geoJSON_features = project_polygon_feature_collection['features']
        for feature in geoJSON_features:
            print (feature)
            insert_query = "INSERT INTO project_tasks (geom) VALUES (ST_GeomFromGeoJSON('{}'))".format(json.dumps(feature['geometry']))
            cursor.execute(insert_query)

        cursor.close()
        connection.close()