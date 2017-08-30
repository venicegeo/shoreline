"""
shoreline
https://github.com/venicegeo/shoreline

Copyright 2016, RadiantBlue Technologies, Inc.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import os
import datetime
import tempfile
import sys
import argparse
import json
import logging
import requests
from dateutil.parser import parse
from satsearch.scene import Scenes
from satsearch.search import Search
from shoreline.version import __version__
import bfalg_ndwi
import visvalingamwyatt as vw
#from osgeo import gdal
import gippy
import gippy.algorithms as alg
import beachfront.mask as bfmask
import beachfront.process as bfproc
import beachfront.vectorize as bfvec
from nose.tools import set_trace

logger = logging.getLogger(__name__)


def query_satapi(aoi, clip=False, **kwargs):
    """ Search sat-api using sat-search """
    if clip:
        aoi = get_coastline(aoi)
    search = Search(intersects=json.dumps(aoi), **kwargs)
    return search.scenes()


def get_coastline(bbox):
    """ Get coastline GeoJSON within bounding box """
    cmask = bfmask.open_vector(os.path.join(os.path.dirname(bfalg_ndwi.__file__), 'coastmask.shp'))
    lons = [c[0] for c in bbox['features'][0]['geometry']['coordinates'][0]]
    lats = [c[1] for c in bbox['features'][0]['geometry']['coordinates'][0]]
    bbox = [min(lons), min(lats), max(lons), max(lats)]
    gj = bfmask.get_features_as_geojson(cmask[1], bbox=bbox, union=True)
    #fname = 'tmpfile.geojson'
    #with open(fname, 'w') as f:
    #    f.write(json.dumps(gj))
    #bfvec.simplify(fname, 0.025)
    #with open(fname) as f:
    #    gj = json.load(f)
    #os.remove(fname)

    #gj = vw.simplify_geometry(gj, ratio=0.08)

    return gj


def search(aoi, clip=False, mintide=0.8, maxtide=1.0, save=None, **kwargs):
    """ Search for scenes with sat-search, add tide data and filter by tide """
    scenes = query_satapi(aoi, clip=clip, **kwargs)
    new_scenes = []
    for scene in scenes:
        add_tide_data(scene)
        normtide = scene.metadata['tide']['normTide']
        if (normtide >= mintide) and (normtide <= maxtide):
            new_scenes.append(scene)
    scenes = Scenes(new_scenes)
    if save:
        scenes.save(save, geojson=True)
    logger.info('%s scenes found' % len(scenes))
    return scenes


def tide_prediction(lat, lon, dt):
    """ Get tide prediction for lat, lon and datetime """
    url = 'http://localhost:5000'
    payload = {'lat': lat, 'lon': lon, 'dtg': dt}
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        td = resp.json()
        tiderange = td['maximumTide24Hours'] - td['minimumTide24Hours']
        td['normTide'] = (td['currentTide'] - td['minimumTide24Hours'])/tiderange
        return td
    else:
        raise Exception('Tide prediction service not found at %s' % url)


def add_tide_data(scene):
    """ Add tide info to scene metadata """
    if scene.metadata['satellite_name'].lower() == 'sentinel-2a':
        dt = parse(scene.metadata['timestamp'])
    elif scene.metadata['satellite_name'].lower() == 'landsat-8':
        tm1 = datetime.datetime.strptime(scene.metadata['sceneStartTime'][:-1], '%Y:%j:%H:%M:%S.%f')
        tm2 = datetime.datetime.strptime(scene.metadata['sceneStopTime'][:-1], '%Y:%j:%H:%M:%S.%f')
        dt = tm1 + (tm2 - tm1) / 2
    bbox = scene.metadata['data_geometry']['coordinates'][0]
    lons = [c[0] for c in bbox]
    lats = [c[1] for c in bbox]
    lon = (min(lons) + max(lons))/2.0
    lat = (min(lats) + max(lats))/2.0
    dtg = dt.strftime('%Y-%m-%d-%H-%M')
    scene.metadata['tide'] = tide_prediction(lat, lon, dtg)
    return scene
