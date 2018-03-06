# -*- coding: utf-8 -*-
# from version_two.src.SlideCrop.SlideCropperAPI import SlideCropperAPI
###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1(wx.Frame):
    def __init__(self, parent):
        self.infile = ""
        self.outfolder = ""

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title= "Slide Cropper")

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Input File/Folder", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        bSizer1.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.m_filePicker1 = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.ims*",
                                               wx.DefaultPosition, wx.DefaultSize,
                                               wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST)
        bSizer1.Add(self.m_filePicker1, 0, wx.ALL, 5)

        self.m_staticline11 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer1.Add(self.m_staticline11, 0, wx.EXPAND | wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"Output Directory", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        bSizer1.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.m_dirPicker1 = wx.DirPickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select an output folder",
                                             wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        bSizer1.Add(self.m_dirPicker1, 0, wx.ALL, 5)

        self.m_staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer1.Add(self.m_staticline1, 0, wx.EXPAND | wx.ALL, 5)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"Start Cropping", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_button1, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_filePicker1.Bind(wx.EVT_FILEPICKER_CHANGED, self.change_input_file)
        self.m_dirPicker1.Bind(wx.EVT_DIRPICKER_CHANGED, self.change_output_folder)
        self.m_button1.Bind(wx.EVT_BUTTON, self.start_crop)

    def __del__(self):
        pass
    # Virtual event handlers, overide them in your derived class
    def change_input_file(self, event):
        self.infile = self.m_filePicker1.GetPath()

    def change_output_folder(self, event):
        self.outfolder = self.m_dirPicker1.GetPath()

    def start_crop(self, event):
        if "" not in [self.infile, self.outfolder]:
            print(self.infile, self.outfolder)
            # SlideCropperAPI.crop_single_image(self.infile, self.outfolder)
        else:
            dlg = wx.MessageDialog(self,
            "Please select input and output paths.")
            dlg.ShowModal()

if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame  = MyFrame1(None)
    frame.Show(True)  # Show the frame.
    app.MainLoop()