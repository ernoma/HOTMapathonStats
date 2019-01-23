import psycopg2
import os
import json
from pprint import pprint

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
            insert_query = "INSERT INTO project_tasks (geom) VALUES (ST_SetSRID(ST_GeomFromGeoJSON('{}'), 4326))".format(json.dumps(feature['geometry']))
            cursor.execute(insert_query)

        create_spatial_index_query = "CREATE INDEX project_tasks_gix ON project_tasks USING GIST (geom);"
        cursor.execute(create_spatial_index_query)

        cursor.close()
        connection.close()

    def find_changes(self, db_name, date, min_hour_utz, osm_key, osm_values=None, osm_exclude_values=None, geomtype=None):
        # TODO find created features that matches the provided date, time, OSM key and possible specifiers for the OSM tag values to include and / or exlude
        connection = psycopg2.connect(database=db_name, user=os.environ['HOTOSM_DB_USER'], host='localhost', password=os.environ['HOTOSM_DB_PASS'])
        cursor = connection.cursor()

        query = ""
        if geomtype == 'polygon':
            query = "SELECT ways.id, version, ST_AsGeoJSON(ST_MakePolygon(linestring)), hstore_to_json(tags) "
            query += "FROM ways, project_tasks " \
                "WHERE ST_Intersects(linestring, project_tasks.geom) AND ST_NumPoints(linestring) >= 4 AND "
        else:
            query = "SELECT ways.id, version, ST_AsGeoJSON(linestring), hstore_to_json(tags) "
            query += "FROM ways, project_tasks " \
                "WHERE ST_Intersects(linestring, project_tasks.geom) AND "
        
        query += "tstamp >= '{} {}'::timestamp".format(date, str(min_hour_utz) + ":00:00")

        if osm_values is None and osm_exclude_values is None:
            query += " AND tags ? '{}'".format(osm_key)
        else:
            if osm_values is not None:
                query += " AND ("
                for value in osm_values:
                    query += "tags -> '{}' = '{}' OR ".format(osm_key, value)
                query = query[:-4] + ")"
            if osm_exclude_values is not None:
                query += " AND ("
                for value in osm_exclude_values:
                    query += "tags -> '{}' <> '{}' AND ".format(osm_key, value)
                query = query[:-5] + ")"
        
        #print(query)
        cursor.execute(query)

        features = []

        row = cursor.fetchone()
        while row:
            #pprint(row)
            feature = self.create_feature(row)
            #pprint(feature)
            features.append(feature)
            row = cursor.fetchone()

        return features

    def create_feature(self, row):
        feature = {}
        feature['type'] = 'Feature'
        feature_version = row[1]
        if feature_version == 1: # store only nodes for created features to save memory & bandwidth
            feature["geometry"] = row[2]

        feature['properties'] = {}

        feature['properties']['id'] = row[0]
        feature['properties']['version'] = feature_version
        feature['properties']['tags'] = row[3]

        return feature
        