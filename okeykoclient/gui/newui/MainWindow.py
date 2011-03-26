import gtk

import WebEngine

class MainWindow(gtk.Window):
    def __init__(self, Control):
        gtk.Window.__init__(self)
        
        self.__Control = Control
        self.__Config = Control['Config']

        iconPath = self.__Config.pathFile('theme-logo.png')
        icon = gtk.gdk.pixbuf_new_from_file_at_size(iconPath, 64, 64)
        self.set_icon_list(icon)
        
        self.parse_geometry(self.__Config.glob['mainWindowGeometry'])
        if self.__Config.glob['disableTrayIcon']:
            self.connect("delete_event", self.askExit)
        else:
            self.connect("delete_event", self.showHide)
        self.set_title("Okeyko ::: Cliente")
        self.WebEngine = WebEngine.WebEngine(Control)

        self.add(self.WebEngine)
        
        self.show_all()


    def saveWindowGeometry(self):
        xPos, yPos = self.get_position()
        wWin, hWin = self.get_size()
        mainWinGeometry = "%sx%s+%s+%s" % (wWin, hWin, xPos, yPos)
        if self.__Config.glob['mainWindowGeometry'] != mainWinGeometry:
            self.__Config.glob['mainWindowGeometry'] = mainWinGeometry

    def showHide(self, widget=None, *args):
        '''Show or hide the main window'''
        if self.flags() & gtk.VISIBLE:
            self.saveWindowGeometry()
            self.hide()
        else:
            self.deiconify()
            self.show()
        return True

    def askExit(self, widget=None, *args):
        '''Ask About closing when tray disabled'''
        askDialog = gtk.Dialog("Desea Salir de OkeykoClient?",
                     self,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        askLabel = gtk.Label('Desea Cerrar Okeykoclient?')
        askLabel.show()
        askImage = gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
        askImage.show()
        askDialog.vbox.pack_start(askImage)
        askDialog.vbox.pack_start(askLabel)
        rta = askDialog.run()
        if rta == -3:
            self.__Control['Quit']()
        askDialog.destroy()
        return True
