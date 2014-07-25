# -*- mode: python -*-
def Datafiles(*filenames, **kw):
	import os
	
	def datafile(path,strip_path=True):
		parts = path.split('/')
		path = name = os.path.join(*parts)
		if strip_path:
			name = os.path.basename(path)
		return name, path, 'DATA'
		
	strip_path = kw.get('strip_path',True)
	return TOC(
		datafile(filename,strip_path=strip_path)
		for filename in filenames
		if os.path.isfile(filename))
		
a = Analysis(['E:\\Shared with Win7\\SlideCrop2.0\\MainGUI.py'],
             pathex=['E:\\Shared with Win7\\SlideCrop2.0\\'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\SlideCrop', 'SlideCrop.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='E:\\Shared with Win7\\SlideCrop2.0\\icon.ico')

schema = Datafiles('E:\\Shared with Win7\\SlideCrop2.0\\ome.xsd',
					'E:\\Shared with Win7\\SlideCrop2.0\\help.html',
					'E:\\Shared with Win7\\SlideCrop2.0\\selectforcrop.png',
					'E:\\Shared with Win7\\SlideCrop2.0\\manualseg.png',
					'E:\\Shared with Win7\\SlideCrop2.0\\loadimage.png',
					'E:\\Shared with Win7\\SlideCrop2.0\\autoseg.png',
					'E:\\Shared with Win7\\SlideCrop2.0\\applythreshold.png')
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
			   schema,
               upx=True,
               name=os.path.join('dist', 'SlideCrop'))