#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import Queue
import gobject
import threading

import libokeyko
import Config
import okegtk
import TrayIcon
import OkeThreads
import Sound
import Notification 

if __name__ == "__main__":
    gtk.gdk.threads_init()
    queueToGtk = Queue.Queue()
    queueToServer = Queue.Queue()
    Server = OkeThreads.server(queueToServer, queueToGtk)
    Okeyko = libokeyko.okeyko()
    Conf = Config.Main()
    Sonido = Sound.Sound(Conf)
    Notificaciones = Notification.MainClass(Conf)
    MainWindow = okegtk.mainWindow(Okeyko, queueToServer, Notificaciones)   
    MainWindow.connect('redraw-done', OkeThreads.actmen, Okeyko, queueToGtk, Sonido, Notificaciones)
    Tray = TrayIcon.TrayIcon(MainWindow)
    #OkeThreads.actmen(MainWindow, Okeyko, conectado, Sonido, Notificaciones)
    gobject.timeout_add(500, OkeThreads.queue_manager, queueToGtk)
    gtk.main()

