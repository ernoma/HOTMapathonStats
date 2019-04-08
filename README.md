
# Mapathon statistics and visualization tool

## Introduction

The tool includes web UI that allows anyone to create mapathon statistics,
that can be seen via a web page created for the mapathon.

There is a backend implemented with Python that creates the statistics.

## Requirements for the backend

* Install PostgreSQL and PostGIS
  * `sudo apt-get install postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-scripts`
* Install osmosis `sudo apt install osmosis`
* Install Python 3, see: [How To Install Python 3 and Set Up a Local Programming Environment on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04)
  * You might like to add `alias python=/usr/bin/python3` to the `~/.bashrc/` or use conda or ... Instructions configuring Apache mod_wsgi below are for the virtualenv.
* Install libraries required by psycopg2
  * `sudo apt-get install python-psycopg2 libpq-dev`
* Install Python packages
  * Just run `pip install -r requirements.txt` or
  * individually
    * `pip3 install Flask`
    * `pip3 install -U flask-cors`
    * `pip3 install geopandas`
    * `pip3 install geojson`
    * `pip3 install python-dateutil`
    * `pip3 install lxml`
    * `pip3 install shapely`
    * `pip3 install requests`
    * `pip3 install pymongo`
    * `pip3 install psycopg2`
* Create MongoDB account and database for the project at https://www.mongodb.com/

## Configurations

### PostgreSQL

It is necessary to have an user with the superuser priviliges because the backend  will make SQL queries to install PostGIS and hstore extensions and only superuser priviliges allow it. So, via psql run the following queries:
<pre>
CREATE USER hotosmfi WITH PASSWORD 'your extremely hard to Know or quesS pass';
CREATE DATABASE hotosmfi OWNER hotosmfi;
ALTER USER hotosmfi SUPERUSER;
</pre>

### Apache

You can use Apache for both the frontend and the backend:

1. Follow general instructions to install Apache.
2. Follow general instructions to use Flask via mod_wsgi: http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/
3. Add the following lines to an Apache sites conf file (such as 000-default.conf) inside the <VirtualHost> tag:

<pre>
WSGIDaemonProcess tool_backend_wsgi user=www-data group=www-data threads=5 home=/home/ubuntu/HOTMapathonStats/backend
WSGIScriptAlias /tool_back /var/www/html/stats/tool_backend_wsgi/tool.wsgi

<Directory /var/www/html/stats/tool_backend_wsgi>
    WSGIProcessGroup tool_backend_wsgi
    WSGIApplicationGroup %{GLOBAL}
    Require all granted
</Directory>
</pre>

4. Create tool.wsgi file under /var/www/html/stats/tool_backend_wsgi/ directory and add the following contents to it (assuming you have created the Python 3 virtualenv in user ubuntu's home directory in the virtualenvs/HOTMapathonStats path):

<pre>
activate_this = '/home/ubuntu/virtualenvs/HOTMapathonStats/bin/activate_this.py'
with open(activate_this) as file_:
     exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/home/ubuntu/HOTMapathonStats/backend')

import os
os.environ['MONGODB_ATLAS_PW'] = 'you mongodb pass'
os.environ['HOTOSM_DB_USER'] = 'hotosmfi'
os.environ['HOTOSM_DB_PASS'] = 'your extremely hard to Know or quesS pass'
os.environ['HOTOSM_START_DB'] = 'hotosmfi'

from server_hotosm import app as application
</pre>

### Backend and frontend code

1. Place the HOTMapathonStats code under user ubuntu's home directory.
2. cd to backend and run
   * `sudo chown -R www-data osc_data`
   * `sudo chown -R www-data mapathons_data`
   * `mv server.py server_hotosm.py`
3. In the backend/mapathons_storage.py modify MONGODB_URL to match your Mongo DB
4. Edit the ui/index.js and change the first line with serverURL to `serverURL = "https://" + window.location.hostname + "/tool_back";`
5. Edit the ui/stats.js and change the first line with serverURL to `const serverURL = "https://" + window.location.hostname + "/tool_back";`
6. Create symbolic link from /var/www/html to the /home/ubuntu/HOTMpathonStats, i.e. run `ln -s /home/ubuntu/HOTMpathonStats /var/www/html`

## Running the tool

After above installs and configurations restart Apache: `sudo systemctl restart apache2.service`. Now when you go to the http://localhost/your_sybmbolic_link_dir address with a web browser the tool should show up. If it does not show up or if there are errors in creating statistics then it is worth to check the Apache logs under /var/log/www.

## Using the tool

Via the web UI create stats for a mapathon. The progress of the statistics creation is shown for the user and after the stats has been created the mapathon is shown in the list on the right hand side of the UI.

If you want to share the statistics page and want to show the mapathon time in your local time zone on the statistics page you can modify the mapathon statistics URL a bit, for example, instead of https://hotosm.fi/tool/stats?title=HOT%20Mapathon%2C%20Turku%20October%202018&date=2018-10-29&time=8&projects=3160&types=building,highway&id=5bfb015075db621bf0194c80 share the URL https://hotosm.fi/tool/stats?title=HOT%20Mapathon%2C%20Turku%20October%202018&date=2018-10-29&time=10&tz=Finnish%20winter%20time&projects=3160&types=building,highway&id=5bfb015075db621bf0194c80

## Note regarding the stored data

When the statistics are created the data is stored permanently to two locations:

* Mapathon edits are stored under HOTMapathonStats/backend/mapathons_data directory. The PostgreSQL database is only used during the statistics creation as well as the HOTMapathonStats/backend/osc_data directory.
* Mapathon info given by the user, ids that can be used to match the mapathon edits with the info and tags found from the osc data are stored in the Mongo DB collection

## Acknowledgements

Thank you for [Geofabrik](http://www.geofabrik.de/)
kindly allowing to use their OSM data for creating the statistics!
