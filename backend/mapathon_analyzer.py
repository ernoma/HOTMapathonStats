#!/usr/bin/env python3

import os
import json
import dateutil.parser
from datetime import *
import requests
import zlib
from lxml import etree
import argparse
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from osmosis_postgis import OsmosisPostgis
from project_postgis import ProjectPostgis

class MapathonChangeCreator(object):
    """
    Functionality for finding changes made for the HOT-OSM project during the mapathon.
    It utilizes the GeoJSON that specifies the project area and the osc file(s) that contain
    the changes for the specific location and day.
    """

    def __init__(self):
        self.analysis_percentage = 0
        self.osmosis_postgis = OsmosisPostgis()
        self.project_postgis = ProjectPostgis()

    def is_inside_any_of_polygons(self, point, polygons):
        #print(polygons)
        for polygon in polygons:
            shapely_point = Point(point['lat'], point['lon'])
            shapely_polygon = Polygon(polygon)
            # TODO probably would be better to use the intersects function.
            is_inside = shapely_polygon.contains(shapely_point)
            if is_inside:
                return True
        return False

    def is_inside_polygon(self, point, polygon_points):
        # adapted from http://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python
        shapely_point = Point(point['lat'], point['lon'])
        shapely_polygon = Polygon(polygon_points)
        is_inside = shapely_polygon.contains(shapely_point)
        #print(is_inside)
        return is_inside

    def create_polygons_from_file(self, project_json_file):
        with open(project_json_file, 'r') as data_file:
            data = json.load(data_file)
            polygons = self.create_polygons_from_feature_collection(data)

            return polygons

    def create_polygons_from_feature_collection(self, data):
        polygons = []

        geojson_features = data['features']
        for feature in geojson_features:
            #print(feature)
            print(feature['geometry']['type'])
            if feature['geometry']['type'] == 'Polygon':
                lines = feature['geometry']['coordinates'][0]
                polygon = self.create_polygon(lines)
                polygons.append(polygon)
            elif feature['geometry']['type'] == 'MultiPolygon':
                for subgeom in feature['geometry']['coordinates']:
                    lines = subgeom[0]
                    polygon = self.create_polygon(lines)
                    polygons.append(polygon)
            else:
                print('unhandled feature geometry type', feature['geometry']['type'])

        return polygons

    def create_polygon(self, lines):
        polygon_string = ""
        
        #print(lines)
        for line in lines:
            polygon_string += str("%.9f" % round(line[1],9)) + " " + str("%.9f" % round(line[0], 9)) + " "

        polygon_string = polygon_string.rstrip(" ")
        data = polygon_string.split(' ')
        #print(data)

        #print(len(data))
        coords = []
        for i in range(0, len(data), 2):
            coords.append((float(data[i]), float(data[i+1])))
            #print(coords)
        return coords

    def calculate_center(self, points):
        #print(points)
        center_point = {}
        lat_sum = 0
        lon_sum = 0
        for point in points:
            lat_sum += point['lat']
            lon_sum += point['lon']
        center_point['lat'] = lat_sum / len(points)
        center_point['lon'] = lon_sum / len(points)
        return center_point


    def create_feature(self, way):
        feature = {}
        feature['id'] = way.xpath("string(@id)")
        feature['user'] = way.xpath("string(@user)")
        feature['uid'] = way.xpath("string(@uid)")
        feature_version = int(way.xpath("string(@version)"))
        feature['version'] = feature_version
        #print(len(way))
        nds = way.xpath("nd")
        feature_nodes = []
        for nd in nds:
            feature_node = {}
            node_ref = nd.xpath("string(@ref)")
            feature_node['id'] = node_ref
            nodes = osc_root_element.xpath("//node[@id='%s']" % node_ref)
            if len(nodes) == 1: # NOTE: can also be 0
                lat = nodes[0].xpath("string(@lat)")
                lon = nodes[0].xpath("string(@lon)")
                feature_node['lat'] = float(lat)
                feature_node['lon'] = float(lon)
                feature_nodes.append(feature_node)

            if len(feature_nodes) == 0: # do not store a way that does not have any new nodes
                count_ways_with_no_nodes += 1
                continue
            else:
                center = self.calculate_center(feature_nodes)
                if not self.is_inside_any_of_polygons(center, project_polygons):
                    continue
                if feature_version == 1: # store only nodes for created features to save memory & bandwidth
                    feature["nodes"] = feature_nodes

        return feature

    def create_mapathon_changes(self, project_polygons, osc_root_element, date, min_hour_utz):

        self.analysis_percentage = 0

        ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}')]".format(date))

        buildings = []
        residential_areas = []
        landuse_farmlands = []
        landuse_orchards = []
        landuse_any_other = []
        highways_path = []
        highways_primary = []
        highways_residential = []
        highways_secondary = []
        highways_service = []
        highways_tertiary = []
        highways_track = []
        highways_unclassified = []
        highways_road = []
        highways_footway = []

        count_ways_with_no_nodes = 0

        for i, way in enumerate(ways):

            percentage = i / len(ways) * 100
            print("Done", "%.2f" % round(percentage, 2), "\b%")
            self.analysis_percentage = round(percentage, 2)

            timestamp = dateutil.parser.parse(way.xpath("string(@timestamp)")) #datetime.datetime object

            if timestamp.hour >= int(min_hour_utz):
                feature = self.create_feature(way)

                tags = way.xpath("tag")

                if(len(tags) > 0):
                    feature_tags = {}
                    feature_type = ''
                    feature_type_value = ''
                    for tag in tags:
                        key = tag.xpath("string(@k)")
                        value = tag.xpath("string(@v)")
                        feature_tags[key] = value
                        if key == "building" or key == "landuse" or key == "highway":
                            feature_type = key
                            feature_type_value = value

                        feature['tags'] = feature_tags

                    if feature_type == "building":
                        buildings.append(feature)
                    elif feature_type == "landuse":
                        if feature_type_value == "residential":
                            residential_areas.append(feature)
                        elif feature_type_value == "farmland":
                            landuse_farmlands.append(feature)
                        elif feature_type_value == "orchard":
                            landuse_orchards.append(feature)
                        else:
                            landuse_any_other.append(feature)
                    elif feature_type == "highway":
                        if feature_type_value == "path":
                            highways_path.append(feature)
                        elif feature_type_value == "primary":
                            highways_primary.append(feature)
                        elif feature_type_value == "residential":
                            highways_residential.append(feature)
                        elif feature_type_value == "secondary":
                            highways_secondary.append(feature)
                        elif feature_type_value == "service":
                            highways_service.append(feature)
                        elif feature_type_value == "tertiary":
                            highways_tertiary.append(feature)
                        elif feature_type_value == "track":
                            highways_track.append(feature)
                        elif feature_type_value == "unclassified":
                            highways_unclassified.append(feature)
                        elif feature_type_value == "road":
                            highways_road.append(feature)
                        elif feature_type_value == "motorway":
                            highways_road.append(feature)
                        elif feature_type_value == "trunk":
                            highways_road.append(feature)
                        elif feature_type_value == "living_street":
                            highways_road.append(feature)
                        elif feature_type_value == "footway":
                            highways_footway.append(feature)
                        else:
                            print(feature_type_value)

        print("count_ways_with_no_nodes: ", count_ways_with_no_nodes)

        return {
            "building": buildings,
            "landuse_residential": residential_areas,
            "landuse_farmland": landuse_farmlands,
            "landuse_orchard": landuse_orchards,
            "landuse_any_other": landuse_any_other,
            "highway_path": highways_path,
            "highway_primary": highways_primary,
            "highway_residential": highways_residential,
            "highway_secondary": highways_secondary,
            "highway_service": highways_service,
            "highway_tertiary": highways_tertiary,
            "highway_track": highways_track,
            "highway_unclassified": highways_unclassified,
            "highway_road": highways_road,
            "highway_footway": highways_footway
        }


    def create_mapathon_changes_from_file(self, project_json_file, osc_file, date, min_hour_utz, output_dir):
        project_polygons = self.create_polygons_from_file(project_json_file)
        osc_root_element = etree.parse(osc_file).getroot()
        results = self.create_mapathon_changes(project_polygons, osc_root_element, date, min_hour_utz)

        os.makedirs(output_dir, exist_ok=True)

        # print(len(ways))
        # print(len(buildings))
        with open(output_dir + '/' + 'buildings.json', 'w') as outfile:
            json.dump(results['building'], outfile)

        # print(len(residential_areas))
        # print(json.dumps(residential_areas))
        with open(output_dir + '/' + 'residential_areas.json', 'w') as outfile:
            json.dump(results['landuse_residential'], outfile)

        with open(output_dir + '/' + 'landuse_farmland.json', 'w') as outfile:
            json.dump(results['landuse_farmland'], outfile)

        with open(output_dir + '/' + 'landuse_orchard.json', 'w') as outfile:
            json.dump(results['landuse_orchard'], outfile)

        with open(output_dir + '/' + 'landuse_any_other.json', 'w') as outfile:
            json.dump(results['landuse_any_other'], outfile)

        # print(len(highways_path))
        # print(json.dumps(highways_path))
        with open(output_dir + '/' + 'highways_path.json', 'w') as outfile:
            json.dump(results['highway_path'], outfile)

        # print(len(highways_primary))
        with open(output_dir + '/' + 'highways_primary.json', 'w') as outfile:
            json.dump(results['highway_primary'], outfile)

        # print(len(highways_residential))
        with open(output_dir + '/' + 'highways_residential.json', 'w') as outfile:
            json.dump(results['highway_residential'], outfile)

        # print(len(highways_secondary))
        with open(output_dir + '/' + 'highways_secondary.json', 'w') as outfile:
            json.dump(results['highway_secondary'], outfile)

        # print(len(highways_service))
        with open(output_dir + '/' + 'highways_service.json', 'w') as outfile:
            json.dump(results['highway_service'], outfile)

        # print(len(highways_tertiary))
        with open(output_dir + '/' + 'highways_tertiary.json', 'w') as outfile:
            json.dump(results['highway_tertiary'], outfile)

        # print(len(highways_track))
        with open(output_dir + '/' + 'highways_track.json', 'w') as outfile:
            json.dump(results['highway_track'], outfile)

        # print(len(highways_unclassified))
        with open(output_dir + '/' + 'highways_unclassified.json', 'w') as outfile:
            json.dump(results['highway_unclassified'], outfile)

        # print(len(highways_road))
        with open(output_dir + '/' + 'highways_road.json', 'w') as outfile:
            json.dump(results['highway_road'], outfile)

        # print(len(highways_footway))
        with open(output_dir + '/' + 'highways_footway.json', 'w') as outfile:
            json.dump(results['highway_footway'], outfile)

    def create_mapathon_changes_from_URL(self, project_polygon_feature_collection, osc_file_download_url, date, min_hour_utz):
        # project_polygons is a geojson featurecollection of polygons similarly to the contents of the project_json_file argument
        try:
            #osc_gz_response = requests.get(osc_file_download_url)
            osc_gz_response = requests.get(osc_file_download_url, stream=True)
        except Exception as e:
            print(e)
            # TODO handle all possible error conditions
        
        file_name = self.save_osc_to_file(osc_file_download_url, osc_gz_response)
        self.insert_data_to_db(file_name, project_polygon_feature_collection)
        # TODO analyze in PostGIS db

        # osc_data = zlib.decompress(osc_gz_response.content, 16 + zlib.MAX_WBITS)
        # osc_root_element = etree.fromstring(osc_data)

        # project_polygons = self.create_polygons_from_feature_collection(project_polygon_feature_collection)
        # return self.create_mapathon_changes(project_polygons, osc_root_element, date, min_hour_utz)


    def insert_data_to_db(self, file_name, project_polygon_feature_collection):
        
        self.db_name = file_name.split('.')[0]
        self.osmosis_postgis.prepare_db(self.db_name)
        ret = self.osmosis_postgis.write_osc_to_pg_using_osmosis(self.db_name, file_name)

        if ret == 0:
            pass
        else:
            pass
             # TODO

        self.project_postgis.write_project_features_to_pg(self.db_name, project_polygon_feature_collection)

    def save_osc_to_file(self, osc_file_download_url, osc_gz_response):
        file_name = osc_file_download_url.split(':')[1][2:].replace('download.geofabrik.de/', '').replace('/', '_').replace('-', '_')
        output_path = os.path.join(os.getcwd(), 'osc_data', file_name)
        with open(output_path, 'wb') as outfile:
            for chunk in osc_gz_response.iter_content(chunk_size=1024): 
                if chunk:
                    outfile.write(chunk)

        return file_name


    def get_analysis_progress(self):
        return self.analysis_percentage


    def filter_same_changes(self, mapathon_changes_for_multiple_areas):
        # if changes were extracted from more than one area (osc file) then
        # the areas (of the osc files) can partially overlap and therefore there is need to look up and filter
        # the same changes
        # mapathon_changes_for_multiple_areas parameter is an array of dictionaries that have all or part
        # of the key-value pairs that are returned from the create_mapathon_changes functions.
        # The items in the array are assumed to have the same keys.
        # returns filtered_changes_for_multiple_areas

        if len(mapathon_changes_for_multiple_areas) >= 1:
            # iterate over the JSON elements of the item in the filtered_mapathon_changes and
            # the the JSON elements of the item in mapathon_changes_for_multiple_areas[i] corresponding the key
            # and add the missing JSON elements to the filtered_mapathon_changes item JSON

            filtered_mapathon_changes = mapathon_changes_for_multiple_areas[0]

            print(range(1, len(mapathon_changes_for_multiple_areas)))

            for i in range(1, len(mapathon_changes_for_multiple_areas)):
                print(i)
                for key, area_changes in mapathon_changes_for_multiple_areas[i].items():
                    for area_change in area_changes:
                        found_change = False
                        for filtered_change in filtered_mapathon_changes[key]:
                            if filtered_change['id'] == area_change['id']:
                                found_change = True
                                break
                        if not found_change:
                            filtered_mapathon_changes[key].append(area_change)

            return filtered_mapathon_changes
        else:
            return mapathon_changes_for_multiple_areas


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("osc_file",
                        help="name of the osc file that contains the OSM changeset that edits are looked up from. OSC files can be found from https://download.geofabrik.de")
    parser.add_argument("project_json_file",
                        help="file that contains coordinates for the area that changes are looked up from. This file can be created from the tasks.json with ogr2ogr")
    parser.add_argument("date", help="date of the changes that are looked up in format year-mm-dd, e.g. 2017-02-08")
    parser.add_argument("min_hour_utz",
                        help="changes are looked up from this hour (in UTC) to end of the day on the specified date")
    parser.add_argument("output_dir", help="name of the directory that will contain the jsons with the changes")
    # parser.add_argument("", help="")
    args = parser.parse_args()

    mapathon_change_creator = MapathonChangeCreator()

    mapathon_change_creator.create_mapathon_changes_from_file(args.project_json_file, args.osc_file, args.date, args.min_hour_utz, args.output_dir)
