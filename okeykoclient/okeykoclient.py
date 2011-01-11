#!/usr/bin/env python
#import Queue
#import threading

import Sound
import Config
import desktop
try:
    import libokeyko
except:
    import libokeyko_beautifulSoup as libokeyko
import OkeThreads
from gui import gtkui




def main():
    #queueToGui, queueToServer = OkeThreads.queue_maker()
    #threadsServer = OkeThreads.server(queueToServer, queueToGui)
    ThreadHandler = OkeThreads.ThreadHandler()
    queueManager = OkeThreads.queue_manager
    Okeyko = libokeyko.okeyko()
    Conf = Config.Main()
    Conf.writeGlobalConfig()
    if Conf.glob['useProxy']:
        Okeyko.setProxy(Conf.glob['proxyHost'], Conf.glob['proxyPort'],
                Conf.glob['proxyUsername'], Conf.glob['proxyPassword'] )
    Sonido = Sound.SoundHandler(Conf)
    #Control = { 'queueToGui' : queueToGui, 'queueToServer' : queueToServer, \
    #            'Okeyko' : Okeyko, 'Config' : Conf, 'Sound' : Sonido, \
    #            'queueManager' : queueManager}
    desktop.override = Conf.glob['overrideDesktop']
    Control = { 'queueToGui' : ThreadHandler.queueToGui,
                'queueToServer' : ThreadHandler.queueToServer, 
                'Okeyko' : Okeyko, 'Config' : Conf, 'Sound' : Sonido, 
                'queueManager' : queueManager, 'ThreadHandler' : ThreadHandler,
                'desktop' : desktop}
    ThreadHandler.setControl(Control)    
    #ActMen = OkeThreads.actmen(Control)
    #Control.update({'ActMen':ActMen})
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


