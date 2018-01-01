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
    project_date = request.form['mapathonDate']
    project_time_utc = request.form['mapathonTime']
    types_of_mapping = request.form.getlist('typesOfMapping')
    print(types_of_mapping)

    # Uniquely dentifies the statistics creation task
    stat_task_uuid = uuid.uuid1()

    new_stats_task = stats_task.MapathonStatistics()
    new_stats_task.start_task(stat_task_uuid)

    result = {
        'status': 'OK',
        'stat_task_uuid': stat_task_uuid,
        'data': {
            'project_number': project_number,
            'project_date': project_date,
            'project_time_utc': project_time_utc,
            'types_of_mapping': types_of_mapping
        }
    }
    
    return jsonify(result);

