#!/usr/bin/env python3

'''This contains the Flask REST API used by the web frontened.
This can be run from command line by:
export FLASK_APP=server.py
flask run --host=0.0.0.0
'''

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import uuid
from bson.json_util import dumps

import stats_task
from mapathons_storage import MapathonsStorage

app = Flask(__name__)
CORS(app)

app.config['stat_tasks'] = {}

@app.route('/')
def alive():
    return 'I am alive! :)'

@app.route('/stats/create', methods=['POST'])
def create_mapathon_stats():
    # Called from the web client when the user has filled and selected the form inputs and
    # submits the form. Starts a background task for creating the mapathon statistics and page.
    # Returns uuid that identifies the mapathon creation task.
    project_number_tokens = request.form['projectNumbers'].split(',')
    project_numbers_as_strings = list(map(str.strip, project_number_tokens))
    project_numbers = list(map(int, project_numbers_as_strings))
    mapathon_date = request.form['mapathonDate']
    mapathon_time_utc = request.form['mapathonTime']
    types_of_mapping = request.form.getlist('typesOfMapping')
    mapathon_title = request.form['mapathonTitle']
    print(types_of_mapping)

    client_data = {
        'project_numbers': project_numbers,
        'mapathon_date': mapathon_date,
        'mapathon_time_utc': mapathon_time_utc,
        'types_of_mapping': types_of_mapping,
        'mapathon_title': mapathon_title
    }

    # Uniquely dentifies the statistics creation task
    stat_task_uuid = uuid.uuid1()

    new_stat_task = stats_task.MapathonStatistics(stat_task_uuid, client_data)
    app.config['stat_tasks'][str(stat_task_uuid)] = new_stat_task
    new_stat_task.start_task()

    result = {
        'stat_task_uuid': stat_task_uuid
    }
    
    return jsonify(result)

@app.route('/stats/state', methods=['GET'])
def get_stats_state():
    # Called from the web client to request status update for a mapathon creation task.
    # The task is identified with uuid that is provided as a parameter.
    # Returns the status of the statistics creation task.
    stat_task_uuid = request.args.get('stat_task_uuid', type=str)

    stat_task = current_app.config['stat_tasks'].get(stat_task_uuid)
    #print(current_app.config['stat_tasks'])

    result = {
        'state': None
    }

    if stat_task is not None:
        result['state'] = stat_task.get_state()

    return jsonify(result)

@app.route('/mapathon/list', methods=['GET'])
def get_mapathon_list():
    # Returns list of the created mapathon statistics and pages
    mapathons_storage = MapathonsStorage()
    mapathons = mapathons_storage.get_all_mapathons()
    return dumps(mapathons)


@app.route('/mapathon/data', methods=['GET'])
def get_mapathon_data():
    mapathon_id = request.args.get('id')
    type_of_mapping = request.args.get('type')

    mapathons_storage = MapathonsStorage()
    data = mapathons_storage.get_mapathon_changes(mapathon_id, type_of_mapping)
    return dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
