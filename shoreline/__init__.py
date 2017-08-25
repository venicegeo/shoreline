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

from .version import __version__

import logging

# quiet these loggers
logging.getLogger('urllib3').setLevel(logging.CRITICAL)