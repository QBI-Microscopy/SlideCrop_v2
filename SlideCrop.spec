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
		
a = Analysis(['C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\main_gui.py'],
             pathex=['C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\SlideCrop', 'SlideCrop.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\icon.ico')

schema = Datafiles('C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\ome.xsd',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\help.html',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\selectforcrop.png',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\manualseg.png',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\loadimage.png',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\autoseg.png',
					'C:\\Users\\uqdmatt2\\Documents\\Python\\SlideCrop\\applythreshold.png')
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
	       schema,
               upx=True,
               name=os.path.join('dist', 'SlideCrop'))
