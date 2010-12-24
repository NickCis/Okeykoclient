#!/usr/bin/python

from distutils.core import setup, Extension
from glob import glob
import os
import sys

if os.name == 'posix':
    for arg in sys.argv:
        if arg == 'install': 
            print 'Hello.\nYou are trying to do a system-wide install of Okeykoclient '\
                  'using this script, which is a very bad thing to do.\n'\
                  'Seriously, you do NOT want to do this, since it can break '\
                  'other python apps, and emesene too!\n'\
                  'Follow my advice: just run the \"Okeykoclient\" script that is '\
                  'in this very same directory and you\'re done. emesene is running '\
                  'and your system is safe. It\'s a win-win, don\'t you think?\n'\
                  'Thanks for trying Okeykoclient.'
            quit()

    # From apport's setup.py
    #mo_files = []
    #for filepath in glob("po/*/LC_MESSAGES/*.mo"):
    #    lang = filepath[len("po/"):]
    #    targetpath = os.path.dirname(os.path.join("share/locale",lang))
    #    mo_files.append((targetpath, [filepath]))

    #libmimic_module = Extension('libmimic',
    #                    sources = ['libmimic/' + file for file in ['bitstring.c', 
    #                     'colorspace.c', 'deblock.c', 'decode.c', 'encode.c',
    #                     'fdct_quant.c', 'idct_dequant.c', 'mimic.c', 'vlc_common.c', 
    #                     'vlc_decode.c', 'vlc_encode.c', 'py_libmimic.c']])

    setup(name         = 'Okeykoclient',
          version      = '0',
          description  = 'Cliente para la red de mesajeria Okeyko',
          author       = 'Nicolas Cisco, se agradece a toda la comunidad de emesene y a la de Pyar',
          author_email = 'ncis20@gmail.com',
          url          = 'http://okeykoclient.sourceforge.net/',
          license      = 'GNU GPL 2',
          requires     = ['gtk'],
          platforms    = ['any'],
          packages     = ['', 'gui', 'gui.gtkui'],
          scripts      = ['Okeykoclient'],
          package_data = {'': ['themes/*/*']},
          #data_files   = [('share/pixmaps', ['misc/emesene.png']),
          #                ('share/icons/hicolor/scalable/apps', ['misc/emesene.svg']),
          #                ('share/man/man1', ['misc/emesene.1']),
          #                ('share/applications', ['misc/emesene.desktop'])] + mo_files,
          #ext_modules = [libmimic_module]
          )
elif os.name == 'nt':
    import pygst  
    pygst.require("0.10")
    import gst

    enabled = True

    if not enabled:
        print "py2exe setup.py"
        print "(disabled, see source)"
        raise SystemExit

    import gobject
    import locale
    import py2exe

    try:
        revision = "$Revision $".split()[1]
    except:
        revision = 0
    version_id = "0"

    #outdata_base = {
    #    "script": "Controller.py",
    #    "icon_resources": [(1, "../emesene.ico")]
    #}

    outdata_win = outdata_base.copy()
    outdata_win['dest_base'] = "Okeykoclient"

    outdata_con = outdata_base.copy() 
    outdata_con['dest_base'] = "Okeykoclient_debug"

    opts = {
        'py2exe': {
    #        'packages': ['encodings', 'gtk', 'email', 'abstract', 'emesenelib', 'emesenelib.p2p',
            'packages': ['gtk', 'gui', 'gui.gtkui', 'themes'],
            'includes': ['locale', 'gst', 'gio', 'pygst', 'poplib', 'cairo', 'pangocairo', 'pango', 'atk', 'gobject',
                'os', 'code', 'winsound', 'win32api', 'win32gui'],
            'excludes': ["ltihooks", "gdk", "pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                "pywin.dialogs", "pywin.dialogs.list",
                "Tkconstants","Tkinter","tcl",
                "doctest","macpath","pdb",
                "cookielib","ftplib","pickle",
                "calendar","win32wnet","unicodedata",
                "getopt","optparse"],
            'dll_excludes': ["libglade-2.0-0.dll", "w9xpopen.exe"],
            'optimize': '2',
            'dist_dir': '../dist',
            }
        }

    #included plugins list
    #plugins = [
    #"__init__.py",
    #"AntiBoss.py",
    #"Commands.py",
    #"CurrentSong.py",
    #"CustomStatus.py",
    #"EmoticonPlugin.py",
    #"EncryptedMessage.py",
    #"Eval.py",
    #"Facebook.py",
    #"gmailNotify.py",
    #"IdleStatus.py",
    #"InlineNotify.py",
    #"LastSaid.py",
    #"LogConversation.py",
    #"Logger.py",
    #"mailChecker.py",
    #"Notification.py",
    #"Plugin.py",
    #"Plus.py",
    #"PlusColorPanel.py",
    #"Screenshots.py",
    #"StatusHistory.py",
    #"TinyUrl.py",
    #"WindowTremblingNudge.py",
    #"WinkReceiving.py"
    #,]

    #plugins = [ "../emesene/plugins_base/" + p for p in plugins ]

    os.chdir("../Okeykoclient")

    files = []
    #individual files
    #files.append( (".", ("../emesene/hotmlog.htm", "../emesene/COPYING", \
    #    "../dlls/libxml2-2.dll", "../dlls/msvcr90.dll", "../dlls/Microsoft.VC90.CRT.manifest",\
    #    "../dlls/jpeg62.dll", "../emesene/GPL", "../emesene/PSF", "../emesene/LGPL")) )
    files.append( (".", ("../Okeykoclient/README")) )
    #files.append( ("smilies/default", glob("../emesene/smilies/default/*.*")) )

    #files.append( ("plugins_base", plugins) )

    #files.append( ("plugins_base/currentSong", \
    #            ["../emesene/plugins_base/currentSong/__init__.py", \
    #            "../emesene/plugins_base/currentSong/AIMP2.py", \
    #            "../emesene/plugins_base/currentSong/Amarok.py", \
    #            "../emesene/plugins_base/currentSong/Amarok2.py", \
    #            "../emesene/plugins_base/currentSong/aTunes.py", \
    #            "../emesene/plugins_base/currentSong/Audacious.py", \
    #            "../emesene/plugins_base/currentSong/Banshee.py", \
    #            "../emesene/plugins_base/currentSong/Clementine.py", \
    #            "../emesene/plugins_base/currentSong/Consonance.py", \
    #            "../emesene/plugins_base/currentSong/CurrentSong.py", \
    #            "../emesene/plugins_base/currentSong/Exaile.py", \
    #            "../emesene/plugins_base/currentSong/Foobar2000.py", \
    #            "../emesene/plugins_base/currentSong/Gmusicbrowser.py", \
    #            "../emesene/plugins_base/currentSong/GOMPlayer.py", \
    #            "../emesene/plugins_base/currentSong/Guayadeque.py", \
    #            "../emesene/plugins_base/currentSong/LastFm.py", \
    #            "../emesene/plugins_base/currentSong/Listen.py", \
    #            "../emesene/plugins_base/currentSong/MediaMonkey.py", \
    #            "../emesene/plugins_base/currentSong/MediaPlayerClassic.py", \
    #            "../emesene/plugins_base/currentSong/Mesk.py", \
    #            "../emesene/plugins_base/currentSong/Mpd.py", \
    #            "../emesene/plugins_base/currentSong/OneByOne.py", \
    #            "../emesene/plugins_base/currentSong/QuodLibet.py", \
    #            "../emesene/plugins_base/currentSong/RealPlayer.py", \
    #            "../emesene/plugins_base/currentSong/Rhythmbox.py", \
    #            "../emesene/plugins_base/currentSong/SMPlayer.py", \
    #            "../emesene/plugins_base/currentSong/Songbird.py", \
    #            "../emesene/plugins_base/currentSong/Spotify.py", \
    #            "../emesene/plugins_base/currentSong/Vagalume.py", \
    #            "../emesene/plugins_base/currentSong/Vlc.py", \
    #            "../emesene/plugins_base/currentSong/Winamp.py", \
    #            "../emesene/plugins_base/currentSong/Xfmedia.py", \
    #            "../emesene/plugins_base/currentSong/Xmms.py", \
    #            "../emesene/plugins_base/currentSong/Xmms2.py", \
    #            "../emesene/plugins_base/currentSong/XMPlay.py"]) ) 

    #files.append( ("plugins_base/encryptMessage", \
    #            ["../emesene/plugins_base/encryptMessage/__init__.py", \
    #            "../emesene/plugins_base/encryptMessage/__rijndael.py", \
    #            "../emesene/plugins_base/encryptMessage/GPG.py", \
    #            "../emesene/plugins_base/encryptMessage/MainEncryptedMessage.py", \
    #            "../emesene/plugins_base/encryptMessage/Rijndael.py"]) )     

    #gtk file structure

    #directories with variable contents
    #for i in glob("../emesene/po/*"):
    #    files.append( (i.split("/emesene/")[1] + '/LC_MESSAGES', glob(i+"/LC_MESSAGES/*")) )

    for i in glob("../Okeykoclient/themes/*"):
        files.append( (i.split("/Okeykoclient/")[1], glob(i+"/*.*")) )

    setup(
        name="Okeykoclient",
        version=version_id,
        description  = 'Cliente para la red de mensajeria Okeyko',
        author       = 'Nicolas Cisco, se agradece a toda la comunidad de emesene y a la de Pyar',
        author_email = 'ncis20@gmail.com',
        url          = 'http://okeykoclient.sourceforge.net/',
        license      = 'GNU GPL 2',
        requires     = ['gtk'],
        windows=[outdata_win],
        console=[outdata_con],
        options=opts,
        data_files=files)
        #ext_modules = [libmimic_module])

    print "Done! Files are here: ../dist/"
