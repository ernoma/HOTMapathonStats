#!/usr/bin/env python3

import json
from os import listdir
import argparse


class UserList(object):
    """
    Functionality for finding the users who particpated the mapathon
    """

    def __init__(self):
        self.users = []

    def find_users_in_json_files(self, dirs):
        for dirname in dirs:
            files = [filename for filename in listdir(dirname) if filename.endswith('.json')]
            #print(files)

            json_data_array = []

            for json_file in files:
                path = dirname + '/' + json_file
                #print(path)
                with open(path) as data_file:
                    json_data = json.load(data_file)
                    json_data_array.append(json_data)

        self.find_users(json_data_array)

        with open('usernames.json', 'w') as outfile:
            json.dump(self.users, outfile)

    def find_users(self, json_data_array):
        for json_data in json_data_array:
            for element in json_data:
                # print(element['user'])
                if element['user'] not in self.users:
                    self.users.append(element['user'])

        return self.users

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", nargs="+",
                        help="one or more directories that contain the json files that user names are extracted from")
    args = parser.parse_args()
    # print(args.dir)

    user_list = UserList()
    user_list.find_users_in_json_files(args.dir)

