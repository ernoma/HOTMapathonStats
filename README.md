
Mapathon statistics and visualization tool.

## Introduction

The tool includes web UI that allows anyone to create mapathon statistics,
that can be seen via a web page created for the mapathon.

There is a backend implemented with Python that creates the statistics.

## Requirements for the backend

* Install Python 3, see: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04
  * You might like to add `alias python=/usr/bin/python3` to to `~/.bashrc/` or use conda or ...
* Install Python packages
  * `pip3 install Flask`
  * `pip3 install -U flask-cors`
  * `pip3 install geopandas`
  * `pip3 install geojson`
  * `pip3 install python-dateutil`
  * `pip3 install lxml`
  * `pip3 install shapely`
  * `pip3 install requests`
  * `pip3 install pymongo`
  * `pip3 install dnspython`
  * `pip3 install psycopg2`


## Using the tool

TODO

## Acknowledgements

Thank you for <a href="http://www.geofabrik.de/">Geofabrik</a>
kindly allowing to use their OSM data for creating the statistics!
