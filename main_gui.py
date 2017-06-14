import sys
from collections import OrderedDict
import cPickle, os.path
import copy
import wx
from wx.lib.buttons import GenBitmapButton,GenBitmapToggleButton
from wxPython.wx import *
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import wx.aui
import wx.combo
import wx.html
from slide_metadata import SlideImage
from ome_metadata import OMETIFF
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage 
import math
import traceback, types
from wx.lib.embeddedimage import PyEmbeddedImage
import wx.lib.delayedresult as delayedresult
from operator import itemgetter
try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])

try:
    from agw import foldpanelbar as fpb
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.foldpanelbar as fpb

##-----------------------------------------------------------------------
##---------- Set some globals -------------------------------------------
##-----------------------------------------------------------------------

id_SELECT   = wx.NewId()
id_RECT     = wx.NewId()
ID_RECT_ROI_SELECT = 6668

PAGE_WIDTH  = 1000
PAGE_HEIGHT = 1000

im = None
imScaled = None
btnState = None

fluoroList = [  ('TL','rgb'),
                ('Alexa488','green'),
                ('DAPI','blue'),
                ('Alexa555','red'),
                ('Cy5','magenta')]
flouroColors = dict(fluoroList)

colors = [('rgb',[1.0,1.0,1.0]),
        ('grey',[0.5,0.5,0.5]),
        ('red',[1.0,0.0,0.0]),
        ('green',[0.0,1.0,0.0]),
        ('blue',[0.0,0.0,1.0]),
        ('magenta',[1.0,0.0,1.0])]
LUTS = dict(colors)

def setIm(img):
    global im
    im = img

def setImScaled(img):
    global imScaled
    imScaled = img

def GetCollapsedIconData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x8eIDAT8\x8d\xa5\x93-n\xe4@\x10\x85?g\x03\n6lh)\xc4\xd2\x12\xc3\x81\
\xd6\xa2I\x90\x154\xb9\x81\x8f1G\xc8\x11\x16\x86\xcd\xa0\x99F\xb3A\x91\xa1\
\xc9J&\x96L"5lX\xcc\x0bl\xf7v\xb2\x7fZ\xa5\x98\xebU\xbdz\xf5\\\x9deW\x9f\xf8\
H\\\xbfO|{y\x9dT\x15P\x04\x01\x01UPUD\x84\xdb/7YZ\x9f\xa5\n\xce\x97aRU\x8a\
\xdc`\xacA\x00\x04P\xf0!0\xf6\x81\xa0\xf0p\xff9\xfb\x85\xe0|\x19&T)K\x8b\x18\
\xf9\xa3\xe4\xbe\xf3\x8c^#\xc9\xd5\n\xa8*\xc5?\x9a\x01\x8a\xd2b\r\x1cN\xc3\
\x14\t\xce\x97a\xb2F0Ks\xd58\xaa\xc6\xc5\xa6\xf7\xdfya\xe7\xbdR\x13M2\xf9\
\xf9qKQ\x1fi\xf6-\x00~T\xfac\x1dq#\x82,\xe5q\x05\x91D\xba@\xefj\xba1\xf0\xdc\
zzW\xcff&\xb8,\x89\xa8@Q\xd6\xaaf\xdfRm,\xee\xb1BDxr#\xae\xf5|\xddo\xd6\xe2H\
\x18\x15\x84\xa0q@]\xe54\x8d\xa3\xedf\x05M\xe3\xd8Uy\xc4\x15\x8d\xf5\xd7\x8b\
~\x82\x0fh\x0e"\xb0\xad,\xee\xb8c\xbb\x18\xe7\x8e;6\xa5\x89\x04\xde\xff\x1c\
\x16\xef\xe0p\xfa>\x19\x11\xca\x8d\x8d\xe0\x93\x1b\x01\xd8m\xf3(;x\xa5\xef=\
\xb7w\xf3\x1d$\x7f\xc1\xe0\xbd\xa7\xeb\xa0(,"Kc\x12\xc1+\xfd\xe8\tI\xee\xed)\
\xbf\xbcN\xc1{D\x04k\x05#\x12\xfd\xf2a\xde[\x81\x87\xbb\xdf\x9cr\x1a\x87\xd3\
0)\xba>\x83\xd5\xb97o\xe0\xaf\x04\xff\x13?\x00\xd2\xfb\xa9`z\xac\x80w\x00\
\x00\x00\x00IEND\xaeB`\x82' 

def GetCollapsedIconBitmap():
    return wx.BitmapFromImage(GetCollapsedIconImage())

def GetCollapsedIconImage():
    import cStringIO
    stream = cStringIO.StringIO(GetCollapsedIconData())
    return wx.ImageFromStream(stream)

#----------------------------------------------------------------------
def GetExpandedIconData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x9fIDAT8\x8d\x95\x93\xa1\x8e\xdc0\x14EO\xb2\xc4\xd0\xd2\x12\xb7(mI\
\xa4%V\xd1lQT4[4-\x9a\xfe\xc1\xc2|\xc6\xc2~BY\x83:A3E\xd3\xa0*\xa4\xd2\x90H!\
\x95\x0c\r\r\x1fK\x81g\xb2\x99\x84\xb4\x0fY\xd6\xbb\xc7\xf7>=\'Iz\xc3\xbcv\
\xfbn\xb8\x9c\x15 \xe7\xf3\xc7\x0fw\xc9\xbc7\x99\x03\x0e\xfbn0\x99F+\x85R\
\x80RH\x10\x82\x08\xde\x05\x1ef\x90+\xc0\xe1\xd8\ryn\xd0Z-\\A\xb4\xd2\xf7\
\x9e\xfbwoF\xc8\x088\x1c\xbbae\xb3\xe8y&\x9a\xdf\xf5\xbd\xe7\xfem\x84\xa4\
\x97\xccYf\x16\x8d\xdb\xb2a]\xfeX\x18\xc9s\xc3\xe1\x18\xe7\x94\x12cb\xcc\xb5\
\xfa\xb1l8\xf5\x01\xe7\x84\xc7\xb2Y@\xb2\xcc0\x02\xb4\x9a\x88%\xbe\xdc\xb4\
\x9e\xb6Zs\xaa74\xadg[6\x88<\xb7]\xc6\x14\x1dL\x86\xe6\x83\xa0\x81\xba\xda\
\x10\x02x/\xd4\xd5\x06\r\x840!\x9c\x1fM\x92\xf4\x86\x9f\xbf\xfe\x0c\xd6\x9ae\
\xd6u\x8d \xf4\xf5\x165\x9b\x8f\x04\xe1\xc5\xcb\xdb$\x05\x90\xa97@\x04lQas\
\xcd*7\x14\xdb\x9aY\xcb\xb8\\\xe9E\x10|\xbc\xf2^\xb0E\x85\xc95_\x9f\n\xaa/\
\x05\x10\x81\xce\xc9\xa8\xf6><G\xd8\xed\xbbA)X\xd9\x0c\x01\x9a\xc6Q\x14\xd9h\
[\x04\xda\xd6c\xadFkE\xf0\xc2\xab\xd7\xb7\xc9\x08\x00\xf8\xf6\xbd\x1b\x8cQ\
\xd8|\xb9\x0f\xd3\x9a\x8a\xc7\x08\x00\x9f?\xdd%\xde\x07\xda\x93\xc3{\x19C\
\x8a\x9c\x03\x0b8\x17\xe8\x9d\xbf\x02.>\x13\xc0n\xff{PJ\xc5\xfdP\x11""<\xbc\
\xff\x87\xdf\xf8\xbf\xf5\x17FF\xaf\x8f\x8b\xd3\xe6K\x00\x00\x00\x00IEND\xaeB\
`\x82' 

def GetExpandedIconBitmap():
    return wx.BitmapFromImage(GetExpandedIconImage())

def GetExpandedIconImage():
    import cStringIO
    stream = cStringIO.StringIO(GetExpandedIconData())
    return wx.ImageFromStream(stream)

#  Embedded Images for the GUI
#  Stored in Byte form to remove dependency on file directories of installed computers

cross_cursor = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSF"
    "lzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABXS"
    "URBVEiJ7dSxCYAADATAUxzIwt7C5Sx1JAvBwp3iCAZBEEwg3f+RKiJCalmCCOZsp/XiFF74H/Amm"
    "JPZCQMObFk8nl52Nx3WZHZEjxN7qlGPq/DCP4xfsjOJ8V7p1ewAAAAASUVORK5CYII=")

selectIcon = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAB7CAAAewgFu0HU+AAAAu"
    "ElEQVR4nNWWUQ7DIAxDw8TBOBrcLJws/YiG9jEJxyzd5q+qUv1iSKAiN8hy1HsXkeqMOWdS9Y8k35"
    "8BtNZyAeeMPcDMThjQHpww0E2mGYEu4hixNiUY4TmIMphBCzHIScYZ/FEBMhhAeUqAOa8hXzPzZ1U"
    "Fv0ITeL2EoASlFC/ZQ5jZerPVPgHuRQJe3VXV1+pjbXpSOwR4iwyFSL+TA3OwtEIgC8gAQGvXt39b"
    "/gBQRWSMkY1J1AUBBalwYqnTSwAAAABJRU5ErkJggg==")

selectIconSel = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAB7CAAAewgFu0HU+AAAA"
    "v0lEQVR4nOWWUQrDMAxDndF7OUfz0Xwz78NdGGOsspJAYfoKhehZid1WZLOaiJjZJnczO3LVe1/u"
    "rqpm9lju+6F/AExeD5RghgEBIoJmoHdAMwqXzDFqXUQwym1aZTBzUGKQg4Yz+EkGGVOvCoRBAtpL"
    "cjXnR9U3InLt7siWQoKstyo0QWstS84QETGe/BaUAPTiAe/u7p5ntaxN6dpRwFckHmL7N7k2B0Mj"
    "xOUBkgDEOnWD35ZJnUekqrtJu/QEHAdUPF3ltYwAAAAASUVORK5CYII=")

rectIcon = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAB7CAAAewgFu0HU+AAAA"
    "Z0lEQVR4nO3UQQrAMAgEwKX4MJ+mP9OXtYce24Qg2CTFPYbgCMICH+TMiYgAoNtw96Ttj6S5BSwE"
    "0POJ2WKzzHgIaH3tp7XW/jcooIAC/gC8l124UIeAQJV2sv8NCpgPEABVzWYScwGL12U2Mp70JwAA"
    "AABJRU5ErkJggg==")

rectIconSel = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAB7CAAAewgFu0HU+AAAA"
    "bElEQVR4nO2UQQrAIAwE0+K/sk/bp+VpPbSnElGCOdhmTiKyIySsSDKHiJBMSifZ7hOA5emqSvJc"
    "nvuiBD8QNPcWsFicGaYE7tMh7rf2n0EJSlCCLwi6ZRcu1ClBoEp77D+DEgx5tkhVs01ZXE8WEAIa"
    "3vhnAAAAAElFTkSuQmCC")

#  Dictionary of above
toolIconImages = dict([('selectIcon',selectIcon),('selectIconSel',selectIconSel),
                       ('rectIcon',rectIcon),('rectIconSel',rectIconSel)])

#  Embedded image
slidecrop = PyEmbeddedImage(    
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABmUlEQVR42mNgYNgBRYoHGTKvMEReY"
    "ODcDeQyMW8Pym+qXJSV1lXKxbcJoQxKGR5j+Pid4ccPEFr/HCgSXtKw44cDBBXPzsXQcOotVDUYMao"
    "c2vTBBa4ByGbj2IKqYcljZA0MXmcye0vgGrZ8cuYTWY+qwfcsQvX3Hww6R12ie+Aatn5xktdagqph3X"
    "MUG9xPTzsTBtcARBIKK1E1bHuJUP30CwPbLu+09m1fnSCqe/fFYniaew/D3lcg1d9+MCRchghqWc4195"
    "qS0VMiJrcKQwPTLgad8wxRjxl8bzMw7IQIxrsVH5usemm2bHlEAoYGz/sMDT+gyPQKUMTFuO3jZrYfOxg"
    "gSFdxOpIGvgMMNd8QGgo+MjDurI6Og6sGoky/LCQNXPsYSj4jNNR+Z+DYKy64HFlDln8WqpOsrqFokDlRE"
    "xMLV/1lK7ONTg9axD1AaAAimeMnpyrDNXzfwaglPxNVQ+RzhOryLwwsu0w1Jr7bwAHRsKzaDiOUWHYz+"
    "DxkqPnOUPWNQe8SRFBKeGmaT25DfKQAzxq4BgDWVDra1cnrsQAAAABJRU5ErkJggg==")

red = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAYAAADzun+cAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN"
    "1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAjSURBVDiNY/zP"
    "wPCfYQAA00BYOmrxqMWjFo9aPGrxqMV4AQCNGQIcYCGkSgAAAABJRU5ErkJggg==")

green = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAYAAADzun+cAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN"
    "1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAjSURBVDiNY2T4"
    "z/CfYQAA00BYOmrxqMWjFo9aPGrxqMV4AQCMGgIcgkzs/AAAAABJRU5ErkJggg==")

blue = PyEmbeddedImage(    
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAYAAADzun+cAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN"
    "1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAjSURBVDiNY2Rg"
    "+P+fYQAA00BYOmrxqMWjFo9aPGrxqMV4AQCLGwIc4YQlTwAAAABJRU5ErkJggg==")

magenta = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAYAAADzun+cAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN"
    "1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAjSURBVDiNY/zP"
    "8P8/wwAApoGwdNTiUYtHLR61eNTiUYvxAgCabgMbav1ACgAAAABJRU5ErkJggg==")

grey = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAPCAYAAADzun+cAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN"
    "1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABLSURBVDiN7dUx"
    "EQAhDETRD4OXbSMnEmMpau4KBgdMaPINvG53AB8PWgARgaQSMDNx9w1LwsxK4NMs1RpuuOGGb7Rg72dV"
    "xxo8eqcf8RkOPAm/1X0AAAAASUVORK5CYII=")

images = OrderedDict([('grey',grey),('red',red),('green',green),('blue',blue),('magenta',magenta)])

##-----------------------------------------------------------------------
##---------- Main GUI class ---------------------------------------------
##-----------------------------------------------------------------------

class SlideCrop(wx.Frame):

    # ==========================================
    # == Initialisation and Window Management ==
    # ==========================================

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=(700,880), style=wx.DEFAULT_FRAME_STYLE):
        """ Standard constructor.

            'parent', 'id' and 'title' are all passed to the standard wx.Frame
            constructor.  'fileName' is the name and path of a saved file to
            load into this frame, if any.
        """
##        wx.Frame.__init__(self, parent, id, title,
##                         style = wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS |
##                                 wx.NO_FULL_REPAINT_ON_RESIZE)
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._flags = 0
        self.infilename = None
        self.threshold = 255
        self.jobID = 0
        self.userDetails = []
        self.abortEvent = delayedresult.AbortEvent()
        self.SetIcon(slidecrop.GetIcon())
        self.SetMenuBar(self.CreateMenuBar())

        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-4, -3])
        self.statusbar.SetStatusText("Daniel Matthews @ 29 July 2014", 0)
        self.statusbar.SetStatusText("Slide Crop", 1)

        self._leftWindow1 = wx.SashLayoutWindow(self, 101, wx.DefaultPosition,
                                                wx.Size(200, 1000), wx.NO_BORDER |
                                                wx.SW_3D | wx.CLIP_CHILDREN)

        self._leftWindow1.SetDefaultSize(wx.Size(396, 1000))
        self._leftWindow1.SetOrientation(wx.LAYOUT_VERTICAL)
        self._leftWindow1.SetAlignment(wx.LAYOUT_LEFT)
        self._leftWindow1.SetSashVisible(wx.SASH_RIGHT, True)
        self._leftWindow1.SetExtraBorderSize(10)

        self._pnl = 0
        self.Bind(wx.EVT_CHAR_HOOK,self.onKeyEvent)
        self.ReCreateFoldPanel(0)
        # Setup the main drawing area.
##        self.drawPanel = wx.ScrolledWindow(self, -1,
##                            style=wx.SUNKEN_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE,size = (340, 800))
        self.drawPanel = wx.Panel(self,-1,size=(340,800))
        self.drawPanel.SetBackgroundColour(wx.WHITE)
        self.panelSize = self.drawPanel.GetClientSizeTuple()
        #self.drawPanel.EnableScrolling(True, True)
        #self.drawPanel.SetScrollbars(20, 20, PAGE_WIDTH / 20, PAGE_HEIGHT / 20)
        self.ppsx = 10  # pixels per unit scroll step
        self.ppsy = 8
        #self.drawPanel.SetScrollbars(self.ppsx, self.ppsy, self.ppsx, self.ppsy)
##        self.maxWidth = 339
##        self.maxHeight = 950
##        self.drawPanel.SetVirtualSize((self.maxWidth, self.maxHeight))
##        self.drawPanel.SetScrollRate(20,20)
        self.image = None
        self.zoomfactor = -2.5
        self.scale = self.getScaleFactor()
        #self.center = self.calcCenter()
        
        self.drawPanel.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

        self.drawPanel.Bind(wx.EVT_IDLE, self.onIdle)
        self.drawPanel.Bind(wx.EVT_SIZE, self.onSize)
        self.drawPanel.Bind(wx.EVT_PAINT, self.onPaint)
        self.drawPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        #self.drawPanel.Bind(wx.EVT_SCROLLWIN, self.onPanelScroll)

        self.Bind(wx.EVT_TIMER, self.onIdle)

        # Position everything in the window.

##        topSizer = wx.BoxSizer(wx.HORIZONTAL)
##        topSizer.Add(self.toolPalette, 0)
##        topSizer.Add(self.drawPanel, 1, wx.EXPAND)
##
##        self.topPanel.SetAutoLayout(True)
##        self.topPanel.SetSizer(topSizer)
##
##        self.SetSizeHints(250, 200)
##        self.SetSize(wx.Size(600, 400))

##        # Select an initial tool.
##
        self.curToolName = None
        self.curToolIcon = None
        self.curTool = None
        self.setCurrentTool("select")

        # Set initial dc mode to fast
        self.wrapDC = lambda dc: dc

        # Setup our frame to hold the contents of a sketch document.

        self.dirty     = False
        self.fileName  = None
        self.contents  = []     # front-to-back ordered list of DrawingObjects.
        self.selection = []     # List of selected DrawingObjects.
        self.undoStack = []     # Stack of saved contents for undo.
        self.redoStack = []     # Stack of saved contents for redo.

        if self.fileName != None:
            self.loadContents()

        self.displayData = None
        self._initBuffer()

        # Finally, set our initial pen, fill and line options.

        self._setPenColour(wx.RED)
        #self._setFillColour(wx.Colour(215,253,254))
        self._setFillColour(None)
        self._setLineSize(2)
        
        self.backgroundFillBrush = None # create on demand

        self.ID_WINDOW_TOP = 100
        self.ID_WINDOW_LEFT1 = 101
        self.ID_WINDOW_RIGHT1 = 102
        self.ID_WINDOW_BOTTOM = 103
    
##        self._leftWindow1.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnFoldPanelBarDrag,
##                               id=100, id2=103)
        self.Bind(wx.EVT_SIZE, self.onSize)
##        self.Bind(wx.EVT_SCROLL, self.OnSlideColour)     

        # Start the background redraw timer
        # This is optional, but it gives the double-buffered contents a 
        # chance to redraw even when idle events are disabled (like during 
        # resize and scrolling)
        self.redrawTimer = wx.Timer(self)
        self.redrawTimer.Start(700)

    # =============================================
    # == Create the menu bar ======================
    # =============================================

    def CreateMenuBar(self, with_window=False):

        # Make a menubar
        file_menu = wx.Menu()

        SC_QUIT = wx.NewId()
##        FPBTEST_REFRESH = wx.NewId()
##        FPB_BOTTOM_FOLD = wx.NewId()
##        FPB_SINGLE_FOLD = wx.NewId()
##        FPB_EXCLUSIVE_FOLD = wx.NewId()
##        FPBTEST_TOGGLE_WINDOW = wx.NewId()
        SC_ABOUT = wx.NewId()
        SC_HELP = wx.NewId()
        
        file_menu.Append(SC_QUIT, "&Exit")

        option_menu = None

        settings_menu = wx.Menu()

        SC_SETTINGS = wx.NewId()       
        settings_menu.Append(SC_SETTINGS, "&Settings")        

##        if with_window:
##            # Dummy option
##            option_menu = wx.Menu()
##            option_menu.Append(FPBTEST_REFRESH, "&Refresh picture")

##        # make fold panel menu
##        
##        fpb_menu = wx.Menu()
##        fpb_menu.AppendCheckItem(FPB_BOTTOM_FOLD, "Create with &fpb.FPB_COLLAPSE_TO_BOTTOM")
##        
##        # Now Implemented!
##        fpb_menu.AppendCheckItem(FPB_SINGLE_FOLD, "Create with &fpb.FPB_SINGLE_FOLD")
##
##        # Now Implemented!
##        fpb_menu.AppendCheckItem(FPB_EXCLUSIVE_FOLD, "Create with &fpb.FPB_EXCLUSIVE_FOLD")        
##
##        fpb_menu.AppendSeparator()
##        fpb_menu.Append(FPBTEST_TOGGLE_WINDOW, "&Toggle FoldPanelBar")

        help_menu = wx.Menu()
        help_menu.Append(SC_HELP, "&Help")
        help_menu.Append(SC_ABOUT, "&About")

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(settings_menu, "&Settings")
##        menu_bar.Append(fpb_menu, "&FoldPanel")
        
        if option_menu:
            menu_bar.Append(option_menu, "&Options")
            
        menu_bar.Append(help_menu, "&Help")

        self.Bind(wx.EVT_MENU, self.OnAbout, id=SC_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnSettings, id=SC_SETTINGS)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=SC_HELP)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=SC_QUIT)
##        self.Bind(wx.EVT_MENU, self.OnToggleWindow, id=FPBTEST_TOGGLE_WINDOW)
##        self.Bind(wx.EVT_MENU, self.OnCreateBottomStyle, id=FPB_BOTTOM_FOLD)
##        self.Bind(wx.EVT_MENU, self.OnCreateNormalStyle, id=FPB_SINGLE_FOLD)
##        self.Bind(wx.EVT_MENU, self.OnCreateExclusiveStyle, id=FPB_EXCLUSIVE_FOLD)

##        self._bottomstyle = FPB_BOTTOM_FOLD
####        self._singlestyle = FPB_SINGLE_FOLD
##        self._exclusivestyle = FPB_EXCLUSIVE_FOLD

        return menu_bar

    # =============================================
    # == Create the foldpanel =====================
    # =============================================

    def ReCreateFoldPanel(self, fpb_flags):

        # delete earlier panel
        self._leftWindow1.DestroyChildren()

        # recreate the foldpanelbar

        self._pnl = fpb.FoldPanelBar(self._leftWindow1, -1, wx.DefaultPosition,
                                     wx.Size(360,1000), agwStyle=fpb_flags)

        IconImages = wx.ImageList(16,16)
        IconImages.Add(GetExpandedIconBitmap())
        IconImages.Add(GetCollapsedIconBitmap())

        #set caption colour and style
        col1 = wx.Colour(255, 255, 255)
        col2 = wx.Colour(128, 128, 128)
        style = fpb.CaptionBarStyle()
        mystyle = fpb.CAPTIONBAR_GRADIENT_H   
        style.SetFirstColour(col1)
        style.SetSecondColour(col2)
        style.SetCaptionStyle(mystyle)
        
        # "Import Slide" Panel of GUI
        item = self._pnl.AddFoldPanel("Import slide", collapsed=False,
                                      foldIcons=IconImages)
        self._pnl.ApplyCaptionStyle(item, style)
         
        self.fbb = wx.Button(item, -1, "Browse")
        self.Bind(wx.EVT_BUTTON,self.fbbCallback,self.fbb)
        self.fbText = wx.TextCtrl(item,-1,"",(30,50))
        self._pnl.AddFoldPanelWindow(item, self.fbText,
                                     fpb.FPB_ALIGN_WIDTH, 10, 10, 100)
        self._pnl.AddFoldPanelWindow(item, self.fbb,
                                     fpb.FPB_ALIGN_WIDTH, -22, 300, 5)
        self._pnl.AddFoldPanelWindow(item, wx.StaticText(item,-1,""),
                                     fpb.FPB_ALIGN_WIDTH, 5)

        # "Image Processing" Panel of GUI
        item = self._pnl.AddFoldPanel("Image processing", collapsed=False,
                                      foldIcons=IconImages)

        self._pnl.ApplyCaptionStyle(item, style)

##        self.autoSegText = wx.StaticText(item, -1, "Automatic segmentation")
##        self._pnl.AddFoldPanelWindow(item, self.autoSegText,
##                                     fpb.FPB_ALIGN_WIDTH, 5, 20)

        #automatic processing inputs and controls
        self.threshText = wx.StaticText(item, -1, "Threshold:")
        self._pnl.AddFoldPanelWindow(item, self.threshText,
                                     fpb.FPB_ALIGN_WIDTH, 20, 20,300)
        self.thresh = wx.Slider(item, -1, 0, 0, 255,style= wx.SL_LABELS)
        self.Bind(EVT_SCROLL_THUMBRELEASE,self.OnThreshSlider,self.thresh)
        self._pnl.AddFoldPanelWindow(item, self.thresh,fpb.FPB_ALIGN_WIDTH, -15, 80,100)

        self.iterText = wx.StaticText(item, -1, "Iterations:")
        self._pnl.AddFoldPanelWindow(item, self.iterText,
                                     fpb.FPB_ALIGN_WIDTH, 15, 20,300)
        self.iter = wx.TextCtrl(item, -1, "1", (30,50))
        self._pnl.AddFoldPanelWindow(item, self.iter,
                                     fpb.FPB_ALIGN_WIDTH, -15, 80, 240)

        self.eroText = wx.StaticText(item, -1, "Erosion:")
        self._pnl.AddFoldPanelWindow(item, self.eroText,
                                     fpb.FPB_ALIGN_WIDTH, -20, 150,180)
        self.ero = wx.TextCtrl(item, -1, "5", (30,50))
        self._pnl.AddFoldPanelWindow(item, self.ero,
                                     fpb.FPB_ALIGN_WIDTH, -15, 200, 120)

        self.fillText = wx.StaticText(item, -1, "Fill:")
        self._pnl.AddFoldPanelWindow(item, self.fillText,
                                     fpb.FPB_ALIGN_WIDTH, -17, 280,80)
        self.fill = wx.TextCtrl(item, -1, "5", (30,50))
        self._pnl.AddFoldPanelWindow(item, self.fill,
                                     fpb.FPB_ALIGN_WIDTH, -17, 310, 10)
        
        self.procButton = wx.Button(item,-1,"Segment")
        self.Bind(wx.EVT_BUTTON, self.OnSegment,self.procButton)
        self._pnl.AddFoldPanelWindow(item, self.procButton,
                                     fpb.FPB_ALIGN_WIDTH, 20, 20,280)
        self.procAbortButton = wx.Button(item,-1,"Abort")
        self.Bind(wx.EVT_BUTTON, self.OnSegmentAbort,self.procAbortButton)
        self._pnl.AddFoldPanelWindow(item, self.procAbortButton,
                                     fpb.FPB_ALIGN_WIDTH, -23, 100,190)        
        self._pnl.AddFoldPanelWindow(item, wx.StaticText(item, -1, ""),
                                     fpb.FPB_ALIGN_WIDTH, 5)        
##        self._pnl.AddFoldPanelSeparator(item)
##        
##        #manual region definition
##        self.manSegText = wx.StaticText(item, -1, "Manual segmentation")
##        self._pnl.AddFoldPanelWindow(item, self.manSegText,
##                                     fpb.FPB_ALIGN_WIDTH, 5, 20)

        self.rectIcon = wx.ToggleButton(item,id_RECT,"Draw")
        self.selectIcon = wx.ToggleButton(item,id_SELECT,"Select")
##        self.selectIcon  = ToolPaletteToggle(item, id_SELECT,
##                                           "select", "Selection Tool", mode=wx.ITEM_RADIO)
##        self.rectIcon    = ToolPaletteToggle(item, id_RECT,
##                                           "rect", "Rectangle Tool", mode=wx.ITEM_RADIO)
        # Create the tools for Select and Draw buttons
        self.tools = {
            'select'  : (self.selectIcon,   SelectDrawingTool()),
            'rect'    : (self.rectIcon,     RectDrawingTool())
        }

        for tool in self.tools.itervalues():
            tool[0].Bind(wx.EVT_TOGGLEBUTTON,    self.onChooseTool)

        self.Bind(wx.EVT_BUTTON, self.onChooseTool,self.selectIcon)      

        self._pnl.AddFoldPanelWindow(item, self.selectIcon,
                                     fpb.FPB_ALIGN_WIDTH,-41,190,100)
        self._pnl.AddFoldPanelWindow(item, self.rectIcon,
                                 fpb.FPB_ALIGN_WIDTH,-23,280,10)







        # "Regions of Interest" Gui fold panel

        item = self._pnl.AddFoldPanel("Regions of interest", False, foldIcons=IconImages)
        style.SetFirstColour(col1)
        style.SetSecondColour(col2)
        style.SetCaptionStyle(mystyle)
        self._pnl.ApplyCaptionStyle(item, style)

        #create the checkbox list
        self.list = CheckListCtrl(item)

        self.list.InsertColumn(0, "X")
        self.list.InsertColumn(1, "Y")
        self.list.InsertColumn(2, "W")
        self.list.InsertColumn(3, "H")

##        for key, data in musicdata.iteritems():
##            print(key)
##            index = self.list.InsertStringItem(sys.maxint, data[0])
##            self.list.SetStringItem(index, 1, data[1])
##            self.list.SetStringItem(index, 2, data[2])
##            self.list.SetStringItem(index, 3, data[3])            
##            self.list.SetItemData(index, key)
      
        self.list.SetColumnWidth(0, 90)
        self.list.SetColumnWidth(1, 90)
        self.list.SetColumnWidth(2, 90)
        self.list.SetColumnWidth(3, 90)
##        self.list.CheckItem(4)
##        self.list.CheckItem(7)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
        
        self._pnl.AddFoldPanelWindow(item, self.list, fpb.FPB_ALIGN_WIDTH,
                                     fpb.FPB_DEFAULT_SPACING, 10)
        

        #select/deselect buttons
        ID_SelectAll = wx.NewId()
        ID_DeselectAll = wx.NewId()
        self.selectAll = wx.Button(item, ID_SelectAll, "Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll,self.selectAll)
        self._pnl.AddFoldPanelWindow(item, self.selectAll,fpb.FPB_ALIGN_WIDTH,5,50,200)
        
        self.deSelectAll = wx.Button(item, ID_DeselectAll, "Deselect All")
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll,self.deSelectAll)
        self._pnl.AddFoldPanelWindow(item, self.deSelectAll,fpb.FPB_ALIGN_WIDTH,-23,200,50)

        #channel selection
        self.ID_ALLCHANS = wx.NewId()
        self.ID_SELECCHANS = wx.NewId()
        self.radio1 = wx.RadioButton(item, self.ID_ALLCHANS, "&All Channels")
        self.radio2 = wx.RadioButton(item, self.ID_SELECCHANS, "&Selected channels")
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChannelSelect,self.radio1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChannelSelect,self.radio2)
        self.radio1.SetValue(True)
        self._pnl.AddFoldPanelWindow(item, self.radio1, fpb.FPB_ALIGN_WIDTH, 10,20,250) 
        self._pnl.AddFoldPanelWindow(item, self.radio2, fpb.FPB_ALIGN_WIDTH, 10,20,250)

        self.scaleText = wx.StaticText(item, -1, "Output scale:")
        self._pnl.AddFoldPanelWindow(item,self.scaleText,
                                     fpb.FPB_ALIGN_WIDTH, -38, 210,95)
        self.scaleCombo = wx.ComboBox(item, -1, value="1", choices=["1", "2", "4", "8", "16"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnScaleChange,self.scaleCombo)
        self._pnl.AddFoldPanelWindow(item,self.scaleCombo,
                                     fpb.FPB_ALIGN_WIDTH, -15, 280,30)
        #self.rotText = wx.StaticText(item, -1, "Rotation:")
        #self._pnl.AddFoldPanelWindow(item, self.rotText,
        #                             fpb.FPB_ALIGN_WIDTH, 10, 210,95)
        #self.rotationCombo = wx.ComboBox(item, -1, value="Original",choices=["Original", "Left 90", "Right 90"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        #self._pnl.AddFoldPanelWindow(item,self.rotationCombo,
        #                             fpb.FPB_ALIGN_WIDTH, -15, 280,30)
        self.chansText = wx.StaticText(item, -1, "Channels:")
        self._pnl.AddFoldPanelWindow(item, self.chansText,
                                     fpb.FPB_ALIGN_WIDTH, 25, 30,300)
        self.chans = wx.TextCtrl(item, -1, "",style=wx.TE_CENTRE)
        self._pnl.AddFoldPanelWindow(item, self.chans,
                                     fpb.FPB_ALIGN_WIDTH, -15, 90, 220)
        self.comprText = wx.StaticText(item, -1, "Compression:")
        self._pnl.AddFoldPanelWindow(item, self.comprText,
                                 fpb.FPB_ALIGN_WIDTH, -20, 210,95)
        self.comprCombo = wx.ComboBox(item, -1, value="lzw",choices=["lzw", "jpeg"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._pnl.AddFoldPanelWindow(item,self.comprCombo,
                                     fpb.FPB_ALIGN_WIDTH, -15, 280,30)
        
        ID_CROP = wx.NewId()
        ID_ABORT = wx.NewId()
        self.crop = wx.Button(item, ID_CROP, "Crop")
        self.Bind(wx.EVT_BUTTON, self.OnCrop,self.crop)
        self._pnl.AddFoldPanelWindow(item, self.crop)
        self.abortCrop = wx.Button(item, ID_ABORT, "Abort Crop!")
        self.Bind(wx.EVT_BUTTON, self.OnAbortCrop,self.abortCrop)
        self._pnl.AddFoldPanelWindow(item, self.abortCrop)            
        self._pnl.AddFoldPanelWindow(item, wx.StaticText(item,-1,""),
                                     fpb.FPB_ALIGN_WIDTH, 5)

        # "Display options" Gui fold panel
        item = self._pnl.AddFoldPanel("Display options", collapsed=False,
                                      foldIcons=IconImages)
        self.dispOpts = item
        self._pnl.ApplyCaptionStyle(item, style)
        
        self.cb = wx.Choice(item, -1, (120, 50),choices=[])
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self.cb)

        self.bcb = wx.combo.BitmapComboBox(item, -1,"",choices=[],style=wx.CB_READONLY)

        # add options to bitmap combo box (choice box on right)
        for k, img in images.iteritems():
            name = k
            obj = img
            img = obj.GetImage()
            bmp = img.ConvertToBitmap()
            self.bcb.Append(name, bmp)
        self.bcb.SetSelection(0)
        self.bcb.Show()

        # bind bcb Combo Box selection to event
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo, self.bcb)

        # add above to panel
        self._pnl.AddFoldPanelWindow(item, self.cb,
                                 fpb.FPB_ALIGN_WIDTH,5,10,270)
        self._pnl.AddFoldPanelWindow(item, self.bcb,
                                 fpb.FPB_ALIGN_WIDTH,-21,130,150)
        self._pnl.AddFoldPanelWindow(item, wx.StaticText(item,-1,""),
                                     fpb.FPB_ALIGN_WIDTH, 5)        
        self.dispOpts.Hide()

    # =============================================
    # == Window resize ============================
    # =============================================

    def onSize(self, event):

        wx.LayoutAlgorithm().LayoutWindow(self, self.drawPanel)
        #self.updateSize()
        self.requestRedraw()
        event.Skip()

    # =============================================
    # == Menu callbacks ===========================
    # =============================================
        

    def OnQuit(self, event):
 
        self.Destroy()

    ## dialog box for user details display
    def OnSettings(self,event):
        dlg = SettingsDialog(self, -1, "User Details", size=(500, 400),
                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                         style=wx.DEFAULT_DIALOG_STYLE )
        dlg.CenterOnScreen()

        #set the dialog to the currently stored userdetails
        dlg.setUserDetails(self.userDetails)

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()

        #reset the currently stored userdetails to whatever is in the dialog
        self.userDetails = dlg.getUserDetails()
        dlg.Destroy()


    def OnAbout(self, event):

        msg = "This tool provides a means to extract (or crop)\n" + \
              "individual tissue sections from Slide Scanner images.\n" + \
              "Currently only images in the Imaris image format are supported.\n\n" + \
              "Author: Daniel Matthews @ December 2013\n\n" + \
              "Please report any bug/requests or improvements\n\n" + \
              "To me at the following adress:\n\n" + \
              "d.matthews1@uq.edu.au\n\n"
              
        dlg = wx.MessageDialog(self, msg, "SlideCrop",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False, "Verdana"))
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self,event):
        helpfrm = HtmlHelpFrame(None, "SlideCrop Help")
##        helpfrm.setContent("Here is some <b>formatted</b> <i><u>text</u></i> "
##            "loaded from a <font color=\"red\">string</font>.")
        helpfrm.Show()

    def OnToggleWindow(self, event):
        
        self._leftWindow1.Show(not self._leftWindow1.IsShown())
        # Leaves bits of itself behind sometimes
        wx.LayoutAlgorithm().LayoutWindow(self, self.drawPanel)
        self.drawPanel.Refresh()

        event.Skip()

    # =============================================
    # == Events ========
    # =============================================

    def onKeyEvent(self, event):
        """ Respond to a keypress event.

            We make the arrow keys move the selected object(s) by one pixel in
            the given direction.
        """
        step = 1
        if event.ShiftDown():
            step = 20
        if event.GetKeyCode() == wx.WXK_UP:
            self._moveObject(0, -step)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self._moveObject(0, step)
        elif event.GetKeyCode() == wx.WXK_LEFT:
            self._moveObject(-step, 0)
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            self._moveObject(step, 0)
        elif event.GetKeyCode() == wx.WXK_DELETE:
            if self.selection:
                self.deleteSelectedObjects(self.selection)
        else:
            event.Skip()


    def onMouseEvent(self, event):
        """ Respond to mouse events in the main drawing panel

            How we respond depends on the currently selected tool.
        """
        if self.curTool is None: return
        if self.image is None: return
        # Translate event into canvas coordinates and pass to current tool
        origx,origy = event.X, event.Y
        pt = self._getEventCoordinates(event)

        #magic numbers to prevent drawing outside image area
        if self.image:
            limits = imScaled.GetSize()
        else:
            limits = [self.MaxWidth,self.MaxHeight]            
        if (pt.x > limits[0]):
            pt.x = limits[0]
        if (pt.y > limits[1]):
            pt.y = limits[1]
        event.m_x = pt.x
        event.m_y = pt.y
        handled = self.curTool.onMouseEvent(self,event)
        event.m_x = origx
        event.m_y = origy
        if self.image:
            displayScale = self._getOutputScale()
            scaledXpos = float(pt.x/self.scale)*displayScale[0]
            scaledYpos = float(pt.y/self.scale)*displayScale[1]
            self.SetStatusText("x:"+str(int(scaledXpos))+", "+"y:"+str(int(scaledYpos)))
        
        if event.LeftUp():
            if self.curToolName == 'rect':
                key = len(self.contents)-1
                obj = self.contents[-1]
                self._addItemToList(obj,key,self.scaleCombo.GetSelection())
            if self.curToolName == 'select':
                self.list.DeleteAllItems()
                for obj in self.contents:
                    key = self.contents.index(obj)
                    self._addItemToList(obj,key,self.scaleCombo.GetSelection())
        if handled: return

        # otherwise handle it ourselves
        if event.RightDown():
            self.doPopupContextMenu(event)

    def OnThreshSlider(self, event):
        ts = event.GetEventObject()
        self.threshold = 255-ts.GetValue()
        try:
            colour = flouroColors[self.curChannelName]
        except:
            colour = 'grey'        
        self.RetrieveImage(self.curChannelIdx,colour)

    def OnChoice(self,event):
        cb = event.GetEventObject()
        self.curChannelIdx = event.GetInt()
        self.curChannelName  = cb.GetString(self.curChannelIdx)
        try:
            colour = flouroColors[self.curChannelName]
        except:
            colour = 'grey'
        self.RetrieveImage(self.curChannelIdx,colour)
        idx = images.keys().index(colour)
        self.bcb.SetSelection(idx)

    def OnCombo(self,event):
        bcb = event.GetEventObject()
        idx = event.GetInt()
        st  = bcb.GetString(idx)
        self.RetrieveImage(self.curChannelIdx,st)
        flouroColors[self.curChannelName] = st

    def OnScaleChange(self,event):        
        sc = event.GetEventObject()
        idx = event.GetInt()
        #get the items that are checked
        checked = []
        for item in range(self.list.GetItemCount()):
            if self.list.IsChecked(item):
                checked.append(item)

        #wipe the table and repopulate
        self.list.DeleteAllItems()
        for obj in self.contents:
            key = self.contents.index(obj)
            self._addItemToList(obj,key,idx)

        #recheck the previously checked items
        for item in checked:
            self.list.CheckItem(item)
        

##    def doPopupContextMenu(self, event):
##        """ Respond to the user right-clicking within our drawing panel.
##
##            We select the clicked-on item, if necessary, and display a pop-up
##            menu of available options which can be applied to the selected
##            item(s).
##        """
##        mousePt = self._getEventCoordinates(event)
##        obj = self.getObjectAt(mousePt)
##
##        if obj == None: return # Nothing selected.
##
##        # Select the clicked-on object.
##
##        self.select(obj)
##
##        # Build our pop-up menu.
##
##        menu = wx.Menu()
##        menu.Append(menu_DUPLICATE, "Duplicate")
##        menu.Append(menu_EDIT_PROPS,"Edit...")
##        menu.Append(wx.ID_CLEAR,    "Delete")
##        menu.AppendSeparator()
##        menu.Append(menu_MOVE_FORWARD,   "Move Forward")
##        menu.Append(menu_MOVE_TO_FRONT,  "Move to Front")
##        menu.Append(menu_MOVE_BACKWARD,  "Move Backward")
##        menu.Append(menu_MOVE_TO_BACK,   "Move to Back")
##
##        menu.Enable(menu_EDIT_PROPS,    obj.hasPropertyEditor())
##        menu.Enable(menu_MOVE_FORWARD,  obj != self.contents[0])
##        menu.Enable(menu_MOVE_TO_FRONT, obj != self.contents[0])
##        menu.Enable(menu_MOVE_BACKWARD, obj != self.contents[-1])
##        menu.Enable(menu_MOVE_TO_BACK,  obj != self.contents[-1])
##
##        self.Bind(wx.EVT_MENU, self.doDuplicate,   id=menu_DUPLICATE)
##        self.Bind(wx.EVT_MENU, self.doEditObject,  id=menu_EDIT_PROPS)
##        self.Bind(wx.EVT_MENU, self.doDelete,      id=wx.ID_CLEAR)
##        self.Bind(wx.EVT_MENU, self.doMoveForward, id=menu_MOVE_FORWARD)
##        self.Bind(wx.EVT_MENU, self.doMoveToFront, id=menu_MOVE_TO_FRONT)
##        self.Bind(wx.EVT_MENU, self.doMoveBackward,id=menu_MOVE_BACKWARD)
##        self.Bind(wx.EVT_MENU, self.doMoveToBack,  id=menu_MOVE_TO_BACK)  
##                            
##        # Show the pop-up menu.
##
##        clickPt = wx.Point(mousePt.x + self.drawPanel.GetPosition().x,
##                          mousePt.y + self.drawPanel.GetPosition().y)
##        self.drawPanel.PopupMenu(menu, mousePt)
##        menu.Destroy()

    def setNewImageParams(self):
        'called by LoadImage()'
        self.drawPanel.SetVirtualSize((imScaled.GetWidth(), imScaled.GetHeight()))

    def getScaleFactor(self):
        return float(2**self.zoomfactor)        

    # =============================================
    # == Screen and object display methods ========
    # =============================================
    
    def onIdle(self, event):
        """
        If the size was changed then resize the bitmap used for double
        buffering to match the window size.  We do it in Idle time so
        there is only one refresh after resizing is done, not lots while
        it is happening.
        """
        if self._reInitBuffer and self.IsShown():
            self._initBuffer()
            self.drawPanel.Refresh(False)

    def requestRedraw(self):
        """Requests a redraw of the drawing panel contents.

        The actual redrawing doesn't happen until the next idle time.
        """
        self._reInitBuffer = True

    def onPaint(self, event):
        """
        Called when the window is exposed.
        """
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.
        dc = wx.BufferedPaintDC(self.drawPanel, self.buffer, wx.BUFFER_VIRTUAL_AREA)
##        if wx.Platform != '__WXMSW__':
##            return
##
##        # First get the update rects and subtract off the part that 
##        # self.buffer has correct already
##        region = self.drawPanel.GetUpdateRegion()
##        panelRect = self.drawPanel.GetClientRect()
##        offset = list(self.drawPanel.CalcUnscrolledPosition(0,0))
##        offset[0] -= self.saved_offset[0]
##        offset[1] -= self.saved_offset[1]
##        region.Subtract(-offset[0],- offset[1],panelRect.Width, panelRect.Height)
##
##        # Now iterate over the remaining region rects and fill in with a pattern
##        rgn_iter = wx.RegionIterator(region)
##        if rgn_iter.HaveRects():
##            #self.setBackgroundMissingFillStyle(dc)
##            offset = self.drawPanel.CalcUnscrolledPosition(0,0)
##        while rgn_iter:
##            r = rgn_iter.GetRect()
##            if r.Size != self.drawPanel.ClientSize:
##                dc.DrawRectangleRect(r)
##            rgn_iter.Next()        
            
    def setBackgroundMissingFillStyle(self, dc):
        if self.backgroundFillBrush is None:
            # Win95 can only handle a 8x8 stipple bitmaps max
            #stippleBitmap = wx.BitmapFromBits("\xf0"*4 + "\x0f"*4,8,8)
            # ...but who uses Win95?
            stippleBitmap = wx.BitmapFromBits("\x06",2,2)
            stippleBitmap.SetMask(wx.Mask(stippleBitmap))
            bgbrush = wx.Brush(wx.WHITE, wx.STIPPLE_MASK_OPAQUE)
            bgbrush.SetStipple(stippleBitmap)
            self.backgroundFillBrush = bgbrush

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(self.backgroundFillBrush)
        dc.SetTextForeground(wx.LIGHT_GREY)
        dc.SetTextBackground(wx.WHITE)
            

    def onEraseBackground(self, event):
        """
        Overridden to do nothing to prevent flicker
        """
        pass


    def onPanelScroll(self, event):
        """
        Called when the user changes scrolls the drawPanel
        """
        # make a note to ourselves to redraw when we get a chance
        self.requestRedraw()
        event.Skip()
        pass

    def display(self,dc):
##        self.image = self.getIm()
        self.image = imScaled
        if self.image:
            #dc = wxClientDC(self)
            #self.PrepareDC(dc)
            #ox, oy = self.drawPanel.CalcUnscrolledPosition(0, 0)
            dc.DrawBitmap(self.image.ConvertToBitmap(), 0, 0)

    def drawContents(self, dc):
        """
        Does the actual drawing of all drawing contents with the specified dc
        """
        # PrepareDC sets the device origin according to current scrolling
        self.drawPanel.PrepareDC(dc)

        gdc = self.wrapDC(dc)

        # First pass draws objects
        ordered_selection = []
        for obj in self.contents[::-1]:
            if obj in self.selection:
                obj.draw(gdc, True)
                ordered_selection.append(obj)
            else:
                obj.draw(gdc, False)

        # First pass draws objects
        if self.curTool is not None:
            self.curTool.draw(gdc)

        # Second pass draws selection handles so they're always on top
        for obj in ordered_selection:
            obj.drawHandles(gdc)
        
##    def setDisplayScale(self):
##        if self.displayData:
##            W = self.displayData.GetWidth()
##            H = self.displayData.GetHeight()
##            if W > H:
##                NewW = self.panelSize
##                NewH = self.panelSize[1] * H / W
##            else:
##                NewH = self.panelSize
##                NewW = self.panelSize[0] * W / H
##            newscale = NewW / W

    # =============================================
    # == Import Data Methods ======================
    # =============================================

    def fbbCallback(self,evt):
        filters = 'Imaris files (*.ims)|*.ims'
        dialog = wx.FileDialog( None, message = 'Open a slide image ...', wildcard=filters, style = wx.OPEN | wx.MULTIPLE )
        # dialog box to import .IMS file
        if dialog.ShowModal() == wx.ID_OK:
            if self.image and self.contents:
                self.wipeOldData()
            self.selectedFile = dialog.GetPaths()

        # Setting the Data values for use in GUI and back-end proccessing
        for selection in self.selectedFile:
            self.infilename = selection
            self.ImarisInput = SlideImage(self.infilename)
            self.numchannels = self.ImarisInput.channels()
            self.mode = self.ImarisInput.micro_mode()
            self.sizeArray = self.ImarisInput.image_size()
            self.inresLevel = 5
            if self.mode == 'MetaCyte FL':
                self.curChannelIdx = 0
                self.curChannelName = self.ImarisInput.get_channel_data()[self.curChannelIdx]
                self.assignChannelsCombo(self.ImarisInput.get_channel_data())
                self.radio1.Show()
                self.radio2.Show()
                self.chans.Show()
                self.chansText.Show()

            # if its not a "metaCyte FL" mode than hide the following:
            #     -  radio 1: "All Channels" select radio button
            #     -  radio 2: "Selected Channels" select radio button
            #     -  chans and chansText: The text field for specifying specific values
            else:
                self.curChannelIdx = [0,1,2]
                self.curChannelName = 'TL'
                self.radio1.Hide()
                self.radio2.Hide()
                self.chans.Hide()
                self.chansText.Hide()

            # Try to specify Channel Colour, default grey
            try:
                colour = flouroColors[self.curChannelName]
            except:
                colour = 'grey'
            self.RetrieveImage(self.curChannelIdx,colour)
        self.fbText.SetValue(selection)

    """
    Resets Gui void of previous data settings. 
    - removes the list of "Display options" options
    - empties self.com (Always empty and is never used)
    - Removes all ROI from "Regions of interest" Table
    - empties list of DrawingObjects
    """
    def wipeOldData(self):
        self.com = []
        self.dispOpts.Hide()
        self.list.DeleteAllItems()
        if self.contents:
            self.contents = []


    """
    Retrieves and configures the GUI image for the Imaris Data at the given channel Num and colour option
    """
    def RetrieveImage(self,channelNum,colour):
        # get Slide data from SlideImage object for inresLevel and channelNum
        self.wholeSlideData = self.ImarisInput.get_data(self.inresLevel, channelNum)

        # converts image into a String representation and sets it as the global variable im
        self.displayData = self.GetwxImage(self.wholeSlideData,colour)
        setIm(self.displayData)

        # redraw, configure and refresh the new image
        self.rescaleDisplayImage()
        self.requestRedraw()
        self.setNewImageParams()
        self.drawPanel.Refresh()

        # set Display option choice box options if correct mode
        if self.mode == 'MetaCyte FL':
            idx = images.keys().index(colour)
            self.bcb.SetSelection(idx)
            self.dispOpts.Show()


    """
    return a wxImage Object from the given .IMS data and desired colour
    """
    def GetwxImage( self, plane, colour):
        r,g,b = self.assignColors(plane,colour)
        imwidth = plane.shape[1]
        imheight = plane.shape[0]
        array = np.zeros( (imheight, imwidth, 3), dtype = np.dtype('uint8'))
        array[:,:,0] = r
        array[:,:,1] = g
        array[:,:,2] = b
        image = wx.EmptyImage(imwidth,imheight)
        image.SetData( array.tostring())
        return image

    """
    Returns an r,g,b repreentation of the desired plane with the given colour as a weighting factor. 
    colour must be in LUTS.keys()
    """
    def assignColors(self,plane,colour):
        cmap = LUTS[colour]
        bw = self.applyThreshold(plane)
        if self.mode == 'MetaCyte FL':
            r = plane[:,:,0]*cmap[0]
            g = plane[:,:,0]*cmap[1]
            b = plane[:,:,0]*cmap[2]
            r[bw] = 255
            g[bw] = 255 
        else:
            r = plane[:,:,0]*cmap[0]
            g = plane[:,:,1]*cmap[1]
            b = plane[:,:,2]*cmap[2]
            r[bw] = 255           
        return r,g,b


    def applyThreshold(self,plane):
        if self.mode == 'MetaCyte TL':
        #   return plane of x,y,0 and invert
            inverted = plane[:,:,0]
            inverted = np.subtract(255,inverted)
            bw = (inverted > 0) & (inverted > self.threshold)

        elif self.mode == 'MetaCyte FL':        
            bw = (plane[:,:,0] > 0) & (plane[:,:,0] > self.threshold)
        return bw

    """
    ReScales the display image 
    """
    def rescaleDisplayImage(self):
        self.scale = float(self.panelSize[1]) / float(self.displayData.GetHeight())
        newWidth = int(self.displayData.GetWidth() * self.scale)
        newHeight = int(self.displayData.GetHeight() * self.scale)
        imgScaled = self.displayData.Scale(newWidth, newHeight,wx.IMAGE_QUALITY_NORMAL)
        setImScaled(imgScaled)

    """
    Adds the possible channels into the "Display options" check boxes    
    """
    def assignChannelsCombo(self,channelNames):
        for chan in channelNames:
            self.cb.Append(chan)
        self.cb.SetSelection(0)
        self.cb.Show()
            
    # =============================================
    # == Object Creation and Destruction Methods ==
    # =============================================

    def addObject(self, obj, select=True):
        """Add a new drawing object to the canvas.
        
        If select is True then also select the object
        """
        #self.saveUndoInfo()
        #self.contents.insert(0,obj)
        self.contents.append(obj)
        self.dirty = True
        if select:
            self.select(obj)
        #self.setCurrentTool('select')

    def deleteSelectedObjects(self,selected):
        for obj in selected:
            idx = self.contents.index(obj)
            self.contents.pop(idx)
        self.requestRedraw()
        self.list.DeleteAllItems()
        for idx in reversed(range(len(self.contents))):
                obj = self.contents[idx]
                self._addItemToList(obj,idx)

    def onChooseTool(self, event):
        """ Respond to tool selection menu and tool palette selections
        """
        
        obj = event.GetEventObject()
        id2name = { id_SELECT: "select",
                    id_RECT: "rect"
                    }
        toolID = event.GetId()
        name = id2name.get( toolID )
        if name:
            self.setCurrentTool(name)

    def updChooseTool(self, event):
        """UI update event that keeps tool menu in sync with the PaletteIcons"""
        obj = event.GetEventObject()
        id2name = { id_SELECT: "select",
                    id_RECT: "rect"}
        toolID = event.GetId()
        event.Check( toolID == self.curToolIcon.GetId() )            

    # =======================
    # == Selection Methods ==
    # =======================

    def setCurrentTool(self, toolName):
        """ Set the currently selected tool.
        """
        
        toolIcon, tool = self.tools[toolName]
        if self.curToolIcon is not None:
            self.curToolIcon.SetValue(False)

        toolIcon.SetValue(True)
        self.curToolName = toolName
        self.curToolIcon = toolIcon
        self.curTool = tool
        self.drawPanel.SetCursor(tool.getDefaultCursor())


    def selectAll(self):
        """ Select every DrawingObject in our document.
        """
        self.selection = []
        for obj in self.contents:
            self.selection.append(obj)
        self.requestRedraw()
        #self._adjustMenus()


    def deselectAll(self):
        """ Deselect every DrawingObject in our document.
        """
        self.selection = []
        self.requestRedraw()
        #self._adjustMenus()


    def select(self, obj, add=False):
        """ Select the given DrawingObject within our document.

        If 'add' is True obj is added onto the current selection
        """
        if not add:
            self.selection = []
        if obj not in self.selection:
            self.selection += [obj]
            self.requestRedraw()
            #self._adjustMenus()

    def selectMany(self, objs):
        """ Select the given list of DrawingObjects.
        """
        self.selection = objs
        self.requestRedraw()
        #self._adjustMenus()


    def selectByRectangle(self, x, y, width, height):
        """ Select every DrawingObject in the given rectangular region.
        """
        self.selection = []
        for obj in self.contents:
            if obj.objectWithinRect(x, y, width, height):
                self.selection.append(obj)
        self.requestRedraw()
        #self._adjustMenus()

    def getObjectAndSelectionHandleAt(self, pt):
        """ Return the object and selection handle at the given point.

            We draw selection handles (small rectangles) around the currently
            selected object(s).  If the given point is within one of the
            selection handle rectangles, we return the associated object and a
            code indicating which selection handle the point is in.  If the
            point isn't within any selection handle at all, we return the tuple
            (None, None).
        """
        for obj in self.selection:
            handle = obj.getSelectionHandleContainingPoint(pt.x, pt.y)
            if handle is not None:
                return obj, handle

        return None, None


    def getObjectAt(self, pt):
        """ Return the first object found which is at the given point.
        """
        for obj in self.contents:
            if obj.objectContainsPoint(pt.x, pt.y):
                return obj
        return None

    # ===========================================
    # == Object selection through list Methods ==
    # ===========================================

    def OnItemSelected(self, evt):
        objects = self.contents
        #objects.reverse()
        
        for ii in range(len(objects)):
            obj = objects[ii]
            displayScale = self._getOutputScale()
            pos = obj.position
            x = (pos.x / self.scale)*displayScale[0]
            y = (pos.y / self.scale)*displayScale[1]
            if ii == evt.m_itemIndex:
                obj.setPenColour(wx.Colour(255,215,0))
                self.select(obj)
##                pos = obj.position
##                x = (pos.x / self.scale)*displayScale[0]
##                y = (pos.y / self.scale)*displayScale[1]
##                print(x,y)
            else:
                obj.setPenColour(wx.RED)
        self.requestRedraw()
        
    def OnItemDeselected(self, evt):
        objects = self.contents
        #objects.reverse()
        for ii in range(len(objects)):
            obj = objects[ii]
            obj.setPenColour(wx.RED)
        self.requestRedraw()

    def OnSelectAll(self,evt):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self,evt):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i,False)

    def OnChannelSelect(self,evt):
        eventid = evt.GetId()
        if eventid == self.ID_ALLCHANS:
            print("All chans")
        elif eventid == self.ID_SELECCHANS:
            print("Selected channels")

    def OnRectSelect(self,evt):
        SetRectBtnState(self.rectBtn.GetValue()) 

    # ==================================
    # == Image segmentation Methods ==
    # ==================================


    """
    Event Handler for "Segment" Button in "Image processing" Panel of GUI
    """
    def OnSegment(self,event):
        self.jobID += 1
        self.wipeOldData()

        # Disable Gui except for "Abort crop!" button in ""Regions of interest" panel
        self._switchControlState(False)
        self.abortCrop.Enable(False)

        # Get Values from "Fill" and "Erosion" and fill text fields in "Image Proccessing" panel of GUI
        self.fillsize = int(self.fill.GetValue())
        self.erosize = int(self.ero.GetValue())

        #Duplicate copy of "Erosion" for iteration purposes
        # From usage it should be the number of iterations the erosion occurs
        self.eroiter = int(self.ero.GetValue())

        #Signal Worker so that self.processImage (Worker Function) sends its data into self.autoCreatedObjects(Consumer Function)
        # wargs/ wkwargs is the sent data
        # In this case not used alot, just to check if jobIDs match
        delayedresult.startWorker(self.autoCreatedObjects, self.processImage,
                                  wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

    """
    Event Handler for "Abort" Button in "Image processing" Panel of GUI
    """
    def OnSegmentAbort(self,event):
        self.abortEvent.set()

    """
    Worker Function for onSegment Handler. Passes jobId and triggers self.autoCreatedObject() as a worker/consumer pair
    """
    def processImage(self,jobID,abortEvent):
        if self.mode == 'MetaCyte TL':
            inverted = self.wholeSlideData[:,:,0]
            inverted = np.subtract(255,inverted)
            bw = (inverted > 0) & (inverted > self.threshold)
        elif self.mode == 'MetaCyte FL':
            bw = (self.wholeSlideData[:,:,0] > 0) & (self.wholeSlideData[:,:,0] > self.threshold)                

        # Size of the structuring element in the morphological fill
        fillsize = [self.fillsize,self.fillsize]

        #Size of the structuring element for the morphological erosion
        erosize = [self.erosize,self.erosize]

        #Perform a binary fill followed by eroiter number of binary erosions
        bwfill = ndimage.binary_fill_holes(bw,structure=np.ones(fillsize))
        bwerode = ndimage.binary_erosion(bwfill,structure=np.ones(erosize),iterations=self.eroiter)


        labeled_type = np.dtype('uint8')

        # Get the geatures and count in the final (filled then eroded ndarray)
        imlabeled,num_features = ndimage.measurements.label(bwerode,output=labeled_type)
        sizes = ndimage.sum(bwerode, imlabeled, range(num_features+1))
        mask_size = sizes < 1000

        # get non-object pixels and set to zero
        remove_pixel = mask_size[imlabeled]
        imlabeled[remove_pixel] = 0
        labels = np.unique(imlabeled)

        # ndimage
        label_clean = np.searchsorted(labels, imlabeled)


        # Iterate through range and make array of 0, 1, ..., len(labels)
        lab = []    
        for i in range(len(labels) - 1):
            lab.append(i + 1)
        
        self.l = lab    
        objs = ndimage.measurements.find_objects(label_clean,max_label=len(labels))
        # If any objects have been found, return
        # return value will be array of tuple of 2 slice Objects
        # [(slice(0, 2, None), slice(0, 3, None)), (slice(2, 5, None), slice(2, 5, None))]
        # Analogous to label_clean[0:2, 0:3] for the first tuple
        if objs:
            output_objs = objs
        data = label_clean
        return output_objs     

    """
    Delayed function after its worker method: processImage()
    Gets the calculated object from the worker method (an Array of Slice object pairs) and configures the GUI
    and data models for them. 
    Updates the canvas, ROI Table in "Regions of interest" panel, and the back end data. 
    """
    def autoCreatedObjects(self,delayedResult):

        # Check whether the jobID is still valid
        # i.e something significant hasn't interjected itself between processImage() and autoCreatedObjects()
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID

        # attempt to assign the returned values from processImage(), else through Exception message box and return
        try:
            objects = delayedResult.get()
        except Exception as exc:
            dlg = wx.MessageDialog(self, "Result for job %s raised exception: %s" % (jobID, exc),
                               'Processing Error',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return


        # Output scaling down factor from "Output Scale" Dropdown from "Regions of interest" fold pane
        scalefact = int(self.scaleCombo.GetSelection())

        # Output Scaling factor (i.e. ratio between selected scale and image used in display GUI (reslevel = 5))
        outputScale = self._getOutputScale(scalefact)

        #scaling for display (using default resLevel = 0)
        displayScale = self._getOutputScale()
        self.roi_definition(objects,scalefact,outputScale,displayScale)
        #this loop populates the table
##        for idx in range(len(self.roiDisplayArray)):
##            roi = self.roiDisplayArray[idx]
##            xval = str(roi[2])
##            yval = str(roi[0])
##            wval = str(roi[3] - roi[2])
##            hval = str(roi[1] - roi[0])             
##            index = self.list.InsertStringItem(sys.maxint, xval)
##            self.list.SetStringItem(index, 1, yval)
##            self.list.SetStringItem(index, 2, wval)
##            self.list.SetStringItem(index, 3, hval)            
##            self.list.SetItemData(index, idx)

        #  iterate throw DrawingObjects (generally the RectDrawingObjects
        # Add each object to the table in "Regions of interest" of GUI
        for obj in self.contents:
            key = self.contents.index(obj)
            self._addItemToList(obj,key,scalefact)
            
        #enable the gui again and reset controls and display for next job    
        self._switchControlState()
        self.abortCrop.Enable(True)
        self.thresh.SetValue(0)
        self.threshold = 255

        # Configure Gui Display Image with current Channel Index and Colour weightings
        try:
            colour = flouroColors[self.curChannelName]
        except:
            colour = 'grey'        
        self.RetrieveImage(self.curChannelIdx,colour)

    """
    Creates and adds each of the objects into the canvas and ROI table
    """
    def roi_definition(self,objects,scalefact,outputScale,displayScale):

##        roiDisplayArray = []
        ## Ordered list of tuples for rectangles around each of the input objects
        ##  Tuple in form (columnStart,rowStart,width, height)
        sortedROIList = []
        roiOutputArray = []
        for idx in range(len(objects)-1):
           
            vec = objects[idx]
            rowvec = vec[0]
            colvec = vec[1]
            # these rois are in screen coordinates are used to create the rectangle drawing objects
            roiY = rowvec.indices(10000)
            roiX = colvec.indices(10000)

            rowstart = int(roiY[0])
            rowend = int(roiY[1])
            colstart = int(roiX[0])
            colend = int(roiX[1])
            H = float(roiY[1] - roiY[0])
            W = float(roiX[1] - roiX[0])

#            padX = 0.05*W
#            padY = 0.05*H
#
#            rowstart = rowstart - padY
#            rowend = rowend + padY
#            colstart = colstart - padX
#            colend = colend + padY

#            padW = int(colend - colstart)
#            padH = int(rowend - rowstart)
            
            if (rowstart < 0):
                rowstart = 0
            if (colstart < 0):
                colstart = 0

            #Account for rounding error in integers
            if (rowend > self.displayData.GetHeight()):
                rowend = self.displayData.GetHeight() - 1
            if (colend > self.displayData.GetWidth()):
                colend = self.displayData.GetWidth() - 1
                
#            roi = (colstart,rowstart,padW,padH)
            roi = (colstart,rowstart,W,H)
            sortedROIList.append(roi)
        
        for roi in sortedROIList:
            #create rectangle drawing objects for each roi update it to adjust for display scale and add to self.contents
            newObject = RectDrawingObject(penColour=self.penColour,
                                    fillColour=self.fillColour,
                                    lineSize=self.lineSize)
            #updates and adds the RectDrawingObject to the canvas
            self._updateObj(newObject,[roi[0],roi[1],roi[2],roi[3]])
            self.addObject(newObject)          
##
##            #these rois are scaled for the resolution level we want to export as
##            origX = round(roi[0] * outputScale[0])
##            origY = round(roi[1] * outputScale[1])
##            origW = round(roi[2] * outputScale[0])
##            origH = round(roi[3] * outputScale[1])            
##            rowstart = int(origY)
##            rowend = int(origY + origH)
##            colstart = int(origX)
##            colend = int(origX + origW)
##
##            if (rowstart < 0):
##                rowstart = 0
##            if (colstart < 0):
##                colstart = 0
##
##            if (rowend > self.sizeArray[scalefact][1]):
##                rowend = self.sizeArray[scalefact][1] - 1
##            if (colend > self.sizeArray[scalefact][0]):
##                colend = self.sizeArray[scalefact][0] - 1
####            disproi = (disprowstart, disprowend, dispcolstart, dispcolend)
####            roiDisplayArray.insert(0,disproi)       
##            roiOutputArray.insert(0,(rowstart, rowend, colstart, colend))
        #return roiOutputArray#, roiDisplayArray
     

    # ==================================
    # == Output data creation Methods ==
    # ==================================
    
    def OnCrop(self,event):
        self._switchControlState(False)
        self.procAbortButton.Enable(False)
        selection = []
        roiArray = []
        for index in range(self.list.GetItemCount()):
            if self.list.IsChecked(index):
                selection.append(index)
                itemArray = []
                for col in range(4):
                    item = self.list.GetItem(index,col)
                    itemArray.append(int(item.GetText()))
                roiArray.append(itemArray)
        if len(roiArray) > 1:
            dlg = wx.ProgressDialog("Writing tissue sections",
                            "Please wait",
                            maximum = len(selection)-1,
                            parent=self,
                            style = wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME)
            delayedresult.startWorker(self.finishedCrop, self.createOutput,wargs=[selection,roiArray,dlg])
        else:
            delayedresult.startWorker(self.finishedCrop, self.createOutput,wargs=[selection,roiArray])
##        #check the file sizes here
##        try:
##            thread = Thread(target=self.createOutput())
##            thread.start()
##            inpath = self.selected[0]
##            self.checkpath = os.path.dirname(inpath)
##            wx.CallAfter(self.check_file_size)
##        except MemoryError:
##            dial = wx.MessageDialog(None, "Error encountered: One or more of the tissue sections generated has "
##                    "used up the system memory. Try to reduce the file size "
##                    "by writing single channels or by down-scaling the image", 'Error', wx.OK | wx.ICON_ERROR)
##            dial.ShowModal()

    def OnAbortCrop(self,event):
        self.shouldAbort = True
        
    def createOutput(self,selection,roiArray,dlg=None):
        scalefact = int(self.scaleCombo.GetSelection())
        outChanChoice = (self.radio1.GetValue())
        compression = self.comprCombo.GetValue()
        if outChanChoice:
            outChan = range(self.numchannels)
        else:
            outChanString = self.chans.GetValue()
            if outChanString.find(',') == 1:
                Channels = map(int, outChanString.split(','))
                outChan = [x-1 for x in Channels]
            elif outChanString.find('-') == 1:
                Channels = map(int, outChanString.split('-'))
                outChan = range(Channels[0]-1,Channels[1])
            else:
                outChan = []
                outChan.append(int(self.chans.GetValue())-1)
                
        rotation = 0#int(self.rotationCombo.GetSelection()) 
        total = len(roiArray) - 1
        for idx in range(len(roiArray)):
            if len(roiArray) > 1:
                wx.CallAfter(dlg.Update,idx)
            print "Processing section number:  " + str(idx+1)
            
            roi = roiArray[idx]
            rowstart = roi[1]
            rowend = roi[1]+roi[3]
            colstart = roi[0]
            colend = roi[0]+roi[2]
            pixelregion = [rowstart,rowend,colstart,colend]
            #outputFileChoice = self.radio_btn_OME.GetValue()
            outputFileChoice = 1
            inpath = self.selectedFile[0]
            infname = inpath[0:-4]
            if (len(self.userDetails)==4) and (self.userDetails[0]==''):
                self.userDetails = []
                print(self.userDetails)
                
            if outputFileChoice:
                if (idx + 1) < 10:
                    if len(outChan) == 1:
                        chanstr = '0' + str(outChan[0]+1)
                        outfilename = infname + '_' + '00' + str(idx + 1) + '_chan' + chanstr + '.ome.tif'
                    else:
                        outfilename = infname + '_' + '00' + str(idx + 1) + '.ome.tif'
                elif (idx + 1) >= 10:
                    outfilename = infname + '_' + 'section_0' + str(idx + 1) + '.ome.tif'
                    
                OMETIFF(self.userDetails, self.infilename, outfilename, compression, str((idx+1)), total, self.ImarisInput, pixelregion,outChan,scalefact,rotation).process()
            else:
                if (idx + 1) < 10:
                    outfilenameImaris = infname + '_' + 'section_00' + str(idx + 1) + '.ims'
                elif (idx + 1) >= 10:
                    outfilenameImaris = infname + '_' + 'section_0' + str(idx + 1) + '.ims'                
                OUTPUTIMARIS(self.infilename, outfilenameImaris, self.ImarisInput, pixelregion).output()
        if len(roiArray) > 1:
            wx.CallAfter(dlg.Destroy)
#        imarray = None

    def finishedCrop(self,result):
        #try:
        r = result.get()
        self._switchControlState()
        self.procAbortButton.Enable(True)
##        except Exception, exc:
##            dlg = wx.MessageDialog(self, "Something went wrong while cropping sections",
##                               'Cropping Error',wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
    

    # =======================
    # == Private Methods ==
    # =======================

    def _initBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        if im:
            self.buffer = wx.EmptyBitmap(im.GetWidth(), im.GetHeight())
        else:
            size = self.drawPanel.GetClientSize()
            self.buffer = wx.EmptyBitmap(max(1,size.width),max(1,size.height))        
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.drawPanel.GetBackgroundColour()))
        dc.Clear()

        if self.displayData:
            self.display(dc)
        
        self.drawContents(dc)
        del dc  # commits all drawing to the buffer
        self._reInitBuffer = False
        #self.saved_offset = self.drawPanel.CalcUnscrolledPosition(0,0)

        


    def _setPenColour(self, colour):
        """ Set the default or selected object's pen colour.
        """
        if len(self.selection) > 0:
            self.saveUndoInfo()
            for obj in self.selection:
                obj.setPenColour(colour)
            self.requestRedraw()

        self.penColour = colour
        #self.optionIndicator.setPenColour(colour)


    def _setFillColour(self, colour):
        """ Set the default or selected object's fill colour.
        """
        if len(self.selection) > 0:
            self.saveUndoInfo()
            for obj in self.selection:
                obj.setFillColour(colour)
            self.requestRedraw()

        self.fillColour = colour
        #self.optionIndicator.setFillColour(colour)


    def _setLineSize(self, size):
        """ Set the default or selected object's line size.
        """
        if len(self.selection) > 0:
            self.saveUndoInfo()
            for obj in self.selection:
                obj.setLineSize(size)
            self.requestRedraw()

        self.lineSize = size
        #self.optionIndicator.setLineSize(size)

    def _buildStoredState(self):
        """ Remember the current state of the document, to allow for undo.

            We make a copy of the document's contents, so that we can return to
            the previous contents if the user does something and then wants to
            undo the operation.  

            Returns an object representing the current document state.
        """
        savedContents = []
        for obj in self.contents:
            savedContents.append([obj.__class__, obj.getData()])

        savedSelection = []
        for i in range(len(self.contents)):
            if self.contents[i] in self.selection:
                savedSelection.append(i)

        info = {"contents"  : savedContents,
                "selection" : savedSelection}

        return info
        
    def _restoreStoredState(self, savedState):
        """Restore the state of the document to a previous point for undo/redo.

        Takes a stored state object and recreates the document from it.
        Used by undo/redo implementation.
        """
        self.contents = []

        for draw_class, data in savedState["contents"]:
            obj = draw_class()
            obj.setData(data)
            self.contents.append(obj)

        self.selection = []
        for i in savedState["selection"]:
            self.selection.append(self.contents[i])

        self.dirty = True
        #self._adjustMenus()
        self.requestRedraw()

    def _resizeObject(self, obj, anchorPt, oldPt, newPt):
        """ Resize the given object.

            'anchorPt' is the unchanging corner of the object, while the
            opposite corner has been resized.  'oldPt' are the current
            coordinates for this corner, while 'newPt' are the new coordinates.
            The object should fit within the given dimensions, though if the
            new point is less than the anchor point the object will need to be
            moved as well as resized, to avoid giving it a negative size.
        """
        if isinstance(obj, TextDrawingObject):
            # Not allowed to resize text objects -- they're sized to fit text.
            wx.Bell()
            return

        self.saveUndoInfo()

        topLeft  = wx.Point(min(anchorPt.x, newPt.x),
                           min(anchorPt.y, newPt.y))
        botRight = wx.Point(max(anchorPt.x, newPt.x),
                           max(anchorPt.y, newPt.y))

        newWidth  = botRight.x - topLeft.x
        newHeight = botRight.y - topLeft.y

        if isinstance(obj, LineDrawingObject):
            # Adjust the line so that its start and end points match the new
            # overall object size.

            startPt = obj.getStartPt()
            endPt   = obj.getEndPt()

            slopesDown = ((startPt.x < endPt.x) and (startPt.y < endPt.y)) or \
                         ((startPt.x > endPt.x) and (startPt.y > endPt.y))

            # Handle the user flipping the line.

            hFlip = ((anchorPt.x < oldPt.x) and (anchorPt.x > newPt.x)) or \
                    ((anchorPt.x > oldPt.x) and (anchorPt.x < newPt.x))
            vFlip = ((anchorPt.y < oldPt.y) and (anchorPt.y > newPt.y)) or \
                    ((anchorPt.y > oldPt.y) and (anchorPt.y < newPt.y))

            if (hFlip and not vFlip) or (vFlip and not hFlip):
                slopesDown = not slopesDown # Line flipped.

            if slopesDown:
                obj.setStartPt(wx.Point(0, 0))
                obj.setEndPt(wx.Point(newWidth, newHeight))
            else:
                obj.setStartPt(wx.Point(0, newHeight))
                obj.setEndPt(wx.Point(newWidth, 0))

        # Finally, adjust the bounds of the object to match the new dimensions.

        obj.setPosition(topLeft)
        obj.setSize(wx.Size(botRight.x - topLeft.x, botRight.y - topLeft.y))

        self.requestRedraw()


    def _moveObject(self, offsetX, offsetY):
        """ Move the currently selected object(s) by the given offset.
        """
        self.saveUndoInfo()

        for obj in self.selection:
            pos = obj.getPosition()
            pos.x = pos.x + offsetX
            pos.y = pos.y + offsetY
            obj.setPosition(pos)

        self.requestRedraw()


    def _buildLineSizePopup(self, lineSize):
        """ Build the pop-up menu used to set the line size.

            'lineSize' is the current line size value.  The corresponding item
            is checked in the pop-up menu.
        """
        menu = wx.Menu()
        menu.Append(id_LINESIZE_0, "no line",      kind=wx.ITEM_CHECK)
        menu.Append(id_LINESIZE_1, "1-pixel line", kind=wx.ITEM_CHECK)
        menu.Append(id_LINESIZE_2, "2-pixel line", kind=wx.ITEM_CHECK)
        menu.Append(id_LINESIZE_3, "3-pixel line", kind=wx.ITEM_CHECK)
        menu.Append(id_LINESIZE_4, "4-pixel line", kind=wx.ITEM_CHECK)
        menu.Append(id_LINESIZE_5, "5-pixel line", kind=wx.ITEM_CHECK)

        if   lineSize == 0: menu.Check(id_LINESIZE_0, True)
        elif lineSize == 1: menu.Check(id_LINESIZE_1, True)
        elif lineSize == 2: menu.Check(id_LINESIZE_2, True)
        elif lineSize == 3: menu.Check(id_LINESIZE_3, True)
        elif lineSize == 4: menu.Check(id_LINESIZE_4, True)
        elif lineSize == 5: menu.Check(id_LINESIZE_5, True)

        self.Bind(wx.EVT_MENU, self._lineSizePopupSelected, id=id_LINESIZE_0, id2=id_LINESIZE_5)

        return menu


    def _lineSizePopupSelected(self, event):
        """ Respond to the user selecting an item from the line size popup menu
        """
        id = event.GetId()
        if   id == id_LINESIZE_0: self._setLineSize(0)
        elif id == id_LINESIZE_1: self._setLineSize(1)
        elif id == id_LINESIZE_2: self._setLineSize(2)
        elif id == id_LINESIZE_3: self._setLineSize(3)
        elif id == id_LINESIZE_4: self._setLineSize(4)
        elif id == id_LINESIZE_5: self._setLineSize(5)
        else:
            wx.Bell()
            return

        self.optionIndicator.setLineSize(self.lineSize)


    def _getEventCoordinates(self, event):
        """ Return the coordinates associated with the given mouse event.

            The coordinates have to be adjusted to allow for the current scroll
            position.
        """
##        originX, originY = self.drawPanel.GetViewStart()
        originX = originY = 0
##        unitX, unitY = self.drawPanel.GetScrollPixelsPerUnit()
        unitX = unitY = 1
        return wx.Point(event.GetX() + (originX * unitX),
                       event.GetY() + (originY * unitY))


    def _drawObjectOutline(self, offsetX, offsetY):
        """ Draw an outline of the currently selected object.

            The selected object's outline is drawn at the object's position
            plus the given offset.

            Note that the outline is drawn by *inverting* the window's
            contents, so calling _drawObjectOutline twice in succession will
            restore the window's contents back to what they were previously.
        """
        if len(self.selection) != 1: return

        position = self.selection[0].getPosition()
        size     = self.selection[0].getSize()

        dc = wx.ClientDC(self.drawPanel)
        self.drawPanel.PrepareDC(dc)
        dc.BeginDrawing()
        dc.SetPen(wx.BLACK_DASHED_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetLogicalFunction(wx.INVERT)

        dc.DrawRectangle(position.x + offsetX, position.y + offsetY,
                         size.width, size.height)

        dc.EndDrawing()

    """
    Add obj to Table in "Regions of interest" pane of gui
    """
    def _addItemToList(self, obj, key, scalefact=0):
        data = []
        displayScale = self.scale
        slideScale = self._getOutputScale(scalefact)

        #get obj data in order specified in ROI table
        data[0:1] = obj.position
        data[2:3] = obj.size

        # Convert pixel coordinates and lengths relative to display image
        data[0] = int((data[0] / displayScale)*slideScale[0])
        data[1] = int((data[1] / displayScale)*slideScale[1])
        data[2] = int((data[2] / displayScale)*slideScale[0])
        data[3] = int((data[3] / displayScale)*slideScale[1])

        # Get final index to insert row
        index = self.list.InsertStringItem(sys.maxint, str(data[0]))

        # insert above obj data into row at index
        self.list.SetStringItem(index, 1, str(data[1]))
        self.list.SetStringItem(index, 2, str(data[2]))
        self.list.SetStringItem(index, 3, str(data[3]))            
        self.list.SetItemData(index, key)

    """
    Return a tuple of two ratios, (Xratio, Yratio) where both ratios are from scaleFact's resLevel /resLevel. 
    Xratio, Yratio imply outputScale is greater than resLevel5
    """
    def _getOutputScale(self,scalefact=0):
        loRes = self.sizeArray[5]
        loResX = loRes[0]
        loResY = loRes[1]
        hiRes = self.sizeArray[scalefact]
        hiResX = hiRes[0]
        hiResY = hiRes[1]
        outputScale = [(hiResX / loResX),(hiResY / loResY)]
        return outputScale


    """
    Given a DrawingObject (usually a RectDrawingObject), method results in that obj being placed
     at the position and size specified in ROI 
     ROI format is (x,y, width, height) where Point(x,y) is the top left vertex. 
    """
    def _updateObj(self,obj,ROI):
        x = ROI[0]*self.scale
        y = ROI[1]*self.scale
        width = ROI[2]*self.scale
        height = ROI[3]*self.scale

        obj.setPosition(wx.Point(x,y))
        obj.setSize(wx.Size(width,height))        

    """
    Switch the Control state of the Gui where state is a boolean of whether the GUI should be enabled. 
    """
    def _switchControlState(self,state=True):
        self.fbb.Enable(state)
        self.fbText.Enable(state)
        #self.autoSegText.Enable(state)
        self.thresh.Enable(state)
        self.threshText.Enable(state)
        self.iter.Enable(state)
        self.iterText.Enable(state)
        self.ero.Enable(state)
        self.eroText.Enable(state)
        self.fill.Enable(state)
        self.fillText.Enable(state)
        self.procButton.Enable(state)
        #self.manSegText.Enable(state)
        for toolName in self.tools.iterkeys():
            toolIcon, tool = self.tools[toolName]
            if toolName == self.curToolName:
                toolIcon.SetValue(state)
            toolIcon.Enable(state)
        self.list.Enable(state)
        self.selectAll.Enable(state)
        self.deSelectAll.Enable(state)
        self.radio1.Enable(state)
        self.radio2.Enable(state)
        self.chans.Enable(state)
        self.chansText.Enable(state)
        self.scaleCombo.Enable(state)
        self.scaleText.Enable(state)
        #self.rotationCombo.Enable(state)
        #self.rotText.Enable(state)
        self.crop.Enable(state)
        self.cb.Enable(state)
        self.bcb.Enable(state)
        
class ToolPaletteToggle(GenBitmapToggleButton):
    """ An icon appearing in the tool palette area of our sketching window.

        Note that this is actually implemented as a wx.Bitmap rather
        than as a wx.Icon.  wx.Icon has a very specific meaning, and isn't
        appropriate for this more general use.
    """

    def __init__(self, parent, iconID, iconName, toolTip, mode = wx.ITEM_NORMAL):
        """ Standard constructor.

            'parent'   is the parent window this icon will be part of.
            'iconID'   is the internal ID used for this icon.
            'iconName' is the name used for this icon.
            'toolTip'  is the tool tip text to show for this icon.
            'mode'     is one of wx.ITEM_NORMAL, wx.ITEM_CHECK, wx.ITEM_RADIO

            The icon name is used to get the appropriate bitmap for this icon.
        """
        iconImage = toolIconImages[iconName + "Icon"]
        iconSelImage = toolIconImages[iconName + "IconSel"]
        #bmp = wx.Bitmap(iconImage.GetBitmap(), wx.BITMAP_TYPE_BMP)
        bmp = iconImage.GetBitmap()
        #bmpsel = wx.Bitmap(iconSelImage.GetBitmap(), wx.BITMAP_TYPE_BMP)
        bmpsel = iconSelImage.GetBitmap()
        GenBitmapToggleButton.__init__(self, parent, iconID, bitmap=bmp, 
                                       size=(bmp.GetWidth(), bmp.GetHeight()),
                                       style=wx.BORDER_NONE)

        self.SetToolTip(wx.ToolTip(toolTip))
        self.SetBitmapLabel(bmp)
        self.SetBitmapSelected(bmpsel)

        self.iconID     = iconID
        self.iconName   = iconName

#============================================================================
class DrawingTool(object):
    """Base class for drawing tools"""

    def __init__(self):
        pass

    def getDefaultCursor(self):
        """Return the cursor to use by default which this drawing tool is selected"""
        return wx.STANDARD_CURSOR

    def draw(self,dc):
        pass


    def onMouseEvent(self,parent, event):
        """Mouse events passed in from the parent.

        Returns True if the event is handled by the tool,
        False if the canvas can try to use it.
        """
        event.Skip()
        return False

#----------------------------------------------------------------------------
class SelectDrawingTool(DrawingTool):
    """Represents the tool for selecting things"""

    def __init__(self):
        self.curHandle = None
        self.curObject = None
        self.objModified = False
        self.startPt = None
        self.curPt = None

    def getDefaultCursor(self):
        """Return the cursor to use by default which this drawing tool is selected"""
        return wx.STANDARD_CURSOR

    def draw(self, dc):
        if self._doingRectSelection():
            dc.SetPen(wx.BLACK_DASHED_PEN)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            x = [self.startPt.x, self.curPt.x]; x.sort()
            y = [self.startPt.y, self.curPt.y]; y.sort()
            dc.DrawRectangle(x[0],y[0], x[1]-x[0],y[1]-y[0])


    def onMouseEvent(self,parent, event):
        handlers = { wx.EVT_LEFT_DOWN.evtType[0]:   self.onMouseLeftDown,
                     wx.EVT_MOTION.evtType[0]:      self.onMouseMotion,
                     wx.EVT_LEFT_UP.evtType[0]:     self.onMouseLeftUp,
                     wx.EVT_LEFT_DCLICK.evtType[0]: self.onMouseLeftDClick }
        handler = handlers.get(event.GetEventType())
        if handler is not None:
            return handler(parent,event)
        else:
            event.Skip()
            return False

    def onMouseLeftDown(self,parent,event):
        mousePt = wx.Point(event.X,event.Y)
        obj, handle = parent.getObjectAndSelectionHandleAt(mousePt)
        self.startPt = mousePt
        self.curPt = mousePt
        if obj is not None and handle is not None:
            self.curObject = obj
            self.curHandle = handle
        else:
            self.curObject = None
            self.curHandle = None
        
        obj = parent.getObjectAt(mousePt)
        if self.curObject is None and obj is not None:
            self.curObject = obj
            self.dragDelta = obj.position-mousePt
            self.curHandle = None
            parent.select(obj, event.ShiftDown())
            
        return True

    def onMouseMotion(self,parent,event):
        if not event.LeftIsDown(): return

        self.curPt = wx.Point(event.X,event.Y)

        obj,handle = self.curObject,self.curHandle
        if self._doingDragHandle():
            self._prepareToModify(parent)
            obj.moveHandle(handle,event.X,event.Y)
            parent.requestRedraw()

        elif self._doingDragObject():
            self._prepareToModify(parent)
            obj.position = self.curPt + self.dragDelta
            #magic numbers to prevent drawing outside image area
            limits = imScaled.GetSize()
            if (obj.position[0] < 1):
                obj.position[0] = 1
            if (obj.position[1] < 1):    
                obj.position[1] = 1            
            if obj.position[0] > limits[0]-obj.size[0]:
                obj.position[0] = limits[0] - obj.size[0]
            if obj.position[1] > limits[1]-obj.size[1]:
                obj.position[1] = limits[1] - obj.size[1]                
            parent.requestRedraw()

        elif self._doingRectSelection():
            parent.requestRedraw()

        return True

    def onMouseLeftUp(self,parent,event):

        obj,handle = self.curObject,self.curHandle
        if self._doingDragHandle():
            obj.moveHandle(handle,event.X,event.Y)
            obj.finalizeHandle(handle,event.X,event.Y)

        elif self._doingDragObject():
            curPt = wx.Point(event.X,event.Y)
            obj.position = curPt + self.dragDelta
            #magic numbers to prevent drawing outside image area
            limits = imScaled.GetSize()
            if (obj.position[0] < 1):
                obj.position[0] = 1
            if (obj.position[1] < 1):    
                obj.position[1] = 1 
            if obj.position[0] > limits[0]-obj.size[0]:
                obj.position[0] = limits[0] - obj.size[0]
            if obj.position[1] > limits[1]-obj.size[1]:
                obj.position[1] = limits[1] - obj.size[1]
        elif self._doingRectSelection():
            x = [event.X, self.startPt.x]
            y = [event.Y, self.startPt.y]
            x.sort()
            y.sort()
            parent.selectByRectangle(x[0],y[0],x[1]-x[0],y[1]-y[0])
            

        self.curObject = None
        self.curHandle = None
        self.curPt = None
        self.startPt = None
        self.objModified = False
        parent.requestRedraw()

        return True

    def onMouseLeftDClick(self,parent,event):
        event.Skip()
        mousePt = wx.Point(event.X,event.Y)
        obj = parent.getObjectAt(mousePt)
        if obj and obj.hasPropertyEditor():
            if obj.doPropertyEdit(parent):
                parent.requestRedraw()
                return True

        return False

    
    def _prepareToModify(self,parent):
        if not self.objModified:
            #parent.saveUndoInfo()
            self.objModified = True
        
    def _doingRectSelection(self):
        return self.curObject is None \
               and self.startPt is not None \
               and self.curPt is not None

    def _doingDragObject(self):
        return self.curObject is not None and self.curHandle is None

    def _doingDragHandle(self):
        return self.curObject is not None and self.curHandle is not None
    
#----------------------------------------------------------------------------
class RectDrawingTool(DrawingTool):
    """Represents the tool for drawing rectangles"""

    def __init__(self):
        self.newObject = None

    def getDefaultCursor(self):
        """Return the cursor to use by default which this drawing tool is selected"""
##        cursor = wx.Cursor('cross_cursor.cur',wx.BITMAP_TYPE_CUR)
##        return cursor
        image = cross_cursor.GetImage()

        # since this image didn't come from a .cur file, tell it where the hotspot is
        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 12)
        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 12)

        # make the image into a cursor
        return wx.CursorFromImage(image)
        #return wx.CROSS_CURSOR

    def draw(self, dc):
        if self.newObject is None: return
        self.newObject.draw(dc,True)


    def onMouseEvent(self,parent, event):
        handlers = { wx.EVT_LEFT_DOWN.evtType[0]: self.onMouseLeftDown,
                     wx.EVT_MOTION.evtType[0]:    self.onMouseMotion,
                     wx.EVT_LEFT_UP.evtType[0]:   self.onMouseLeftUp }
        handler = handlers.get(event.GetEventType())
        if handler is not None:
            return handler(parent,event)
        else:
            event.Skip()
            return False

    def onMouseLeftDown(self,parent, event):
        self.startPt = wx.Point(event.GetX(), event.GetY())
        self.newObject = None
        event.Skip()
        return True

    def onMouseMotion(self,parent, event):
        if not event.Dragging(): return

        if self.newObject is None:
            obj = RectDrawingObject(penColour=parent.penColour,
                                    fillColour=parent.fillColour,
                                    lineSize=parent.lineSize)
            self.newObject = obj

        self._updateObjFromEvent(self.newObject, event)

        parent.requestRedraw()
        event.Skip()
        return True

    def onMouseLeftUp(self,parent, event):

        if self.newObject is None:
            return

        self._updateObjFromEvent(self.newObject,event)

        parent.addObject(self.newObject)

        self.newObject = None

        event.Skip()
        return True


    def _updateObjFromEvent(self,obj,event):
        x = [event.X, self.startPt.x]
        y = [event.Y, self.startPt.y]
        x.sort()
        y.sort()
        width = x[1]-x[0]
        height = y[1]-y[0]
        obj.setPosition(wx.Point(x[0],y[0]))
        obj.setSize(wx.Size(width,height))

#============================================================================
class DrawingObject(object):
    """ Base class for objects within the drawing panel.

        A pySketch document consists of a front-to-back ordered list of
        DrawingObjects.  Each DrawingObject has the following properties:

            'position'      The position of the object within the document.
            'size'          The size of the object within the document.
            'penColour'     The colour to use for drawing the object's outline.
            'fillColour'    Colour to use for drawing object's interior.
            'lineSize'      Line width (in pixels) to use for object's outline.
            """

    # ==================
    # == Constructors ==
    # ==================

    def __init__(self, position=wx.Point(0, 0), size=wx.Size(0, 0),
                 penColour=wx.BLACK, fillColour=wx.WHITE, lineSize=1,
                 ):
        """ Standard constructor.

            The remaining parameters let you set various options for the newly
            created DrawingObject.
        """
        # One must take great care with constructed default arguments
        # like wx.Point(0,0) above.  *EVERY* caller that uses the
        # default will get the same instance.  Thus, below we make a
        # deep copy of those arguments with object defaults.

        self.position          = wx.Point(position.x,position.y)
        self.size              = wx.Size(size.x,size.y)
        self.penColour         = penColour
        self.fillColour        = fillColour
        self.lineSize          = lineSize

    # =============================
    # == Object Property Methods ==
    # =============================

    def getData(self):
        """ Return a copy of the object's internal data.

            This is used to save this DrawingObject to disk.
        """
        return [self.position.x, self.position.y,
                self.size.width, self.size.height,
                self.penColour.Red(),
                self.penColour.Green(),
                self.penColour.Blue(),
                self.fillColour.Red(),
                self.fillColour.Green(),
                self.fillColour.Blue(),
                self.lineSize]


    def setData(self, data):
        """ Set the object's internal data.

            'data' is a copy of the object's saved data, as returned by
            getData() above.  This is used to restore a previously saved
            DrawingObject.

            Returns an iterator to any remaining data not consumed by 
            this base class method.
        """
        #data = copy.deepcopy(data) # Needed?

        d = iter(data)
        try:
            self.position          = wx.Point(d.next(), d.next())
            self.size              = wx.Size(d.next(), d.next())
            self.penColour         = wx.Colour(red=d.next(),
                                              green=d.next(),
                                              blue=d.next())
            self.fillColour        = wx.Colour(red=d.next(),
                                              green=d.next(),
                                              blue=d.next())
            self.lineSize          = d.next()
        except StopIteration:
            raise ValueError('Not enough data in setData call')

        return d


    def hasPropertyEditor(self):
        return False

    def doPropertyEdit(self, parent):
        assert False, "Must be overridden if hasPropertyEditor returns True"

    def setPosition(self, position):
        """ Set the origin (top-left corner) for this DrawingObject.
        """
        self.position = position


    def getPosition(self):
        """ Return this DrawingObject's position.
        """
        return self.position


    def setSize(self, size):
        """ Set the size for this DrawingObject.
        """
        self.size = size


    def getSize(self):
        """ Return this DrawingObject's size.
        """
        return self.size


    def setPenColour(self, colour):
        """ Set the pen colour used for this DrawingObject.
        """
        self.penColour = colour


    def getPenColour(self):
        """ Return this DrawingObject's pen colour.
        """
        return self.penColour


    def setFillColour(self, colour):
        """ Set the fill colour used for this DrawingObject.
        """
        self.fillColour = colour


    def getFillColour(self):
        """ Return this DrawingObject's fill colour.
        """
        return self.fillColour


    def setLineSize(self, lineSize):
        """ Set the linesize used for this DrawingObject.
        """
        self.lineSize = lineSize


    def getLineSize(self):
        """ Return this DrawingObject's line size.
        """
        return self.lineSize


    # ============================
    # == Object Drawing Methods ==
    # ============================

    def draw(self, dc, selected):
        """ Draw this DrawingObject into our window.

            'dc' is the device context to use for drawing.  

            If 'selected' is True, the object is currently selected.
            Drawing objects can use this to change the way selected objects
            are drawn, however the actual drawing of selection handles
            should be done in the 'drawHandles' method
        """
        if self.lineSize == 0:
            dc.SetPen(wx.Pen(self.penColour, self.lineSize, wx.TRANSPARENT))
        else:
            dc.SetPen(wx.Pen(self.penColour, self.lineSize, wx.SOLID))

        if self.fillColour == None:
            dc.SetBrush(wx.Brush(self.penColour, wx.TRANSPARENT))
        else:
            dc.SetBrush(wx.Brush(self.fillColour, wx.SOLID))

        self._privateDraw(dc, self.position, selected)


    def drawHandles(self, dc):
        """Draw selection handles for this DrawingObject"""

        # Default is to draw selection handles at all four corners.
        dc.SetPen(wx.Pen(self.penColour))
        dc.SetBrush(wx.Brush(self.penColour))
        
        x,y = self.position
        self._drawSelHandle(dc, x, y)
        self._drawSelHandle(dc, x + self.size.width, y)
        self._drawSelHandle(dc, x, y + self.size.height)
        self._drawSelHandle(dc, x + self.size.width, y + self.size.height)


    # =======================
    # == Selection Methods ==
    # =======================

    def objectContainsPoint(self, x, y):
        """ Returns True iff this object contains the given point.

            This is used to determine if the user clicked on the object.
        """
        # Firstly, ignore any points outside of the object's bounds.
        if x < self.position.x: return False
        if x > self.position.x + self.size.x: return False
        if y < self.position.y: return False
        if y > self.position.y + self.size.y: return False

        # Now things get tricky.  There's no straightforward way of
        # knowing whether the point is within an arbitrary object's
        # bounds...to get around this, we draw the object into a
        # memory-based bitmap and see if the given point was drawn.
        # This could no doubt be done more efficiently by some tricky
        # maths, but this approach works and is simple enough.

        # Subclasses can implement smarter faster versions of this.

        bitmap = wx.EmptyBitmap(self.size.x + 10, self.size.y + 10)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        dc.BeginDrawing()
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, self.lineSize + 5, wx.SOLID))
        dc.SetBrush(wx.BLACK_BRUSH)
        self._privateDraw(dc, wx.Point(5, 5), True)
        dc.EndDrawing()
        pixel = dc.GetPixel(x - self.position.x + 5, y - self.position.y + 5)
        if (pixel.Red() == 0) and (pixel.Green() == 0) and (pixel.Blue() == 0):
            return True
        else:
            return False

    handle_TOP    = 0
    handle_BOTTOM = 1
    handle_LEFT   = 0
    handle_RIGHT  = 1

    def getSelectionHandleContainingPoint(self, x, y):
        """ Return the selection handle containing the given point, if any.

            We return one of the predefined selection handle ID codes.
        """
        # Default implementation assumes selection handles at all four bbox corners.
        # Return a list so we can modify the contents later in moveHandle()
        if self._pointInSelRect(x, y, self.position.x, self.position.y):
            return [self.handle_TOP, self.handle_LEFT]
        elif self._pointInSelRect(x, y, self.position.x + self.size.width,
                                        self.position.y):
            return [self.handle_TOP, self.handle_RIGHT]
        elif self._pointInSelRect(x, y, self.position.x,
                                        self.position.y + self.size.height):
            return [self.handle_BOTTOM, self.handle_LEFT]
        elif self._pointInSelRect(x, y, self.position.x + self.size.width,
                                        self.position.y + self.size.height):
            return [self.handle_BOTTOM, self.handle_RIGHT]
        else:
            return None

    def moveHandle(self, handle, x, y):
        """ Move the specified selection handle to given canvas location.
        """
        assert handle is not None

        # Default implementation assumes selection handles at all four bbox corners.
        pt = wx.Point(x,y)
        x,y = self.position
        w,h = self.size
        if handle[0] == self.handle_TOP:
            if handle[1] == self.handle_LEFT:
                dpos = pt - self.position
                self.position = pt
                self.size.width -= dpos.x
                self.size.height -= dpos.y
            else:
                dx = pt.x - ( x + w )
                dy = pt.y - ( y )
                self.position.y = pt.y
                self.size.width += dx
                self.size.height -= dy
        else: # BOTTOM
            if handle[1] == self.handle_LEFT:
                dx = pt.x - ( x )
                dy = pt.y - ( y + h )
                self.position.x = pt.x
                self.size.width -= dx
                self.size.height += dy
            else: 
                dpos = pt - self.position
                dpos.x -= w
                dpos.y -= h
                self.size.width += dpos.x
                self.size.height += dpos.y


        # Finally, normalize so no negative widths or heights.
        # And update the handle variable accordingly.
        if self.size.height<0:
            self.position.y += self.size.height
            self.size.height = -self.size.height
            handle[0] = 1-handle[0]

        if self.size.width<0:
            self.position.x += self.size.width
            self.size.width = -self.size.width
            handle[1] = 1-handle[1]
            


    def finalizeHandle(self, handle, x, y):
        pass


    def objectWithinRect(self, x, y, width, height):
        """ Return True iff this object falls completely within the given rect.
        """
        if x          > self.position.x:                    return False
        if x + width  < self.position.x + self.size.width:  return False
        if y          > self.position.y:                    return False
        if y + height < self.position.y + self.size.height: return False
        return True

    # =====================
    # == Private Methods ==
    # =====================

    def _privateDraw(self, dc, position, selected):
        """ Private routine to draw this DrawingObject.

            'dc' is the device context to use for drawing, while 'position' is
            the position in which to draw the object.
        """
        pass

    def _drawSelHandle(self, dc, x, y):
        """ Draw a selection handle around this DrawingObject.

            'dc' is the device context to draw the selection handle within,
            while 'x' and 'y' are the coordinates to use for the centre of the
            selection handle.
        """
        dc.DrawRectangle(x - 3, y - 3, 6, 6)


    def _pointInSelRect(self, x, y, rX, rY):
        """ Return True iff (x, y) is within the selection handle at (rX, ry).
        """
        if   x < rX - 3: return False
        elif x > rX + 3: return False
        elif y < rY - 3: return False
        elif y > rY + 3: return False
        else:            return True      

#----------------------------------------------------------------------------
class RectDrawingObject(DrawingObject):
    """ DrawingObject subclass that represents an axis-aligned rectangle.
    """
    def __init__(self, *varg, **kwarg):
        DrawingObject.__init__(self, *varg, **kwarg)

    def objectContainsPoint(self, x, y):
        """ Returns True iff this object contains the given point.

            This is used to determine if the user clicked on the object.
        """
        # Firstly, ignore any points outside of the object's bounds.

        if x < self.position.x: return False
        if x > self.position.x + self.size.x: return False
        if y < self.position.y: return False
        if y > self.position.y + self.size.y: return False

        # Rectangles are easy -- they're always selected if the
        # point is within their bounds.
        return True

    # =====================
    # == Private Methods ==
    # =====================

    def _privateDraw(self, dc, position, selected):
        """ Private routine to draw this DrawingObject.

            'dc' is the device context to use for drawing, while 'position' is
            the position in which to draw the object.  If 'selected' is True,
            the object is drawn with selection handles.  This private drawing
            routine assumes that the pen and brush have already been set by the
            caller.
        """
        dc.DrawRectangle(position.x, position.y,
                         self.size.width, self.size.height)        

#----------------------------------------------------------------------------

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, size=(-1,250), style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        self.listData = {}
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

##    # this is called by the base class when an item is checked/unchecked
##    def OnCheckItem(self, index, flag):
##        data = self.GetItemData(index)
##        title = self.listData[data][1]
##        if flag:
##            what = "checked"
##        else:
##            what = "unchecked"
##        print('item "%s", at index %d was %s\n' % (title, index, what))

class HtmlHelpFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(500,600))
        self.SetIcon(slidecrop.GetIcon())
        self.html = wx.html.HtmlWindow(self)
        if "gtk2" in wx.PlatformInfo:
            self.html.SetStandardFonts()
        wx.CallAfter(
            self.html.LoadPage, "help.html")

    def setContent(self,message):
        self.html.SetPage(message)

class SettingsDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):

        wx.Dialog.__init__(self,parent, ID, title, pos, size, style)
        self.SetIcon(slidecrop.GetIcon())
        
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Username:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.userName = wx.TextCtrl(self, -1, "", size=(100,-1))
        box.Add(self.userName, 1, wx.ALIGN_CENTRE|wx.LEFT|wx.TOP|wx.BOTTOM, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Group:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.group = wx.TextCtrl(self, -1, "", size=(100,-1))
        box.Add(self.group, 1, wx.ALIGN_CENTRE|wx.LEFT, 25)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "First name:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.firstName = wx.TextCtrl(self, -1, "", size=(100,-1))
        box.Add(self.firstName, 1, wx.ALIGN_CENTRE|wx.LEFT|wx.TOP|wx.BOTTOM, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Last name:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.lastName = wx.TextCtrl(self, -1, "", size=(100,-1))
        box.Add(self.lastName, 1, wx.ALIGN_CENTRE|wx.LEFT|wx.TOP|wx.BOTTOM, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)        

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def setUserDetails(self,details):
        if details:
            self.userName.SetValue(details[0])
            self.group.SetValue(details[1])
            self.firstName.SetValue(details[2])
            self.lastName.SetValue(details[3])       

    def getUserDetails(self):
        userName = self.userName.GetValue()
        group = self.group.GetValue()
        firstName = self.firstName.GetValue()
        lastName = self.lastName.GetValue()
        return [userName,group,firstName,lastName]

#----------------------------------------------------------------------------

class ExceptionHandler:
    """ A simple error-handling class to write exceptions to a text file.

        Under MS Windows, the standard DOS console window doesn't scroll and
        closes as soon as the application exits, making it hard to find and
        view Python exceptions.  This utility class allows you to handle Python
        exceptions in a more friendly manner.
    """

    def __init__(self):
        """ Standard constructor.
        """
        self._buff = ""
        if os.path.exists("errors.txt"):
            os.remove("errors.txt") # Delete previous error log, if any.


    def write(self, s):
        """ Write the given error message to a text file.

            Note that if the error message doesn't end in a carriage return, we
            have to buffer up the inputs until a carriage return is received.
        """
        if (s[-1] != "\n") and (s[-1] != "\r"):
            self._buff = self._buff + s
            return

        try:
            s = self._buff + s
            self._buff = ""

            f = open("errors.txt", "a")
            f.write(s)
            f.close()

            if s[:9] == "Traceback":
                # Tell the user than an exception occurred.
                wx.MessageBox("An internal error has occurred.\nPlease " + \
                             "refer to the 'errors.txt' file for details.",
                             "Error", wx.OK | wx.CENTRE | wx.ICON_EXCLAMATION)


        except:
            pass # Don't recursively crash on errors.

#----------------------------------------------------------------------------         
class MyApp(wx.App):

    def OnInit(self):
        frame = SlideCrop(None,title="SlideCrop")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True   

#---------------------------------------------------------------------------


def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win


#---------------------------------------------------------------------------


def main():
    app = MyApp(0)
    app.MainLoop()


if __name__ == "__main__":
    main()
