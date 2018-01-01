'''This contains the Flask REST API used by the web frontened.
This can be run from command line by:
export FLASK_APP=server.py
flask run --host=0.0.0.0
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

import stats_task

app = Flask(__name__)
CORS(app)

@app.route('/')
def alive():
    return 'I am alive! :)'

@app.route('/create/stats', methods=['POST'])
def create_mapathon_stats():
    project_number = request.form['projectNumber']
    mapathon_date = request.form['mapathonDate']
    mapathon_time_utc = request.form['mapathonTime']
    types_of_mapping = request.form.getlist('typesOfMapping')
    print(types_of_mapping)

    client_data = {
        'project_number': project_number,
        'mapathon_date': mapathon_date,
        'mapathon_time_utc': mapathon_time_utc,
        'types_of_mapping': types_of_mapping
    }

    # Uniquely dentifies the statistics creation task
    stat_task_uuid = uuid.uuid1()

    new_stats_task = stats_task.MapathonStatistics(stat_task_uuid, client_data)
    new_stats_task.start_task()

    result = {
        'status': 'OK',
        'stat_task_uuid': stat_task_uuid,
        'client_data': client_data
    }
    
    return jsonify(result);

