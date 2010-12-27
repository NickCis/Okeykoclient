#!/usr/bin/python

try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages, Extension

import os
import platform

python_version = platform.python_version()[0:3]

setup_info = dict(name = 'okeykoclient',
        version = '0',
        description = 'Cliente para la red de mesajeria Okeyko',
        author = 'Nicolas Cisco, se agradece a toda la comunidad de emesene y a la de Pyar',
        author_email = 'ncis20@gmail.com',
        keywords = "okeyko sms",
        long_description = """Okeykoclient es un cliente para la red de mensajeria okeyko""",
        url = 'http://okeykoclient.sourceforge.net/',
        license = 'GNU GPL 3',
        classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications :: Chat",
        ],
        ext_package = "okeykoclient",
        include_package_data = True,
        package_data = {"okeykoclient" : ['themes/*/*']})

def windows_check():
    return platform.system() in ('Windows', 'Microsoft')

def osx_check():
    return platform.system() == "Darwin"


if os.name == 'nt':
    import py2exe

    _data_files = ['../dlls/Microsoft.VC90.CRT.manifest',
            '../dlls/msvcm90.dll',
            '../dlls/msvcp90.dll',
            '../dlls/msvcr71.dll',
            '../dlls/msvcr90.dll']


    for base in ("themes",):
        for dirname, dirnames, files in os.walk(base):
            fpath = []
            for file in files:
                fpath.append(os.path.join(dirname, file))
            _data_files.append((dirname, fpath))

    opts = {
        'py2exe': {
            'packages': ['encodings', 'gtk',],
            'includes': ['locale', 'gio', 'cairo', 'pangocairo', 'pango',
                'atk', 'gobject', 'os', 'code', 'winsound', 'win32api',
                'win32gui'],
            'excludes': ['ltihooks', 'pywin', 'pywin.debugger',
                'pywin.debugger.dbgcon', 'pywin.dialogs',
                'pywin.dialogs.list', 'Tkconstants', 'Tkinter', 'tcl'
                'doctest', 'macpath', 'pdb', 'cookielib', 'ftplib',
                'pickle', 'caledar', 'win32wnet', 'unicodedata',
                'getopt', 'gdk'],
            'dll_excludes': ['libglade-2.0-0.dll', 'w9xpopen.exe'],
            'optimize': '2',
            'dist_dir': '../dist',
            "skip_archive": 1
        }
    }

    setup(requires    = ["gtk"],
        windows        = [{"script": "okeyko.py", 'icon_resources': [(1, "okeykoclient.ico")], "dest_base": "okeykoclient"}],
        console        = [{"script": "okeyko.py", "dest_base": "okeykoclient_debug"}],
        options        = opts,
        data_files    = _data_files, **setup_info)

    print "done! files at: dist"

else:
    # Data files to be installed to the system
    _data_files = [
        ('share/icons/scalable/apps', ['okeykoclient/data/icons/scalable/apps/okeykoclient.svg']),
        ('share/icons/hicolor/16x16/apps', ['okeykoclient/data/icons/hicolor/16x16/apps/okeykoclient.png']),
        ('share/icons/hicolor/22x22/apps', ['okeykoclient/data/icons/hicolor/22x22/apps/okeykoclient.png']),
        ('share/icons/hicolor/24x24/apps', ['okeykoclient/data/icons/hicolor/24x24/apps/okeykoclient.png']),
        ('share/icons/hicolor/32x32/apps', ['okeykoclient/data/icons/hicolor/32x32/apps/okeykoclient.png']),
        ('share/icons/hicolor/36x36/apps', ['okeykoclient/data/icons/hicolor/36x36/apps/okeykoclient.png']),
        ('share/icons/hicolor/48x48/apps', ['okeykoclient/data/icons/hicolor/48x48/apps/okeykoclient.png']),
        ('share/icons/hicolor/64x64/apps', ['okeykoclient/data/icons/hicolor/64x64/apps/okeykoclient.png']),
        ('share/icons/hicolor/72x72/apps', ['okeykoclient/data/icons/hicolor/72x72/apps/okeykoclient.png']),
        ('share/icons/hicolor/96x96/apps', ['okeykoclient/data/icons/hicolor/96x96/apps/okeykoclient.png']),
        ('share/icons/hicolor/128x128/apps', ['okeykoclient/data/icons/hicolor/128x128/apps/okeykoclient.png']),
        ('share/icons/hicolor/192x192/apps', ['okeykoclient/data/icons/hicolor/192x192/apps/okeykoclient.png']),
        ('share/icons/hicolor/256x256/apps', ['okeykoclient/data/icons/hicolor/256x256/apps/okeykoclient.png']),
        ('share/applications', ['okeykoclient/data/share/applications/okeykoclient.desktop']),
        ('share/pixmaps', ['okeykoclient/data/pixmaps/okeykoclient.png', 'okeykoclient/data/pixmaps/okeykoclient.xpm']),
        ('bin', ['okeykoclient/data/bin/okeykoclient'])
        #('share/man/man1', ['docs/man/emesene.1'])
    ]

    setup(data_files = _data_files,
        packages = find_packages(), **setup_info)
