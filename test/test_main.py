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
import json
import datetime
import logging
import shoreline.main as main
from satsearch import Scenes
from nose.tools import set_trace

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Test(unittest.TestCase):
    """ Test masking functions """

    path = os.path.dirname(__file__)
    date_from = '2017-01-01'
    date_to = '2017-01-10'

    def get_aoi_json(self):
        """ Get test AOI from GeoJSON file """
        with open(os.path.join(self.path, 'test/aoi1.geojson')) as f:
            aoi = json.load(f)
        return aoi

    def parse_args(self, args):
        return main.parse_args(args.split(' '))

    def test_parse_args(self):
        """ Parse arguments """
        args = self.parse_args('search --aoi test/aoi1.geojson')
        self.assertEqual(args['verbose'], 2)
        self.assertEqual(args['date_to'], str(datetime.date.today()))
        args = self.parse_args('search --aoi test/aoi1.geojson --date_from %s --date_to %s' % (self.date_from, self.date_to))
        self.assertEqual(args['date_from'], self.date_from)

    def test_parse_args_with_params(self):
        """ Parse arguments with provided algorithm key=value pairs """
        args = self.parse_args('search --aoi test/aoi1.geojson --param TESTKEY=TESTVALUE')
        self.assertEqual(args['TESTKEY'], 'TESTVALUE')

    def test_process(self):
        """ Process collection of scenes into coastline geojson """
        scenes = Scenes.load(os.path.join(self.path, 'scenes1.json'))
        result = main.process(scenes, path=self.path)
