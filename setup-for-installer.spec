# -*- mode: python -*-

block_cipher = None


a = Analysis(['PyEveLiveDPS\\peld.py'],
             pathex=['.\\PyEveLiveDPS'],
             binaries=[],
             datas=[('app.ico', '.'), ('.\\PyEveLiveDPS\\images\\*.png', 'images'), ('.\\PyEveLiveDPS\\images\\*.gif', 'images')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PELD',
          debug=False,
          strip=False,
          upx=True,
          console=False, icon='app.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PELD')
