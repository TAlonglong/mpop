#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016.

# Author(s):

#   Trygve Aspenes <trygve.aspenes@met.no>

# This file is part of mpop.

# mpop is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# mpop is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# mpop.  If not, see <http://www.gnu.org/licenses/>.


"""mpop mitiff writer interface.
"""

__revision__ = 0.1

import numpy as np
import logging

logger = logging.getLogger(__name__)

def save(scene, filename, compression=True, dtype=np.int16, band_axis=2):
    """Saves the scene as a MITIFF file. This is local for METNO, but can be read by DIANA

    """
    return mitiff_writer(filename, CFScene(scene, dtype, band_axis), compression=compression)


def mitiff__writer(filename, root_object, compression=True):
    """ Write data to MITIFF file. """

