#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016.
#from tifffile.tifffile import TIFF_TAGS
from TiffImagePlugin import IMAGEDESCRIPTION
from pyparsing import Upcase
#from libxml2mod import last
#from aifc import data

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

KELVIN_TO_CELSIUS = -273.15

import os
import numpy as np
import logging
from copy import deepcopy
#import xml_read
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
    
    #print "instrument_name: ", root_object.instrument_name
    
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
        
    #print root_object
    tifargs = dict()
    args={}

    from libtiff import TIFF

    tif = TIFF.open(filename, mode ='w')
    #print dir(tif)
    
    #np.set_printoptions(threshold=np.nan)
    
    #Need to generate information to go into the image description
    #This is parsed by DIANA to be used when displaying the data
    image_description = _make_image_description(root_object, product_channels)
    
    print str(image_description)
    #print dtype(image_description)
    tif.SetField(IMAGEDESCRIPTION, str(image_description))
    for ch in product_channels:
        found_channel = False
        print ch.attrib['name']
        for channels in root_object.channels:
            if ch.attrib['name'] == channels.name:
                #Need to scale the data set to mitiff 0-255. 0 is no/missing/bad data.
                logger.debug("min %f max %f value" % (float(ch.attrib['min-val']),float(ch.attrib['max-val'])))
                reverse_offset = 0.
                reverse_scale = 1.
                if ch.attrib['calibration'] == "BT":
                    reverse_offset = 255.
                    reverse_scale = -1.
                    channels.data += KELVIN_TO_CELSIUS
                    #print channels.data
                    
                logger.debug("Reverse offset: %f reverse scale: %f" % ( reverse_offset,reverse_scale))

                _mask = channels.data.mask
                _data = np.clip(channels.data, float(ch.attrib['min-val']),float(ch.attrib['max-val']))

                data=reverse_offset + reverse_scale*(((_data-float(ch.attrib['min-val']))/(float(ch.attrib['max-val']) - float(ch.attrib['min-val'])))*255.)

                data[_mask] = 0

                tif.write_image(data.astype(np.uint8),)
                found_channel = True
                break

        if not found_channel:
            logger.debug("Could not find configured channel in read data set. Fill with empty.")
            fill_channel = np.zeros(root_object.channels[0].data.shape,dtype=np.uint8)
            tif.write_image(fill_channel)
        

    tif.close
    
def _make_image_description(ro, pc):
    #generate image desdcription for mitiff.
    """
     Satellite: NOAA 18
     Date and Time: 06:58 31/05-2016
     SatDir: 0
     Channels:   6 In this file: 1-VIS0.63 2-VIS0.86 3(3B)-IR3.7 4-IR10.8 5-IR11.5 6(3A)-VIS1.6
     Xsize:  4720
     Ysize:  5544
     Map projection: Stereographic
     Proj string: +proj=stere +lon_0=0 +lat_0=90 +lat_ts=60 +ellps=WGS84 +towgs84=0,0,0 +units=km +x_0=2526000.000000 +y_0=5806000.000000
     TrueLat: 60 N
     GridRot: 0
     Xunit:1000 m Yunit: 1000 m
     NPX: 0.000000 NPY: 0.000000
     Ax: 1.000000 Ay: 1.000000 Bx: -2526.000000 By: -262.000000

     Satellite: <satellite name>
     Date and Time: <HH:MM dd/mm-yyyy>
     SatDir: 0
     Channels:   <number of chanels> In this file: <channels names in order>
     Xsize:  <number of pixels x>
     Ysize:  <number of pixels y>
     Map projection: Stereographic
     Proj string: <proj4 string with +x_0 and +y_0 which is the positive distance from proj origo to the lower left corner of the image data>
     TrueLat: 60 N
     GridRot: 0
     Xunit:1000 m Yunit: 1000 m
     NPX: 0.000000 NPY: 0.000000
     Ax: <pixels size x in km> Ay: <pixel size y in km> Bx: <left corner of upper right pixel in km> By: <upper corner of upper right pixel in km>
     
     
     if palette image write special palette
     if normal channel write table calibration:
     Table_calibration: <channel name>, <calibration type>, [<unit>], <no of bits of data>, [<calibration values space separated>]\n\n
    """
    
    _image_description = ''

    _image_description += ' Satellite: '
    if ( ro.satname != None ):
        _image_description += ro.satname.upper()
    if ( ro.number != None ):
        _image_description += ' '+str(ro.number)
    
    _image_description += '\n'
        
    _image_description += ' Date and Time: '
    _image_description += ro.time_slot.strftime("%H:%M %d/%m-%Y\n")
       
    _image_description += ' SatDir: 0\n'
    
    _image_description += ' Channels: '
    _image_description += str(len(pc))
    _image_description += ' In this file: '
    for ch in pc:
        _image_description += ch.attrib['name-alias']
        if ch == pc[-1]:
            _image_description += '\n'
        else:
            _image_description += ' '
       
    _image_description += ' Xsize: '
    _image_description += str(ro.area.x_size) + '\n'
    
    _image_description += ' Ysize: '
    _image_description += str(ro.area.y_size) + '\n'
    
    _image_description += ' Map projection: Stereographic\n'
    _image_description += ' Proj string: ' + ro.area.proj4_string
    if not ("datum","towgs84") in ro.area.proj_dict:
        _image_description += ' +towgs84=0,0,0'

    if not ("units") in ro.area.proj_dict:
        _image_description += ' +units=km'
        
    
    _image_description += ' +x_0=%.6f' % (-ro.area.area_extent[0])
    _image_description += ' +y_0=%.6f' % (-ro.area.area_extent[1])
    
    _image_description += '\n'
    _image_description += ' TrueLat: 60N\n'
    _image_description += ' GridRot: 0\n'
    
    _image_description += ' Xunit:1000 m Yunit: 1000 m\n'

    _image_description += ' NPX: %.6f' % (0)
    _image_description += ' NPY: %.6f' % (0) + '\n'

    _image_description += ' Ax: %.6f' % (ro.area.pixel_size_x/1000.)
    _image_description += ' Ay: %.6f' % (ro.area.pixel_size_y/1000.)
    #But this ads up to upper left corner of upper left pixel.
    _image_description += ' Bx: %.6f' % (ro.area.area_extent[0]/1000.) #LL_x
    _image_description += ' By: %.6f' % (ro.area.area_extent[3]/1000.) #UR_y
    _image_description += '\n'
    
    logger.debug("Area extent: ",ro.area.area_extent)

    for ch in pc:        
        palette=False
        #Make calibration.
        if palette:
            logging.debug("Do palette calibration")
        else:
            _image_description += 'Table_calibration: '
            if 'name-alias' in ch.keys():
                _image_description += ch.attrib['name-alias']
            else:
                _image_description += ch.attrib['name']

            _reverse_offset = 0.;
            _reverse_scale = 1.;

            if ch.attrib['calibration'] == 'RADIANCE':
                _image_description += ', Radiance, '
                _image_description += '[W/m²/µm/sr]'
                _decimals = 8
            elif ch.attrib['calibration'] == 'BT':
                _image_description += ', BT, '
                _image_description += '[°C]'

                _reverse_offset = 255.;
                _reverse_scale = -1.;
                _decimals = 2
            elif ch.attrib['calibration'] == 'REFLECTANCE':
                _image_description += ', Reflectance(Albedo), '
                _image_description += '[%]'
                _decimals = 2

            else:
                logger.warning("Unknown calib type. Must be Radiance, Reflectance or BT.")

            _image_description += ', 8, [ '
            for val in range(0,256):
                #Comma separated list of values
                #calib.append(boost::str(boost::format("%.8f ") % (prod_chan_it->min_val + (val * (prod_chan_it->max_val - prod_chan_it->min_val)) / 255.)));
                _image_description += '{0:.{1}f} '.format((float(ch.attrib['min-val']) + ( (_reverse_offset + _reverse_scale*val) * ( float(ch.attrib['max-val']) - float(ch.attrib['min-val'])))/255.),_decimals)
                
            _image_description += ']\n\n'

    
    return _image_description


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
    
    
    
    