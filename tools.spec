# -*- mode: python -*-

block_cipher = None


a = Analysis(['D:\PythonProject\\tools\core\\tools.py'],
             pathex=['D:\\PythonProject\\tools'],
             binaries=[],
             datas=[],
             hiddenimports=['toolKit.classes', 'toolKit.encryption', 'toolKit.lyric'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tools',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
