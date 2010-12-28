#!/usr/bin/env python
#import Queue
#import threading

import libokeyko
import Config
from gui import gtkui
import OkeThreads
import Sound


def main():
    queueToGui, queueToServer = OkeThreads.queue_maker()
    threadsServer = OkeThreads.server(queueToServer, queueToGui)
    queueManager = OkeThreads.queue_manager
    Okeyko = libokeyko.okeyko()
    Conf = Config.Main()
    Conf.writeGlobalConfig()
    Sonido = Sound.SoundHandler(Conf)
    Control = { 'queueToGui' : queueToGui, 'queueToServer' : queueToServer, \
                'Okeyko' : Okeyko, 'Config' : Conf, 'Sound' : Sonido, \
                'queueManager' : queueManager}
    ActMen = OkeThreads.actmen(Control)
    Control.update({'ActMen':ActMen})
    gtkui.gtk_main(Control)
    #Notificaciones = Notification.MainClass(Conf)
    #MainWindow = okegtk.mainWindow(Okeyko, queueToServer, Notificaciones)
    #MainWindow.connect('redraw-done', OkeThreads.actmen, Okeyko, queueToGtk, Sonido, Notificaciones)
    #Tray = TrayIcon.TrayIcon(MainWindow)
    #OkeThreads.actmen(MainWindow, Okeyko, conectado, Sonido, Notificaciones)
    #gobject.timeout_add(500, OkeThreads.queue_manager, queueToGtk)
    #gtk.main()

if __name__ == "__main__":
    main()


