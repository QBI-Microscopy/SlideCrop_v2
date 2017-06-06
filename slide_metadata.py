import h5py
import numpy as np

class SlideImage:
    def __init__(self, filename):
        self.filename = filename
        self.infile = h5py.File(filename,'r')

        #.IMS image parameters(Imaris details, Image Overview, Time, Log and Channel X)
        self.dataSetInfo = self.infile['/DataSetInfo']

        #.IMS image attributes specificallly, Image Overview
        self.imageInfo = self.infile['/DataSetInfo/Image']

        #Number of resolutions full tiff data is in (different resolutions)
        self.resLevels = len(self.infile['/DataSet'])

        #
        self.numChannels = len(self.infile['/DataSet/ResolutionLevel 0/TimePoint 0/'])

        #self.imarray  Created when self.get_data_in_channel(*args, **kwargs) is called

    """
        Returns np.imarray for the specified parameters. 
            selectedRes:  0<= int<= 8 for the desired resolution level
             channelNum: int 
             region: if not None a Region of interest where imarray is the image data for solely that region. 
             region = [top_row_number, bottom_row_number, left_column_number, right_column_number]
    """
    def get_data_in_channel(self, selectedRes, channelNum, region=None):
        # selects resLevel from relevant row of 8x2 np array
        imSize = self.image_size_from_data()[selectedRes]
        respath = '/DataSet/ResolutionLevel ' + str(selectedRes) + '/'
        imrespath = respath + 'TimePoint 0' + '/' + 'Channel ' + str(channelNum)        
        pathToData = self.infile[imrespath]

        # data for selectedRes, ChannelNum at TimePoint 0
        data = pathToData["Data"]

        # Region specified -> change desired region Height and Width
        if region:
            try:
                regionH,regionW = data[0,region[0]:region[1],region[2]:region[3]].shape
                print ('regionW,regionH:',regionW,regionH)
            except:
                regionW = region[3]-region[2]
                regionH = region[1]-region[0]

        #region == None -> select whole image
        else:
            regionW = imSize[0]
            regionH = imSize[1]

        #Create imarray for regionW and regionH
        #if region specified fill with Region of interest (size will be compatible due to above
        # region == None -> duplicate whole image
        im_dtype = np.dtype('uint8')
        self.imarray = np.zeros((1,regionH,regionW),dtype=im_dtype)

        if region:
            try:
                self.imarray[0,:,:] = data[0,region[0]:region[1],region[2]:region[3]]
            except:
                return self.imarray
        else:
            self.imarray[0:,:] = data[0,:,:]            
        return self.imarray  


    """
        Returns np.imarray for the specified parameters. Has alternate to return an imarray with mutiple channels. 
            selectedRes:  0<= int<= 8 for the desired resolution level
            channelNum: int for a single channel data or a [ints] for mulitple levels. 
                        imarray returned will have channels in order specified in channelNum
            region: if not None a Region of interest where imarray is the image data for solely that region. 
                region = [top_row_number, bottom_row_number, left_column_number, right_column_number]
    """
    def get_data(self, selectedRes,channelNum,region=None):

        #get image size for selectedRes and set regionW, regionH depending if region ==None
        imSize = self.image_size_from_data()[selectedRes]
        if region:
            regionW = region[3]-region[2]
            regionH = region[1]-region[0]
        else:
            regionW = imSize[0]
            regionH = imSize[1]
        print ('regionw, regionh:',regionW,regionH)
        im_dtype = np.dtype('uint8')

        #  if more than one input: create an (x,y, numChannels) imarray and populate each with appropriate image data
        #  if region specified, imarray will solely have the areas specfied
        if type(channelNum) == list: #if it is a list we are either pulling RGB or all channels for cropping
            numChannels = self.numChannels
            respath = '/DataSet/ResolutionLevel ' + str(selectedRes) + '/'
#            self.imarray = np.zeros((imSize[1],imSize[0],numChannels),dtype=im_dtype)
            self.imarray = np.zeros((regionH,regionW,numChannels),dtype=im_dtype)
            for ii in range(numChannels):
                imrespath = respath + 'TimePoint 0' + '/' + 'Channel ' + str(ii)
                pathToData = self.infile[imrespath]
                data = pathToData["Data"]
                if region:
                    self.imarray[:,:,ii] = data[0,region[0]:region[1],region[2]:region[3]]
                else:
                    self.imarray[:,:,ii] = data[0,:,:]
        #  else one channel number, and imarray will be a (x,y,1) imarray. Also considers region ==None?
        else:
            numChannels = self.numChannels
            respath = '/DataSet/ResolutionLevel ' + str(selectedRes) + '/'
            imrespath = respath + 'TimePoint 0' + '/' + 'Channel ' + str(channelNum)
#            self.imarray = np.zeros((imSize[1],imSize[0],1))
            self.imarray = np.zeros((regionH,regionW,1),dtype=im_dtype)
            pathToData = self.infile[imrespath]
            data = pathToData["Data"]
            if region:
                self.imarray[:,:,0] = data[0,region[0]:region[1],region[2]:region[3]]
            else:
                self.imarray[:,:,0] = data[0,:,:]            
            #get just a single channel
        return self.imarray        
      

    """
    Return an np.array for the resolution 7 data in channel=0 and timepoint=0
    """
    def display_image(self):
        respath = '/DataSet/ResolutionLevel 7/'
        minrespath = respath + 'TimePoint 0/' + 'Channel 0'
        self.imres7 = self.infile[minrespath]["Data"]
        return self.imres7

    """
    Returns a string representation of the microscope mode. Described in docs as the "Deconvolution parameter"
    """
    def micro_mode(self):
        MM = self.imageInfo.attrs['MicroscopeMode']
        self.micromode = list2str(MM)
        return self.micromode


    def resolution_levels(self):
        self.reslevels = len(self.infile['/DataSet'])
        return self.reslevels

    """
    Returns the number of time_points for the .IMS Data. Specifically for level 0 but should be consistent. 
    """
    def time_points(self):
        numTimePoints = len(self.infile['/DataSet/ResolutionLevel 0/'])
        self.timePoint = numTimePoints
        return self.timePoint


    """
    returns the number of channels in the .IMS file. Specifically for level 0 but should be consistent.
    """
    def channels(self):
        self.numChannels = len(self.infile['/DataSet/ResolutionLevel 0/TimePoint 0/'])                 
        return self.numChannels


    """
    Returns an 8x2 np array with the dimensions for that level. For Each resolution level, i, where 0<=i<=8
    [i, 0], [i, 1] gives the dimensions
    """
    def image_size_from_data(self):
        imSizeArrayFromData = np.zeros((8,2))

        #iterate through all resLevels
        for r in range(self.resLevels):
            res_level = "ResolutionLevel " + str(r)
            path = "/DataSet/" + res_level + "/TimePoint 0/" + "Channel 0"
            pathToData = self.infile[path]
            data = pathToData["Data"]
            #  add dimensions to specified resLevel Row
            imSizeArrayFromData[r,0]= data.shape[2]
            imSizeArrayFromData[r,1]= data.shape[1]
        return imSizeArrayFromData

    """
       Returns an 8x2 np array with the sizes for that level. For Each resolution level, i, where 0<=i<=8
       [i, 0], [i, 1] gives the sizes
    """
    def image_size(self):
        imSizeArray = np.zeros((8,2))
        for r in range(self.resLevels):
            res_level = "ResolutionLevel " + str(r)
            path = "/DataSet/" + res_level + "/TimePoint 0/"
            folder = "Channel 0"
            chanAttribs = dict_builder(self.infile, path, folder, 0)
            sizeX = int(chanAttribs['ImageSizeX'])
            sizeY = int(chanAttribs['ImageSizeY'])
            imSizeArray[r,0] = sizeX
            imSizeArray[r,1] = sizeY

        return imSizeArray

    """
    Returns a tuple of (Min data extension, Max data extensions) where each is an array [3].
        min Data extension is the data origin for the x,y,z dimensions
        Max data extension is the x,y,z maxs
    """
    def extents(self):
        self.extMax = []
        self.extMin = []
        for e in range(3):
            maxstr  = "ExtMax" + str(e)
            extMaxVal = self.imageInfo.attrs[maxstr]
            extMaxVal = int(float(list2str(extMaxVal)))
            self.extMax.append(extMaxVal)
            
            minstr  = "ExtMin" + str(e)
            extMinVal = self.imageInfo.attrs[minstr]
            extMinVal = int(float(list2str(extMinVal)))
            self.extMin.append(extMinVal)
        return self.extMin, self.extMax


    """
    Returns the relative scaling of the res Levels in comparison to resLevel 0
        self.xscale, self.yscale being the relative scalings for each of the levels
        self.xscale[0] = self.xscale[0] =1
    """
    def scale(self):
        self.xscale = []
        self.yscale = []
        slideSize = self.image_size()
        maxressize = slideSize[0]
        Xmax = maxressize[2]
        Ymax = maxressize[1]
        for r in range(self.resLevels):
            slideshape = slideSize[r]
            self.xscale.append(float(slideshape[2]) / float(Xmax))
            self.yscale.append(float(slideshape[1]) / float(Ymax))
            
        return self.xscale, self.xscale


    """
    Returns dataset for all the channels of resolutionLevel0, TimePoint0
    """
    def dataSet_channels(self):
        #extracted from DataSet group
        numchans = self.numChannels
        folder = "Channel "
        path = "/DataSet/ResolutionLevel 0/TimePoint 0/"
        self.DataSetChanList = dict_builder(self.infile, path, folder, numchans)
        return self.DataSetChanList

    """
    Returns the DataSetInfo for the channels 
    """
    def datasetinfo_channels(self):
        #extracted from DataSetInfo group
        numchans = self.numChannels

        folder = "Channel "
        path = "/DataSetInfo/"
        self.DataSetInfoChanList = dict_builder(self.infile, path, folder, numchans)
        return self.DataSetInfoChanList


    """
       List format of self.datasetinfo_channels 
    """
    def get_channel_data(self):
        channelNames = []
        DataSetInfoChanList = self.datasetinfo_channels()
        for chan in range(self.numChannels):
            channelInfo = DataSetInfoChanList[chan]
            channelNames.append(channelInfo['Name'])
        return channelNames

    """
    Series of methods to access the various sections of dataSetInfo. 
    """

    def datasetinfo_image(self):
        folder = "Image"
        path = "/DataSetInfo/"
        self.DataSetInfoImgList = dict_builder(self.infile, path, folder, 0)
        return self.DataSetInfoImgList
        
    def datasetinfo_imaris(self):
        folder = "Imaris"
        path = "/DataSetInfo/"
        self.DataSetInfoImarisList = dict_builder(self.infile, path, folder, 0)
        return self.DataSetInfoImarisList

    def datasetinfo_imarisdataset(self):
        folder = "ImarisDataSet"
        path = "/DataSetInfo/"
        self.DataSetInfoImarisDataSetList = dict_builder(self.infile, path, folder, 0)
        return self.DataSetInfoImarisDataSetList

    def datasetinfo_log(self):
        folder = "Log"
        path = "/DataSetInfo/"
        self.DataSetInfoLogList = dict_builder(self.infile, path, folder, 0)
        return self.DataSetInfoLogList

    def datasetinfo_capture(self):
        folder = "MF Capt Channel "
        path = "/DataSetInfo/"
        numchans = self.numChannels
        self.DataSetInfoCaptList = dict_builder(self.infile, path, folder, numchans)
        return self.DataSetInfoCaptList

    def datasetinfo_time(self):
        folder = "TimeInfo"
        path = "/DataSetInfo/"
        self.DataSetInfoTimeList = dict_builder(self.infile, path, folder, 0)        
        return self.DataSetInfoTimeList
        
        
#Helper functions        
def dict_builder(inputfile,path, folder, numFolders):
        
    numattrs = []
    attrsKeys = []
    
    if numFolders == 0:
        metaDictList = []
        folderstr = folder + "/"
        folderpath = path + folderstr
        datagrp = inputfile[folderpath]
        numattrs = (len(list(datagrp.attrs)))
        attrsKeys = (list(datagrp.attrs))
        metaDict = {}
        for attr in range(numattrs):
            attrKey2str = str(attrsKeys[attr])
            attrValue = list2str(datagrp.attrs[attrKey2str])
            metaDict[attrKey2str] = attrValue

        #sort_chandict = sorted(chandict.iterkeys())
        metaDictList = metaDict
    elif numFolders > 0:
        
        metaDictList = []
        for f in range(numFolders):
            folderstr = folder + str(f) + "/"
            folderpath = path + folderstr
            datagrp = inputfile[folderpath]
            numattrs.append(len(list(datagrp.attrs)))
            attrsKeys.append(list(datagrp.attrs))
            metaDict = {}
            for attr in range(numattrs[f]):
                attrKey2str = str(attrsKeys[f][attr])
                attrValue = list2str(datagrp.attrs[attrKey2str])
                metaDict[attrKey2str] = attrValue
                    
            #sort_chandict = sorted(chandict.iterkeys())
            metaDictList.append(metaDict)
             
    return metaDictList

def list2str(inputarray):
    str_list = []
    for iExt in range(len(inputarray)):
        str_list.append(inputarray[iExt])
        
    return ''.join(str_list)
