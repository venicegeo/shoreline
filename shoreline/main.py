#!/usr/bin/env python
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
import sys
import argparse
import json
import logging
# initialized beachfront logger
import beachfront
import gippy
from bfalg_ndwi.ndwi import main as ndwi_main
from shoreline.search import search
from shoreline.version import __version__
from nose.tools import set_trace
from satsearch import Scenes
import satsearch.config as config

logger = logging.getLogger(__name__)


TIDESERVICE = 'http://localhost:5000'


class KeyValuePair(argparse.Action):
    """ Custom action for getting arbitrary key values from argparse """
    def __call__(self, parser, namespace, values, option_string=None):
        for val in values:
            n, v = val.split('=')
            setattr(namespace, n, v)


def parse_args(args):
    """ Parse arguments for the NDWI algorithm """
    desc = 'Beachfront Shoreline (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser0 = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    pparser = argparse.ArgumentParser(add_help=False)
    h = '0: Quiet, 1: Debug, 2: Info, 3: Warn, 4: Error, 5: Critical'
    pparser.add_argument('--verbose', help=h, default=2, type=int)
    pparser.add_argument('--version', help='Print version and exit', action='version', version=__version__)

    subparsers = parser0.add_subparsers(dest='command')

    parser = subparsers.add_parser('search', parents=[pparser], help='Search for images', formatter_class=dhf)
    parser.add_argument('--aoi', help='GeoJSON Feature (file or string)')
    today = datetime.date.today()
    parser.add_argument('--date_from', help='Beginning date', default=str(today+datetime.timedelta(days=-365)))
    parser.add_argument('--date_to', help='End date', default=str(today))
    parser.add_argument('--cloud_from', help='Lower limit for cloud coverage', default=0)
    parser.add_argument('--cloud_to', help='Upper limit for cloud coverage', default=20)
    parser.add_argument('--mintide', help='Lowest tide to include (0 - 1.0)', type=float)
    parser.add_argument('--maxtide', help='Highest tide to include (0 - 1.0)', type=float)
    parser.add_argument('--param', nargs='*', help='Other search parameters of form KEY=VALUE', action=KeyValuePair)
    parser.add_argument('--tideservice', help='Tide service URL', default=TIDESERVICE)
    parser.add_argument('--save', help='Save scene metadata in this file', default=None)

    parser = subparsers.add_parser('process', parents=[pparser], help='Process images', formatter_class=dhf)
    parser.add_argument('scenes', help='Filename of a scenes json file')
    parser.add_argument('--datadir', help='Default data directory', default=config.DATADIR)
    parser.add_argument('--path', help='Local path to save results', default='./')

    # convert input to dictionary
    args = vars(parser0.parse_args(args))
    args = {k: v for k, v in args.items() if v is not None}

    # if local file, read JSON from that
    if 'aoi' in args:
        if os.path.exists(args['aoi']):
            with open(args['aoi']) as f:
                args['aoi'] = json.loads(f.read())
        elif isinstance(args['aoi'], str):
            args['aoi'] = json.loads(args['aoi'])

    return args


def process(scenes, path='./'):
    """ Process scenes using bfalg-ndwi """
    fouts = []
    for scene in scenes.scenes:
        satname = scene.platform.lower()
        if satname == 'landsat-8':
            bands = ['B1', 'B5']
        elif satname == 'sentinel-2a':
            bands = ['03', '08']
        else:
            logger.error('Satellite %s not supported' % satname)
        b1 = str(scene.download(bands[0])[bands[0]])
        b2 = str(scene.download(bands[1])[bands[1]])
        #geoimg = gippy.GeoImage.open(b1)
        geojson = ndwi_main([b1, b2], outdir=path, bname=str(scene.scene_id))
        fouts.append(os.path.join(path, scene.scene_id + '.geojson'))
    return fouts


def conflate(coastlines):
    """ Conflate series of coastlines together """
    # TODO - call JS
    pass


def cli():
    args = parse_args(sys.argv[1:])
    logger.setLevel(args.pop('verbose') * 10)
    TIDESERVICE = args.pop('tideservice', 'http://localhost:5000')
    config.DATADIR = args.pop('datadir', config.DATADIR)

    cmd = args.pop('command')
    if cmd == 'search':
        scenes = search(**args)
    elif cmd == 'process':
        scenes = Scenes.load(args['scenes'])
        process(scenes, path=args['path'])

    #main(args.input, bands=args.bands, l8bqa=args.l8bqa, coastmask=args.coastmask, minsize=args.minsize,
    #     close=args.close, simple=args.simple, smooth=args.smooth, outdir=args.outdir, bname=args.basename)


if __name__ == "__main__":
    cli()
