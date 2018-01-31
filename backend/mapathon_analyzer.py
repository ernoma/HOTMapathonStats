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

class MapathonChangeCreator(object):
    """
    Functionality for finding changes made for the HOT-OSM project during the mapathon.
    It utilizes the GeoJSON that specifies the project area and the osc file(s) that contain
    the changes for the specific location and day.
    """

    def is_inside_any_of_polygons(self, point, polys):
        for poly in polys:
            shapelyPoint = Point(point['lat'], point['lon'])
            shapelyPolygon = Polygon(poly)
            isInside = shapelyPolygon.contains(shapelyPoint)
            if isInside:
                return True
        return False

    def is_inside_polygon(self, point, polyPoints):
        # adapted from http://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python
        shapelyPoint = Point(point['lat'], point['lon'])
        shapelyPolygon = Polygon(polyPoints)
        isInside = shapelyPolygon.contains(shapelyPoint)
        #print(isInside)
        return isInside

    def create_polys(self, project_json_file):
        polys = []

        with open(project_json_file, 'r') as data_file:
            data = json.load(data_file)
            geojsonFeatures = data['features']
            for feature in geojsonFeatures:
                poly = self.create_poly(feature)
                polys.append(poly)

        return polys

    def create_poly(self, geojsonFeature):
        polyString = ""
        lines = geojsonFeature['geometry']['coordinates'][0]
        for line in lines:
            polyString += str("%.9f" % round(line[1],9)) + " " + str("%.9f" % round(line[0], 9)) + " "

        polyString = polyString.rstrip(" ")
        data = polyString.split(' ')
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
        latSum = 0
        lonSum = 0
        for point in points:
            latSum += point['lat']
            lonSum += point['lon']
        center_point['lat'] = latSum / len(points)
        center_point['lon'] = lonSum / len(points)
        return center_point


    def create_mapathon_changes(self, project_polygons, osc_root_element, date, min_hour_utz):

        #ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}') and @version='1' and @uid='69016']".format(date))
        #ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}') and @version='1' and @user='erno']".format(date))
        #ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}') and @version='1']".format(date))
        #ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}') and @uid='69016']".format(date))
        #ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}') and @user='erno']".format(date))
        ways = osc_root_element.xpath("//way[starts-with(@timestamp, '{0}')]".format(date))

        #print(ways)

        buildings = []
        residential_areas = []
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

            feature = {}
            #print(way.tag)
            #print(way.attrib)
            #print(way.xpath("string(@id)"))

            timestamp = dateutil.parser.parse(way.xpath("string(@timestamp)")) #datetime.datetime object
            #print(way.xpath("string(@timestamp)"))
            #print(timestamp.hour)
            if timestamp.hour >= int(min_hour_utz):
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
                    if len(nodes) > 1: # NOTE: can also be 0
                        pass
                        #print("len(nodes) > 1, ", len(nodes))
                        #print(nodes[0].attrib)
                        #print(nodes[1].attrib)
                    elif len(nodes) == 0:
                        pass
                        #print("len(nodes) == 0")
                        #print(len(nds))
                    else:
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

                #for nd in nds:
                #    print(nd.attrib)
                feature_type = ''
                tags = way.xpath("tag")
                #print(len(tags))

                if(len(tags) > 0):
                    #print(len(tags))
                    feature_tags = {}
                    feature_type_value = ''
                    for tag in tags:
                        #print(tag.attrib)
                        key = tag.xpath("string(@k)")
                        #print(key)
                        value = tag.xpath("string(@v)")
                        feature_tags[key] = value
                        if key == "building" or (key == "landuse" and value == "residential") or key == "highway":
                            feature_type = key
                            feature_type_value = value

                        feature['tags'] = feature_tags

                        #if feature_type is not '':
                        #    print(feature_type)

                    if feature_type == "building":
                        buildings.append(feature)
                    elif feature_type == "landuse":
                        residential_areas.append(feature)
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
                        elif feature_type_value == "footway":
                            highways_footway.append(feature)
                        elif feature_type_value == "motorway":
                            highways_road.append(feature)
                        elif feature_type_value == "trunk":
                            highways_road.append(feature)
                        elif feature_type_value == "living_street":
                            highways_road.append(feature)
                        else:
                            print(feature_type_value)

        print("count_ways_with_no_nodes: ", count_ways_with_no_nodes)

        return {
            "building": buildings,
            "landuse_residential": residential_areas,
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
        project_polygons = self.create_polys(project_json_file)
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

    def create_mapathon_changes_from_URL(self, project_polygons, osc_file_download_url, date, min_hour_utz):
        # TODO use updated input parameters
        # project_polygons is a geojson featurecollection of polygons similarly to the contents of the project_json_file argument
        try:
            osc_gz_response = requests.get(osc_file_download_url)
        except Exception as e:
            print(e)
            # TODO handle all possible error conditions

        osc_data = zlib.decompress(osc_gz_response.content, 16 + zlib.MAX_WBITS)
        osc_root_element = etree.fromstring(osc_data)

        return self.create_mapathon_changes(project_polygons, osc_root_element, date, min_hour_utz)

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

            for i in range(1, len(mapathon_changes_for_multiple_areas)):
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
