import sys
import os,shutil
from cx_Freeze import setup, Executable
base = None
executables = [Executable(script='tiro_proxy.py',
               base=base,
               targetName="tiro.exe",
               compress=True)]
setup(name='tiroFinale',
      version='1.0',
      description='tiroFinale HTTP Proxy',
      options={'build_exe':{
        'optimize':2,
        'include_files':['const.py'],
        'excludes':'const',
      }},
      executables=executables)

#os.remove('build/exe.win32-3.4/unicodedata.pyd')

if os.path.isdir('openssl'):
    shutil.copytree('openssl','build/exe.win32-3.4/openssl')
shutil.copytree('ssl_stuff','build/exe.win32-3.4/ssl_stuff')

print('===== DONE =====')

