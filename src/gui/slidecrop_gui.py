# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Slide Crop Application v2", pos = wx.DefaultPosition, size = wx.Size( 786,795 ), style = wx.CLOSE_BOX|wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menuFile = wx.Menu()
		self.m_menubar1.Append( self.m_menuFile, u"File" ) 
		
		self.m_menuHelp = wx.Menu()
		self.m_menubar1.Append( self.m_menuHelp, u"Help" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		
		self.m_scrolledWindow1 = wx.ScrolledWindow( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText2 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Import Slide", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		bSizer2.Add( self.m_staticText2, 0, wx.ALL, 5 )
		
		self.m_filePicker1 = wx.FilePickerCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST )
		bSizer2.Add( self.m_filePicker1, 0, wx.ALL, 5 )
		
		
		self.m_scrolledWindow1.SetSizer( bSizer2 )
		self.m_scrolledWindow1.Layout()
		bSizer2.Fit( self.m_scrolledWindow1 )
		self.m_scrolledWindow2 = wx.ScrolledWindow( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow2.SetScrollRate( 5, 5 )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_bitmap1 = wx.StaticBitmap( self.m_scrolledWindow2, wx.ID_ANY, wx.Bitmap( u"./loadimage.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_bitmap1, 0, wx.ALL, 5 )
		
		
		self.m_scrolledWindow2.SetSizer( bSizer3 )
		self.m_scrolledWindow2.Layout()
		bSizer3.Fit( self.m_scrolledWindow2 )
		self.m_splitter1.SplitVertically( self.m_scrolledWindow1, self.m_scrolledWindow2, 0 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 1, 0, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 0 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	

