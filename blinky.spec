# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\blinky.py'],
             pathex=['Z:\\src'],
             binaries=[],
             datas=[
                ('c:\\Python36\\lib\\site-packages\\text_unidecode\\data.bin','text_unidecode'),
                ('/wine/drive_c/Python36/Lib/site-packages/webview/lib/WebBrowserInterop.x64.dll','webview/lib'),
                ('/wine/drive_c/Python36/Lib/site-packages/certifi/cacert.pem','certifi'),
                ('src/templates/*','templates'),
                ('src/static/css/*', 'static/css'),
                ('src/static/videos/*', 'static/vidoes')
             ],
             hiddenimports=[],
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
          name='blinky',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
