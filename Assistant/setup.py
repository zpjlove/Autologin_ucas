import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'


options = {
'build_exe':{'include_files':['id.xlsx']},
}

executables = [Executable('init.py', base=base, targetName='Assistant.exe')]

setup(
    name="Assistant",
    version="1.0.0",
    author='zhangpengjie',
    author_email='zhangpengjie1993@163.com',
    description="You needn't worry about the flow in ucas!",
    options=options,
    executables=executables,
)