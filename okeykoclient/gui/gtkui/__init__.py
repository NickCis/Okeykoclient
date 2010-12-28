import os
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import okegtk
import Notification
import TrayIcon

def gtk_main(Control):

    def redrawDone(*args):
        Control['ActMen'].thStart()
        Control['Sound'].update()
        Tray.reBuildMenu()
    
    def redrawDisconnect(*args):
        Control['Sound'].clearUpdate()
        Control['Okeyko'].disconnect()
        Control['ActMen'].thStop()
        Tray.buildMenu()
    
    if os.name != 'nt':
        gtk.gdk.threads_init()

    OKC_FOKY = 'okc-foky'
    gtk.stock_add(((OKC_FOKY, '_FOKY', gtk.gdk.CONTROL_MASK, gtk.gdk.keyval_from_name('P'), 'FOKY'),))
    pixbufFoky = gtk.gdk.pixbuf_new_from_file(Control['Config'].pathFile('theme-foky.png'))
    iconSetFoky = gtk.IconSet(pixbufFoky)
    iconFact = gtk.IconFactory()
    iconFact.add(OKC_FOKY, iconSetFoky)
    iconFact.add_default()

    Notificaciones = Notification.MainClass(Control)
    Control.update({'Notification': Notificaciones})
    MainWindow = okegtk.mainWindow(Control)
    Control.update({'MainWindow': MainWindow})
    Tray = TrayIcon.TrayIcon(MainWindow)
    Control['ActMen'].setgui(MainWindow, Notificaciones)
    #MainWindow.connect('redraw-done', Control['ActMen'].thStart)
    MainWindow.connect('redraw-done', redrawDone)
    MainWindow.connect('redraw-disconnect', redrawDisconnect)
    gobject.timeout_add(500, Control['queueManager'], Control['queueToGui'])
    gtk.main()

