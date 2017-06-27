import os
import sys
from uuid import uuid1 as uuid
from lxml import etree
from lxml.builder import ElementMaker
from tifffile import *
# try:
from libtiff import *
# except:
#     import traceback
#     traceback.print_exc()
#     #raw_input('enter to close')
import numpy as np


"""
Setting up xml for the OME through lxml a xml generation API. 
"""
namespace_map=dict(bf = "http://www.openmicroscopy.org/Schemas/BinaryFile/2010-06",
                   ome = "http://www.openmicroscopy.org/Schemas/OME/2010-06",
                   xsi = "http://www.w3.org/2001/XMLSchema-instance",
                   sa = "http://www.openmicroscopy.org/Schemas/SA/2010-06",
                   spw = "http://www.openmicroscopy.org/Schemas/SPW/2010-06")

# create element makers: bioformats, OME, xsi (for XML Schema)
default_validate = False
if default_validate:
    # use this when validating
    ome = ElementMaker (namespace = namespace_map['ome'], nsmap = namespace_map) 
else:
    # use this for creating imagej readable ome.tiff files.
    ome = ElementMaker (nsmap = namespace_map) 

bf = ElementMaker (namespace = namespace_map['bf'], nsmap = namespace_map)
sa = ElementMaker (namespace = namespace_map['sa'], nsmap = namespace_map)
spw = ElementMaker (namespace = namespace_map['spw'], nsmap = namespace_map)


"""
String representation of an Attribute element of a OMETiff/ Metadata. Used in conjunction with an xml element
"""
def ATTR(namespace, name, value):
    return {'{%s}%s' % (namespace_map[namespace], name): value}


"""
Error Subclass for file size errors (i.e. dimensions etc). 
Identical Class also in ome_metadata
"""
class FileSizeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

"""
Validates a given xml (presumably OME metadata) through the given XSD (XML Schema Definition) of OME. 
"""
def validate_xml(xml):

    # getattr(sys,'frozen') is checking whether run in a bundle or live
    if getattr(sys,'frozen'):
        #running in a bundle
        ome_xsd_path = os.path.dirname(sys.executable)
    elif __file__:
        #running live and __file__ is not None
        ome_xsd_path = os.path.dirname(__file__)

    #.xsd file is an xml Schema file
    ome_xsd = os.path.join(ome_xsd_path,'ome.xsd')    

    #if xml schema is file
    if os.path.isfile(ome_xsd):
        ome_xsd = os.path.join(namespace_map['ome'],'ome.xsd')
        f = open (ome_xsd)

    #else must find online
    else:
        import urllib2
        # isn't parsed correctly should contain \\
        ome_xsd = os.path.join(namespace_map['ome'],'ome.xsd')
        f = urllib2.urlopen(ome_xsd)

    #parse xml and parse
    sys.stdout.write('Validating XML content against %r...' % (ome_xsd))
    xmlschema_doc = etree.parse(f)
    
    xmlschema = etree.XMLSchema(xmlschema_doc)

    # base string unresolved reference
    # if xml = is a basestring (pressumably just string
    if isinstance (xml, basestring):
        xml = etree.parse(xml)

    #validate the inputted xml with the xml schema definitions
    result = xmlschema.validate(xml)

    # if failed, output messages
    if not result:
        sys.stdout.write('FAILED:\n')
        for error in xmlschema.error_log:
            s = str (error)
            #refine error message to abbreviations
            for k,v in namespace_map.items():
                s = s.replace ('{%s}' % v, '%s:' % k)
        sys.stdout.write('-----\n')
    else:
        sys.stdout.write('SUCCESS!\n')
    return result

"""
    Abstract Superclass for components in a OMETiff. 
    Has parent, root
    Subclasses include: Dataset, Experimenter, Group, Instrument, Image
"""
class ElementBase:
    def __init__ (self, parent, root):
        #parent must be Object: presumably one with superclass ElementBase
        self.parent = parent
        self.root = root

        # name of must subClass the object is.
        # in practice it won't be ElementBase, rather one of the above subclasses
        n = self.__class__.__name__

        #gets an iterator for the parent Object if iterable. Else assigns None
        iter_mth = getattr(parent, 'iter_%s' % (n), None)


        nsn = 'ome'

        nm = n

        #no preexisting subclasses have self.__class__.__name__ that contain "_"
        #for use in preexisiting XSD which arent OME specified
        if '_' in n:
            nsn, nm = n.split('_',1)
            nsn = nsn.lower()

        #reference outside the class to the above ElementMaker Object
        #if n doesn't contain "_" nsn will be an ome ElementMaker
        #i.e. follow the ome xml definitions and constraints
        ns = eval(nsn)


        # ns.nm if not None
        # functools.partial Object
        ome_el = getattr (ns, nm, None)

        #iterates through
        if iter_mth is not None:
            for element in iter_mth(ome_el):
                root.append(element)
        elif 0:
            print ('NotImplemented: %s.iter_%s(<%s.%s callable>)' % (parent.__class__.__name__, n, nsn, nm))


class Dataset(ElementBase): pass
class Group(ElementBase): pass
class Experimenter(ElementBase): pass
class Instrument(ElementBase): pass
class Image(ElementBase): pass


class TiffImageGenerator:
    """
    Final Class to generate output Tiff Images from predefined input data, rotation and scale factors
    """
    def __init__(self,instrument,filename,input_data,rotation,scalefact,outChan,compression):
        self.instrument = instrument
        self.filename = filename
        self.rotation = rotation
        self.scale = scalefact
        self.data = input_data
        self.channels = outChan
        self.compression = compression


    """
    Creates a .TIFF image from the input variables and returns the tile count of the generated .TIFF 
    """
    def create_tiles(self,roi,sizeX, sizeY, sizeZ, sizeC, sizeT, tileWidth, tileHeight, description):
        tif_image = TIFF.open(self.filename, 'w')
        tile_count = 0

        #iterate though all Colour ranges
        for c in range(0, sizeC):
            if c == 0:
                tif_image.set_description(description)
                
            tif_image.tile_image_params(sizeX,sizeY,sizeC,tileWidth,tileHeight,self.compression)
            channel = self.channels[c]
            tile_num_in_channel = 0
            #iterate through tiles and create singular tiles for each
            for tileOffsetY in range(
                    0, ((sizeY + tileHeight - 1) / tileHeight)):

                for tileOffsetX in range(
                        0, ((sizeX + tileWidth - 1) / tileWidth)):

                    # x,y of top left corner
                    x = tileOffsetX * tileWidth
                    y = tileOffsetY * tileHeight
                    w = tileWidth

                    #if (presumably final) tile is bigger than sizeX (through rounding)
                    # width will be the remaining pixels
                    if (w + x > sizeX):
                        w = sizeX - x

                    # similar as above except for height
                    h = tileHeight
                    if (h + y > sizeY):
                        h = sizeY - y
                    
                    tile_count +=1
                    # Create a single tile for the channel and above calculated values
                    # roi is [top horizontal, bottom horizontal, left vertical, right vertical] of ROI

                    tile_data = self.mktile(roi,channel,x,y,w,h)

                    # ensure dimensions are correct
                    if (h != tile_data.shape[1]) or (w != tile_data.shape[2]):
                        h = tile_data.shape[1]
                        w = tile_data.shape[2]


                    tile_dtype = tile_data.dtype
                    tile = np.zeros((1,tileWidth,tileHeight),dtype=tile_dtype)
                    tile[0,:h,:w] = tile_data[0,:,:]                     
                    tif_image.write_tile(tile,x,y)
                    
            tif_image.WriteDirectory()
        tif_image.close()
        return tile_count


    """
    Make a tile for a given Region of interest and its channel,
    coordinates and rectangular size. 
    """
    def mktile(self,roi,channel,x,y,w,h):
        #row value from total image
        row_start = y + roi[0]

        #h rows down from start
        row_end = row_start + h

        #column value from start of region and distance to top left
        col_start = x + roi[2]

        #w pixels along from start
        col_end = col_start + w

        #roi is top horizontal, bottom horizontal, left vertical and right vertical of ROI
        roi = [row_start,row_end,col_start,col_end]

        #return this pixel array in given channel, scale and roi
        tile_data = self.data.get_data_in_channel(self.scale,channel,roi)
        return tile_data
        
    def create_plane(self,roi,sizeX,sizeY,sizeC,description):
        tif_image = TIFF.open(self.filename, 'w')
        im_dtype = np.dtype('uint8')
        image_data = np.zeros((sizeC,sizeY,sizeX),dtype=im_dtype)
        print ('num channels=',sizeC)
        for c in range(sizeC):

            # add description to tif_image only once
            if c == 0:
                tif_image.set_description(description)
            channel = self.channels[c]

            #image data for roi in channel
            #appears that this could be full image
            imarray = self.mkplane(roi,c)
            print ('imarray shape:',imarray.shape)
            
            print("Writing channel:  ", c+1)

            #  account for rotation given self.rotation
            #  Self.rotation | degrees of rotation
            #        0       |        0
            #        1       |        90
            #        2       |        270
            if self.rotation == 0:
                plane = imarray[0,:,:] 
            if self.rotation == 1:
                plane = np.rot90(imarray[0,:,:],1)
            elif self.rotation == 2:
                plane = np.rot90(imarray[0,:,:],3)

            # add rotated plane to the whole of the given channel, c
            image_data[c,:,:] = plane    

        #write all the image_data to the tiff_image and close()
        tif_image.write_image(image_data, compression=self.compression.encode('ascii','ignore'))
        tif_image.close()

    """
    Returns Numpy Array of data in given channel, scale and roi. 
    """
    def mkplane(self,roi,channel):
        return self.data.get_data_in_channel(self.scale,channel,roi)

class OMEBase:
    """ Base class for OME-XML writers.
    """
    #List of classes where they can be iterated to construct each object
    _subelement_classes = [Dataset, Experimenter, Group, Instrument, Image]

    prefix = ''
    def __init__(self):
        self.tif_images = {}
#        self.cwd = os.path.abspath(os.getcwd())
#        self.output_prefix = os.path.join(self.cwd, self.prefix)
#        if not os.path.exists (self.output_prefix):
#            os.makedirs(self.output_prefix)
#        self.file_prefix = os.path.join(self.output_prefix,'')

    def process(self, options=None, validate=default_validate):
        template_xml = list(self.make_xml())
        tif_gen = TiffImageGenerator(self.instrument,self.tif_filename,self.imarray,self.rotation,self.scalefact,self.outChan,self.compression)
        self.tif_images[self.instrument,self.tif_filename,self.tif_uuid,self.PhysSize] = tif_gen

        s = None
        for (detector, fn, uuid, res), tif_gen in self.tif_images.items():
            xml= ome.OME(ATTR('xsi','schemaLocation',"%s %s/ome.xsd" % ((namespace_map['ome'],)*2)), UUID = uuid)
            for item in template_xml:

                if item.tag.endswith('Image') and item.get('ID')!='Image:%s' % (detector):
                    continue
                xml.append(item)
                
            if s is None and validate:
                s = etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
                validate_xml(xml)
            else:
                s = etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
            
            if (self.sizeX < 4096) and (self.sizeY < 4096):
                tif_gen.create_plane(self.roi,self.sizeX,self.sizeY,self.sizeC,s)
            else:
                tc = tif_gen.create_tiles(self.roi,self.sizeX, self.sizeY, self.sizeZ, self.sizeC, self.sizeT, self.tile_width, self.tile_height, s)
                print ('tile count=',tc)
            print ('SUCCESS!')

        return s

    def _mk_uuid(self):
        return 'urn:uuid:%s' % (uuid())

    def make_xml(self):
        #get specific xml to uuid
        self.temp_uuid = self._mk_uuid()
        xml = ome.OME(ATTR('xsi','schemaLocation',"%s %s/ome.xsd" % ((namespace_map['ome'],)*2)),
                       UUID = self.temp_uuid)

        #create a single of each the Elementbase objects in _subelement_classes
        #  with parent = self (OMEBase) , root = xml
        for element_cls in self._subelement_classes:
            element_cls(self, xml) # element_cls should append elements to root
        return xml   

    def get_AcquiredDate(self):
        return None

    @staticmethod
    def dtype2PixelIType(dtype):
        return dict (int8='int8',int16='int16',int32='int32',
                     uint8='uint8',uint16='uint16',uint32='uint32',
                     complex128='double-complex', complex64='complex',
                     float64='double', float32='float',
                     ).get(dtype.name, dtype.name)
