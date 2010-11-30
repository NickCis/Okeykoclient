import pygtk
pygtk.require('2.0')
import gtk
import gobject

import okegtk
import Notification
import TrayIcon

def gtk_main(Control):
    gtk.gdk.threads_init()
    Notificaciones = Notification.MainClass(Control)
    Control.update({'Notification' : Notificaciones})
    MainWindow = okegtk.mainWindow(Control)    
    Tray = TrayIcon.TrayIcon(MainWindow)
    Control['ActMen'].setgui(MainWindow, Notificaciones)
    MainWindow.connect('redraw-done', Control['ActMen'].thStart)
    gobject.timeout_add(500, Control['queueManager'], Control['queueToGui'])
    gtk.main()

