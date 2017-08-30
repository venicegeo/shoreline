"""
bfalg-ndwi
https://github.com/venicegeo/bfalg-ndwi

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

import unittest
import os
import sys
import datetime
import json
import logging
import shoreline.search as search
from nose.tools import assert_almost_equals, set_trace

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Test(unittest.TestCase):
    """ Test masking functions """

    path = os.path.dirname(__file__)
    date_from = '2017-01-01'
    date_to = '2017-01-10'

    def get_aoi_json(self):
        """ Get test AOI from GeoJSON file """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.load(f)
        return aoi

    def get_query(self):
        """ Get a query for testing """
        scenes = search.query_satapi(aoi=self.get_aoi_json(),
                                     date_from=self.date_from, date_to=self.date_to,
                                     cloud_from=0, cloud_to=20)
        return scenes

    def test_query(self):
        """ Make a search query to find scenes """
        scenes = self.get_query()
        self.assertEqual(len(scenes), 22)

    def test_get_coastline(self):
        """ Get GeoJSON of coastline within bounding box """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            bbox = json.load(f)
        gj = search.get_coastline(bbox)
        with open(os.path.join(self.path, 'aoi-test.geojson'), 'w') as f:
            f.write(json.dumps(gj))

    def test_search(self):
        """ Search with tide constraints """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.load(f)
        scenes = search.search(aoi=self.get_aoi_json(), mintide=0.7, maxtide=1.0,
                               date_from=self.date_from, date_to=self.date_to,
                               cloud_from=0, cloud_to=20)
        self.assertEqual(len(scenes), 13)

    def test_tideprediction(self):
        """ Try tide prediction service """
        result = search.tide_prediction(45.0, -60.0, '2017-01-01-12-00')
        assert_almost_equals(result['normTide'], 0.8, places=2)

    def test_query_coastline(self):
        """ Test clipping to just coastline in query """
        aoi = search.get_coastline(self.get_aoi_json())
        fname = os.path.join(self.path, 'test_query_coastline.geojson')
        with open(fname, 'w') as f:
            f.write(json.dumps(aoi))
        scenes = search.query_satapi(aoi=aoi,
                                     date_from=self.date_from, date_to=self.date_to,
                                     cloud_from=0, cloud_to=20)
        #self.assertTrue(os.path.exists(fname))

    def _test_tide_filter(self):
        """ Filter scenes by tide """
        scenes = self.get_query()
        new_scenes = search.tide_filter(scenes, 0.9, 1.0)
        from nose.tools import set_trace; set_trace()
