import os
import sys
from uuid import uuid1 as uuid
from lxml import etree
from lxml.builder import ElementMaker
from pylibtiff import TIFFimage
import numpy as np

namespace_map=dict(bf = "http://www.openmicroscopy.org/Schemas/BinaryFile/2010-06",
                   ome = "http://www.openmicroscopy.org/Schemas/OME/2010-06",
                   xsi = "http://www.w3.org/2001/XMLSchema-instance",
                   sa = "http://www.openmicroscopy.org/Schemas/SA/2010-06",
                   spw = "http://www.openmicroscopy.org/Schemas/SPW/2010-06")

# create element makers: bf, ome, xsi
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

def ATTR(namespace, name, value):
    return {'{%s}%s' % (namespace_map[namespace], name): value}

class FileSizeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

def validate_xml(xml):
    if getattr(sys,'frozen',None):
        ome_xsd_path = os.path.dirname(sys.executable)
    elif __file__:  
        ome_xsd_path = os.path.dirname(__file__)
        
    ome_xsd = os.path.join(ome_xsd_path,'ome.xsd')    

    if os.path.isfile (ome_xsd):
        ome_xsd = os.path.join(namespace_map['ome'],'ome.xsd')
        f = open (ome_xsd) 
    else:
        import urllib2
        ome_xsd = os.path.join(namespace_map['ome'],'ome.xsd')
        f = urllib2.urlopen(ome_xsd)
    sys.stdout.write('Validating XML content against %r...' % (ome_xsd))
    xmlschema_doc = etree.parse(f)
    
    xmlschema = etree.XMLSchema(xmlschema_doc)
    if isinstance (xml, basestring):
        xml = etree.parse(xml)
    result = xmlschema.validate(xml)
    if not result:
        sys.stdout.write('FAILED:\n')
        for error in xmlschema.error_log:
            s = str (error)
            for k,v in namespace_map.items():
                s = s.replace ('{%s}' % v, '%s:' % k)
        sys.stdout.write('-----\n')
    else:
        sys.stdout.write('SUCCESS!\n')
    return result

class ElementBase:

    def __init__ (self, parent, root):
        self.parent = parent
        self.root = root
        
        n = self.__class__.__name__
        iter_mth = getattr(parent, 'iter_%s' % (n), None)
        nsn = 'ome'
        nm = n
        if '_' in n:
            nsn, nm = n.split('_',1)
            nsn = nsn.lower()
        ns = eval(nsn)    
        ome_el = getattr (ns, nm, None)

        if iter_mth is not None:
            for element in iter_mth(ome_el):
                root.append(element)
        elif 0:
            print 'NotImplemented: %s.iter_%s(<%s.%s callable>)' % (parent.__class__.__name__, n, nsn, nm)

class TiffDataGenerator:
    
    def __init__(self,instrument,filename,input_data,rotation,scalefact):
        self.instrument = instrument
        self.filename = filename
        self.rotation = rotation
        self.scale = scalefact
        self.data = input_data
#
#    def create_tile(self):
        
#    def create_plane(self):
#        
    def tif_data_from_imaris(self,pixelregion,outChan):
        try:
            imarray = self.data.get_data(self.scale, range(len(outChan)),pixelregion)
            print 'imarray shape=',imarray.shape
            shape_dum = imarray.shape
            if self.instrument == 'Fluorescence':
                im_dtype = np.dtype('uint8')
                if self.rotation == 0:
                    ImageData = np.zeros((len(outChan),shape_dum[0],shape_dum[1]),dtype=im_dtype)
                else:
                    ImageData = np.zeros((len(outChan),shape_dum[1],shape_dum[0]),dtype=im_dtype)
    
                if len(outChan) > 1:
                    idx = -1
                    for c in outChan:
                        idx += 1
                        print("Writing channel:  ", c+1)
                        section = imarray[:,:,c]
                        if self.rotation == 0:
                            SectionRot = section
                        elif self.rotation == 1:
                            SectionRot = np.rot90(section,1)
                        elif self.rotation == 2:
                            SectionRot = np.rot90(section,3)
                        ImageData[idx,:,:] = SectionRot
    
                else:
                    section = imarray[:,:,outChan[0]]
                    if self.rotation == 0:
                        SectionRot = section
                    elif self.rotation == 1:
                        SectionRot = np.rot90(section,1)
                    elif self.rotation == 2:
                        SectionRot = np.rot90(section,3)
                    ImageData[0,:,:] = SectionRot
                
                ImageDataMemSize = SectionRot.nbytes
                if ImageDataMemSize > 2e9:
                    raise FileSizeError(2e9)
                
            if self.instrument == 'Bright-field':
                itype = np.uint8
                im_dtype = np.dtype(dict(names = list('rgb'), formats = [itype]*3))
                ImageData = np.zeros((shape_dum[0],shape_dum[1]),dtype=im_dtype)
                outChan = list('rgb')
                idx = -1
                for c in outChan:
                    idx += 1
                    print("Writing channel:  ", c)
                    section_res = imarray[:,:,idx]
                    ImageData[c][:,:] = section_res
                ImageDataMemSize = 100
    
                      
        except FileSizeError as e:
            msg = "Error encountered: One or more of the tissue sections generated has exceeded " + str(e.value) + " bytes. Try to reduce the file size by writing single channels or by down-scaling the image"                                
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()          
        return ImageData, ImageDataMemSize
            
class Dataset(ElementBase): pass            
class Group(ElementBase): pass
class Experimenter(ElementBase): pass
class Instrument(ElementBase): pass
class Image(ElementBase): pass

class OMEBase:
    """ Base class for OME-XML writers.
    """

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
        tif_gen = TiffDataGenerator(self.instrument,self.tif_filename,self.imarray,self.rotation,self.scalefact)
        tif_data, tif_memsize = tif_gen.tif_data_from_imaris(self.roi,self.outChan)
        self.tif_images[self.instrument,self.tif_filename,self.tif_uuid,self.PhysSize] = tif_data
        s = None
        for (detector, fn, uuid, res), tif_data in self.tif_images.items():
            xml= ome.OME(ATTR('xsi','schemaLocation',"%s %s/ome.xsd" % ((namespace_map['ome'],)*2)),
                          UUID = uuid)
            for item in template_xml:

                if item.tag.endswith('Image') and item.get('ID')!='Image:%s' % (detector):
                    continue
                xml.append(item)
                
            if s is None and validate:
                s = etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
                validate_xml(xml)
            else:
                s = etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
            
            tif_image = TIFFimage(tif_data,description=s)
            print(tif_data.shape)
            tif_image.write_file(fn,compression='lzw') 
            del tif_image  
            #tif_image.description = s
            #tif_image.write_file(fn, compression='none')
            #imsave(fn,tif_data,description=s,photometric='minisblack',resolution=res)
            
            print 'SUCCESS!'

        return s

    def _mk_uuid(self):
        return 'urn:uuid:%s' % (uuid())

    def make_xml(self):
        self.temp_uuid = self._mk_uuid()
        xml = ome.OME(ATTR('xsi','schemaLocation',"%s %s/ome.xsd" % ((namespace_map['ome'],)*2)),
                       UUID = self.temp_uuid)
        for element_cls in self._subelement_classes:
            element_cls(self, xml) # element_cls should append elements to root
        return xml
    
    def make_tif_data(self,instrument,filename,input_data,pixelregion,outChan,rotation,scalefact):
        try:
            imarray = input_data.get_data(scalefact, range(len(outChan)),pixelregion)
            print 'imarray shape=',imarray.shape
            #imdum = imarray[:,:,0]
            #section_dum = imdum[pixelregion[0]:pixelregion[1],pixelregion[2]:pixelregion[3]]
            #shape_dum = section_dum.shape
            shape_dum = imarray.shape
            if instrument == 'Fluorescence':
                im_dtype = np.dtype('uint8')
                if rotation == 0:
                    ImageData = np.zeros((len(outChan),shape_dum[0],shape_dum[1]),dtype=im_dtype)
                else:
                    ImageData = np.zeros((len(outChan),shape_dum[1],shape_dum[0]),dtype=im_dtype)
    
                if len(outChan) > 1:
                    idx = -1
                    for c in outChan:
                        idx += 1
                        print("Writing channel:  ", c+1)
                        #im = imarray[:,:,c]
                        #section = im[pixelregion[0]:pixelregion[1],pixelregion[2]:pixelregion[3]]
                        section = imarray[:,:,c]
                        if rotation == 0:
                            SectionRot = section
                        elif rotation == 1:
                            SectionRot = np.rot90(section,1)
                        elif rotation == 2:
                            SectionRot = np.rot90(section,3)
                        ImageData[idx,:,:] = SectionRot
    
                else:
                    #im = imarray[:,:,outChan[0]]
                    #section = im[pixelregion[0]:pixelregion[1],pixelregion[2]:pixelregion[3]]
                    section = imarray[:,:,outChan[0]]
                    if rotation == 0:
                        SectionRot = section
                    elif rotation == 1:
                        SectionRot = np.rot90(section,1)
                    elif rotation == 2:
                        SectionRot = np.rot90(section,3)
                    ImageData[0,:,:] = SectionRot
                
                ImageDataMemSize = SectionRot.nbytes
                if ImageDataMemSize > 2e9:
                    raise FileSizeError(2e9)
                
            if instrument == 'Bright-field':
                itype = np.uint8
                im_dtype = np.dtype(dict(names = list('rgb'), formats = [itype]*3))
                ImageData = np.zeros((shape_dum[0],shape_dum[1]),dtype=im_dtype)
                outChan = list('rgb')
                idx = -1
                for c in outChan:
                    idx += 1
                    print("Writing channel:  ", c)
                    #im = imarray[:,:,idx]
                    #section_res = im[pixelregion[0]:pixelregion[1],pixelregion[2]:pixelregion[3]]
                    section_res = imarray[:,:,idx]
                    ImageData[c][:,:] = section_res
                ImageDataMemSize = 100
    
                      
        except FileSizeError as e:
            msg = "Error encountered: One or more of the tissue sections generated has exceeded " + str(e.value) + " bytes. Try to reduce the file size by writing single channels or by down-scaling the image"                                
            dial = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()          
        return ImageData, ImageDataMemSize     

    def get_AcquiredDate(self):
        return None

    @staticmethod
    def dtype2PixelIType(dtype):
        return dict (int8='int8',int16='int16',int32='int32',
                     uint8='uint8',uint16='uint16',uint32='uint32',
                     complex128='double-complex', complex64='complex',
                     float64='double', float32='float',
                     ).get(dtype.name, dtype.name)
