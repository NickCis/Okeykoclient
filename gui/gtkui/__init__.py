import pygtk
pygtk.require('2.0')
import gtk
import gobject

import okegtk
import Notification
import TrayIcon

def gtk_main(Control):
    gtk.gdk.threads_init()
    #Notificaciones = Notification.MainClass(Control)
    MainWindow = okegtk.mainWindow(Control)
    #MainWindow.connect('redraw-done', OkeThreads.actmen, Okeyko, queueToGtk, Sonido, Notificaciones)
    Tray = TrayIcon.TrayIcon(MainWindow)
    gobject.timeout_add(500, Control['queueManager'], Control['queueToGui'])
    gtk.main()
