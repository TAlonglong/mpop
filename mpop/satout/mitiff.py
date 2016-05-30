#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016.
#from tifffile.tifffile import TIFF_TAGS
from TiffImagePlugin import IMAGEDESCRIPTION

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

import os
import numpy as np
import logging
from copy import deepcopy
import xml_read
#import xml.etree.ElementTree as etree

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#
# Read MiTIFF products config file.
#
#-------------------------------------------------------------------------------
def get_product_config(product_name, force_read=False):
    """Read MiTIFF configuration entry for a given product name.

    :Parameters:
        product_name : str
            Name of MiTIFF product.

    :Arguments:
        force_read : Boolean
            Force re-reading config file.

    **Notes**:
        * It will look for a *mitiff_products.cfg* in MPOP's
          configuration directory defined by *PPP_CONFIG_DIR*.
        * As an example, see *mitiff_products.cfg.template* in
          MPOP's *etc* directory.
    """
    return ProductConfigs()(product_name, force_read)


class _Singleton(type):
    def __init__(cls, name_, bases_, dict_):
        super(_Singleton, cls).__init__(name_, bases_, dict_)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls.instance

class ProductConfigs(object):
    __metaclass__ = _Singleton

    def __init__(self):
        self.read_config()

    def __call__(self, product_name, force_read=False):
        if force_read:
            self.read_config()
        return self._products[product_name]

    @property
    def product_names(self):
        return sorted(self._products.keys())

    def read_config(self):
        from ConfigParser import ConfigParser

        def _eval(val):
            try:
                return eval(val)
            except:
                return str(val)

        filename = self._find_a_config_file()
        logger.info("Reading MiTIFF config file: '%s'" % filename)

        cfg = ConfigParser()
        cfg.read(filename)
        products = {}
        for sec in cfg.sections():
            prd = {}
            for key, val in cfg.items(sec):
                prd[key] = _eval(val)
                logger.debug("%s %s" % (key,prd[key]))
            products[sec] = prd
        self._products = products

    @staticmethod
    def _find_a_config_file():
        name_ = 'mitiff_products.cfg'
        home_ = os.path.dirname(os.path.abspath(__file__))
        penv_ = os.environ.get('PPP_CONFIG_DIR', '')
        for fname_ in [os.path.join(x, name_) for x in (home_, penv_)]:
            if os.path.isfile(fname_):
                return fname_
        raise ValueError("Could not find a MiTIFF config file")

def save(scene, filename, product_name=None):
    """Saves the scene as a MITIFF file. This format can be read by DIANA

    """
    print "inside save ... "
    return mitiff_writer(filename, scene, mitiff_product_name=product_name)


def mitiff_writer(filename, root_object, compression=True, mitiff_product_name=None):
    """ Write data to MITIFF file. """
    print "Inside mitiff_writer ... "


    name_ = 'mitiff_products.xml'
    penv_ = os.environ.get('PPP_CONFIG_DIR', '')
    fname_ = os.path.join(penv_,name_)
    if os.path.isfile(fname_):
        config = xml_read.parse_xml(xml_read.get_root(fname_))
    #raise ValueError("Could not find a MiTIFF config file ", fname_)

    
    #if mitiff_product_name:
    #    options = deepcopy(get_product_config(mitiff_product_name))
    #else:
    #    print "No MiTIFF product name given. Skip Config. Sure you want this?"
    #   options = {}


    #print root_object
    tifargs = dict()
    args={}

    from libtiff import TIFF

    tif = TIFF.open(filename, mode ='w')
    #print dir(tif)
    
    #np.set_printoptions(threshold=np.nan)
    
    #tif.TIFFSetField(tif,IMAGEDESCRIPTION,"test")
    tif.SetField(IMAGEDESCRIPTION, "TEST")
    for ch in root_object.channels:
        print ch
        print ch.info.get('units', 'None')
        #print ch.data
        data=ch.data.astype(np.uint8)
        tif.write_image(data,)
        
    tif.close
    
if __name__ == '__main__':
    from mpop.satellites import PolarFactory
    from mpop.projector import get_area_def
    import datetime

    logging.basicConfig(level=logging.DEBUG)

    print "Test saving mitiff."
    orbit = "37582"
    time_slot = datetime.datetime(2016, 5, 24, 15, 25)
    global_data = PolarFactory.create_scene("noaa","19","avhrr/3",time_slot, orbit)
    global_data.load()

    from pprint import pprint
    #pprint(vars(global_data))
    
    local_data = global_data.project("eurol_metno", mode="nearest")
    
    pprint(vars(local_data))
    
    save(local_data,"test.mitiff",product_name="AVHRR")
    print "Complete."
    
    
    
    