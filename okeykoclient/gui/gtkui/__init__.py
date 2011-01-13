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
    def setConError(error):
        disconnect(error=error)

    def setError(error):
        dialog = gtk.Dialog('Error', MainWindow)
        dialogLabel = gtk.Label(error)
        dialogLabel.set_property('wrap', True)
        dialogLabel.show()
        dialog.vbox.pack_start(dialogLabel)
        dialog.run()
    
    def setInbox(inbox):
        Control['MainWindow'].set_inbox(inbox)

    def setPensamiento(pensamientos):
        Control['MainWindow'].set_pen(pensamientos)

    def setOutbox(outbox):
        Control['MainWindow'].set_outbox(outbox)

    def setFavorito(favbox):
        Control['MainWindow'].set_fav(favbox)

    def newInbox(mensajes):
        Control['MainWindow'].new_inbox(mensajes)
        Control['Sound'].recibido()
        #self.__MainWindow.blink() #TODO
        men = list(mensajes)
        men.reverse()
        for m in men:
            openMessage = lambda *x, **y: MainWindow.openMessage(m[3])
            Control['Notification'].mensajeNew(m[0], openMessage, None, m[4], m[2])
        
    def newPensamiento(pensamientos):
        Control['MainWindow'].new_pen(pensamientos)
        Control['Sound'].pensamiento()
        pen = list(pensamientos)
        pen.reverse()
        for p in pen:
            Control['Notification'].pensamientoNew(p[0], None, None, p[4], p[2])

    def newOutbox(outbox):
        Control['MainWindow'].new_outbox(outbox)

    def redrawDone(*args):
        #Control['ActMen'].thStart()
        Control['ThreadHandler'].createActMen()
        Control['ThreadHandler'].startActMen()
        # moved to okegtk.
        #Control['Config'].setCurrentUser(Control['Okeyko'].getUser())
        #Control['Config'].readUserConfig()
        Control['Sound'].update()
        Control['Notification'].updateConfig()
        Tray.reBuildMenu()
    
    def disconnect(*args, **kargs):
        if kargs.has_key('error'):
            MainWindow.disconnect(error=kargs['error'])
        else:
            MainWindow.disconnect()
    
    
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
    #Control['ThreadHandler'].setgui(MainWindow, Notificaciones)
    #MainWindow.connect('redraw-done', Control['ActMen'].thStart)
    MainWindow.connect('redraw-done', redrawDone)
    MainWindow.connect('redraw-disconnect', redrawDisconnect)
    
    Control['ThreadHandler'].connect('setConError', setConError)
    Control['ThreadHandler'].connect('setError', setError)
    Control['ThreadHandler'].ActMenConnect('setInbox', setInbox)
    Control['ThreadHandler'].ActMenConnect('setPensamiento', setPensamiento)
    Control['ThreadHandler'].ActMenConnect('setOutbox', setOutbox)
    Control['ThreadHandler'].ActMenConnect('setFavorito', setFavorito)
    Control['ThreadHandler'].ActMenConnect('newInbox', newInbox)
    Control['ThreadHandler'].ActMenConnect('newPensamiento', newPensamiento)
    Control['ThreadHandler'].ActMenConnect('newOutbox', newOutbox)
    
    gobject.timeout_add(500, Control['queueManager'], Control['queueToGui'])
    gtk.main()

