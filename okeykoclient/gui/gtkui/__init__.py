import os
import sys
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import okegtk
import Notification
import TrayIcon

def gtk_main(Control):

    def redrawDone(*args):
        #Control['ActMen'].thStart()
        Control['ThreadHandler'].startActMen()
        # moved to okegtk.
        #Control['Config'].setCurrentUser(Control['Okeyko'].getUser())
        #Control['Config'].readUserConfig()
        Control['Sound'].update()
        Control['Notification'].updateConfig()
        Tray.reBuildMenu()
    
    def redrawDisconnect(*args):
        Control['Sound'].clearUpdate()
        Control['Okeyko'].disconnect()
        #Control['ActMen'].thStop()
        Control['ThreadHandler'].killActMen()
        Tray.buildMenu()

    def quit(*args):
        for window in gtk.window_list_toplevels(): #Hides all windows. 
            try:
                window.saveMainWindowGeometry()
            except:
                pass
            window.hide()
        if not Tray.disabled:
            Tray.remove()
        gtk.main_quit()
        if Control['Okeyko'].conectado()[0]:
            Control['Config'].writeUserConfig()
            Control['Okeyko'].disconnect()
        Control['Config'].writeGlobalConfig()
        sys.exit(0)
        
    
    if os.name != 'nt':
        gtk.gdk.threads_init()

    OKC_FOKY = 'okc-foky'
    gtk.stock_add(((OKC_FOKY, '_FOKY', gtk.gdk.CONTROL_MASK, gtk.gdk.keyval_from_name('P'), 'FOKY'),))
    pixbufFoky = gtk.gdk.pixbuf_new_from_file(Control['Config'].pathFile('theme-foky.png'))
    iconSetFoky = gtk.IconSet(pixbufFoky)
    iconFact = gtk.IconFactory()
    iconFact.add(OKC_FOKY, iconSetFoky)
    iconFact.add_default()
    Control.update({'Quit': quit})
    Notificaciones = Notification.MainClass(Control)
    Control.update({'Notification': Notificaciones})
    MainWindow = okegtk.mainWindow(Control)
    Control.update({'MainWindow': MainWindow})
    #Tray = TrayIcon.TrayIcon(MainWindow)
    Tray = TrayIcon.TrayIcon(Control)    
    #Control['ActMen'].setgui(MainWindow, Notificaciones)
    Control['ThreadHandler'].setgui(MainWindow, Notificaciones)
    #MainWindow.connect('redraw-done', Control['ActMen'].thStart)
    MainWindow.connect('redraw-done', redrawDone)
    MainWindow.connect('redraw-disconnect', redrawDisconnect)
    gobject.timeout_add(500, Control['queueManager'], Control['queueToGui'])
    gtk.main()

