#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016.
#from tifffile.tifffile import TIFF_TAGS
from TiffImagePlugin import IMAGEDESCRIPTION
from libxml2mod import last

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

def save(scene, filename, product_name=None):
    """Saves the scene as a MITIFF file. This format can be read by DIANA

    """
    print "inside save ... "
    return mitiff_writer(filename, scene, mitiff_product_name=product_name)


def mitiff_writer(filename, root_object, compression=True, mitiff_product_name=None):
    """ Write data to MITIFF file. """
    print "Inside mitiff_writer ... "

    import xml.etree.ElementTree as etree

    name_ = 'mitiff_products.xml'
    penv_ = os.environ.get('PPP_CONFIG_DIR', '')
    fname_ = os.path.join(penv_,name_)
    if os.path.isfile(fname_):
        tree = etree.parse(fname_)
        root = tree.getroot()

        #config = xml_read.parse_xml(xml_read.get_root(fname_))
    #raise ValueError("Could not find a MiTIFF config file ", fname_)
    
    print "instrument_name: ", root_object.instrument_name
    
    product_list = root.findall("product[@instrument_name='%s']" % (root_object.instrument_name))
    #product_iter = root.iterfind("product[@instrument_name='%s']" % (root_object.instrument_name))

    product_list_length = len(product_list)
    
    if product_list_length == 0:
        raise ValueError("No configuration mitiff product for this instrument is found: ", root_object.instrument_name)
    elif product_list_length != 1:
        raise ValueError("More than one configuration mitiff product for this instrument, '%s',  found. Please check your config." % (root_object.instrument_name))
        

    for elem in product_list:
        print "product_list : ", elem.tag, elem.attrib['instrument_name']

    product_channels = root.findall("product[@instrument_name='%s']/channel" % (root_object.instrument_name))
    for ch in product_channels:
        print ch.items()
        
    #for child in root:
    #    print "loop: ", child
    #    print "loop2: ", child.tag, child.attrib

    #print root_object
    tifargs = dict()
    args={}

    from libtiff import TIFF

    tif = TIFF.open(filename, mode ='w')
    #print dir(tif)
    
    tif.SetField(IMAGEDESCRIPTION, "TEST")
    for ch in product_channels:
        found_channel = False
        print ch.attrib['name']
        for channels in root_object.channels:
            if ch.attrib['name'] == channels.name:
                data=channels.data.astype(np.uint8)
                tif.write_image(data,)
                found_channel = True
                break
        if not found_channel:
            logger.debug("Could not find configured channel in read data set. Fill with empty.")
            fill_channel = np.zeros(root_object.channels[0].data.shape,dtype=np.uint8)
            tif.write_image(fill_channel)
            
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
    
    
    
    