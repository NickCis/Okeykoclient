import gtk
import gobject

UILOGIN = '''<ui>
    <menubar name="MenuBar">
      <menu action="Cuenta">
        <menuitem action="Crear"/>
        <menuitem action="Salir"/>
      </menu>
      <menu action="Pref">
        <menuitem action="Settings"/>
      </menu>
      <menu action="Ayuda">
        <menuitem action="OkePag"/>
        <menuitem action="Pag"/>
        <separator/>
        <menuitem action="About"/>
      </menu>
    </menubar>
    </ui>'''


class LoginWindow(gtk.VBox):
    __gsignals__ = {
        'connected': (gobject.SIGNAL_RUN_LAST, None, () ),
        'aboutOpen': (gobject.SIGNAL_RUN_LAST, None, () ),
        'settingsOpen': (gobject.SIGNAL_RUN_LAST, None, () ),
        'openLink': (gobject.SIGNAL_RUN_LAST, None, (str,) ),
    }

    def __init__(self, Control):
        def launchPag(*args): #TODO
            pag = args[0].get_name()
            if pag == 'OkePag':
                self.emit('openLink', 'http://www.okeyko.com')
            elif pag == 'Pag':
                self.emit('openLink', 'http://okeykoclient.sourceforge.net')
            elif pag == 'Crear':
                self.emit('openLink', "http://www.okeyko.com/")
            
        def aboutClient(*args): #TODO
            self.emit('aboutOpen')

        def SettingsWin(*args):
            d = gtk.Dialog()
            d.vbox.pack_start(gtk.Label('Proximamente'))
            d.show_all()
            self.emit('settingsOpen')
            #ST = SettingsWindow.SettingsWindow(self.__Control, self)
            #ST.show()    
    
        gtk.VBox.__init__(self, False, 0)
        
        self.__Control = Control
        self.__Config = Control['Config']
        self.__Okeyko = Control['Okeyko']
        self.__queueToServer = Control['queueToServer']

        uimanager = gtk.UIManager() #Create a Uimanager instance   
           
        self.accelgroup = uimanager.get_accel_group() # add accelartor group #TODO
        #self.add_accel_group(accelgroup)         # to the toplevel win
        
        actiongroup = gtk.ActionGroup('UIManagerMenuLogin') # Create Action Group
        
        #create actions        
        # (Name, StockItem, Label, accelerator, ToolTip, CallBack)
        actiongroup.add_actions([('Cuenta', None, '_Cuenta'),
                                 ('Salir', gtk.STOCK_QUIT, '_Salir', "<Ctrl><Alt>q",
                                    'Salir', self.__Control['Quit']),
                                 ('Pref', None, '_Preferencias'),
                                 ('Settings', gtk.STOCK_PREFERENCES, '_Ajustes', None, 
                                    'Abrir ventana de ajustes', SettingsWin),
                                 ('Ayuda', None, '_Ayuda'),
                                 ('Crear', gtk.STOCK_HOME, '_Crear Cuenta',
                                    None, None, launchPag),
                                 ('OkePag', gtk.STOCK_HOME, 'Pagina de _Inicio',
                                    None, None, launchPag),
                                 ('Pag', gtk.STOCK_INFO, 'Pagina del _Cliente',
                                    None, None, launchPag),
                                 ('About', gtk.STOCK_ABOUT, 'Acerca _de', None,
                                    "Borrar Mensaje", aboutClient)])

        uimanager.insert_action_group(actiongroup, 0) #Add actiongroup to the uimanager        
        uimanager.add_ui_from_string(UILOGIN) #Add UI description         
        menubar = uimanager.get_widget('/MenuBar') #Create MenuBar
        self.pack_start(menubar, False)
        
        self.errorBox = gtk.EventBox()
        self.errorBox.modify_bg(gtk.STATE_NORMAL,
                            self.errorBox.get_colormap().alloc_color("yellow"))
        self.errorBox.set_no_show_all(True)
        self.pack_start(self.errorBox, False)

        
        align = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5,
            yscale=1.0)
        self.pack_start(align)
        vbox = gtk.VBox(True, 0)
        align.add(vbox)
        
        self.loginImg = gtk_LoginImage(self.__Config.pathFile('theme-logo.png'), 150)
        vbox.pack_start(self.loginImg, False, False, 0)
        
        self.VboxInput = gtk.VBox()
        vbox.pack_start(self.VboxInput, False, False, 0)
        
        labentryhbox = gtk.HBox(False)
        labentry = gtk.Label("Usuario:")
        labentryhbox.pack_start(labentry, False, False, 0)
        self.VboxInput.pack_start(labentryhbox, True, True, 0)
        self.userEntry = gtk.Entry()
        self.VboxInput.pack_start(self.userEntry, True, True, 0)  
        entryComp = gtk.EntryCompletion()
        self.userEntry.set_completion(entryComp)
        userListStore = gtk.ListStore (str, str)
        for a, b in self.__Config.userList:
            userListStore.append([a,'foto',])
        entryComp.set_model (userListStore)
        entryComp.set_text_column(0)

        labcontrahbox = gtk.HBox(False)
        labcontra = gtk.Label("Password:")
        labcontrahbox.pack_start(labcontra, False, False, 0)
        self.VboxInput.pack_start(labcontrahbox, True, False, 0)
        contra = gtk.Entry()
        contra.set_max_length(50)
        contra.set_visibility(False)
        self.VboxInput.pack_start(contra, True, False, 0)
        
        
        
        
        
        
        self.conectadoAnim = gtk.VBox()
        self.conectadoAnim.set_no_show_all(True)
        self.pack_start(self.conectadoAnim, False, False, 0)
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        label = gtk.Label("\n Conectando \n")
        label.set_use_markup(True)
        self.conectadoAnim.pack_start(anim, False, False, 0)
        self.conectadoAnim.pack_start(label, False, False, 0)
        anim.show()
        label.show()
        
        
        
        
        
        

        ButtonAlign = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0,
            yscale=1.0)
        self.buttonBox = gtk.VBox()
        ButtonAlign.add(self.buttonBox)

        vbox.pack_start(ButtonAlign, False, False, 0)                
        checkRe = gtk.CheckButton("Recordar Me")
        self.buttonBox.pack_start(checkRe)
        checkRe.set_active(self.__Config.glob['rememberMe'])    
        checkRC = gtk.CheckButton("Recordar Password")
        self.buttonBox.pack_start(checkRC)
        checkRC.set_active(self.__Config.glob['rememberMyPassword'])
        checkAL = gtk.CheckButton("Auto Login")
        self.buttonBox.pack_start(checkAL)
        checkAL.set_active(False)

        self.button = gtk.Button("Conectar")
        contra.connect("activate", self.conectar, self.userEntry, contra,
            (checkRe.get_active, checkRC.get_active, checkAL.get_active))
        self.button.connect("clicked", self.conectar, self.userEntry, contra,
            (checkRe.get_active, checkRC.get_active, checkAL.get_active))
        vbox.pack_start(self.button, False, False, 0)

        self.userEntry.connect('focus-out-event', self.entryUFocusOut,
            contra, (checkRe.set_active, checkRC.set_active,
            checkAL.set_active))
        entryComp.connect('match-selected', self.seterCompletionEntry,
            self.userEntry, contra, (checkRe.set_active, checkRC.set_active,
            checkAL.set_active))

        self.show_all()

    def seterCompletionEntry(self, completion, model, Iter, entry,
                                                    contra, checks):
        entry.set_text(model[Iter][0])
        contra.grab_focus()

    def entryUFocusOut(self, widget, event, contra, checks):
        key = widget.get_text()
        if key in self.__Config.userList:
            if self.__Config.userList[key] != "0":
                contra.set_text(self.__Config.userList[key])
                checks[0](True)
                checks[1](True)
            else:
                checks[0](True)
                checks[1](False)
        else:
            contra.set_text('')
            checks[1](False)
        self.loginImg.set_from_path(self.__Config.profileAvatarLoad(key, False)[1])
        

    def conectar(self, widget, user, contra, checks):
        ''' Callback para conectar '''
        def post_conectar(arg, checks, Uerror=None):
            conectado, error = self.__Okeyko.conectado()
            if Uerror != None:
                error = Uerror
            if conectado:
                if checks[0]():
                    if checks[1]():
                        self.__Config.userList[entry_text] = contra_text
                    else:
                        self.__Config.userList[entry_text] = False
                self.emit('connected')
            else:
                self.conectadoAnim.hide()
                #self.set_property("sensitive", True)
                #self.buttonBox.set_property("sensitive", True)
                self.buttonBox.show()
                self.VboxInput.set_property("sensitive", True)
                self.button.show()
                if self.errorBox.child:
                   self.errorBox.remove(self.errorBox.child)
                hboxerror = gtk.HBox()
                imageerror = gtk.image_new_from_stock(gtk.STOCK_DIALOG_ERROR,
                                                 gtk.ICON_SIZE_LARGE_TOOLBAR)
                hboxerror.pack_start(imageerror)
                laberror = gtk.Label(error)
                hboxerror.pack_start(laberror)
                self.errorBox.add(hboxerror)
                hboxerror.show_all()
                self.errorBox.show()

        #self.set_property("sensitive", False)
        #self.buttonBox.set_property("sensitive", False)
        entry_text = user.get_text()
        contra_text = contra.get_text()
        if len(entry_text) == 0 or len(contra_text) == 0:
            post_conectar('a', 'b', 'Usuario o Contrasena Vacios')
            return
        self.buttonBox.hide()
        self.VboxInput.set_property("sensitive", False)
        self.button.hide()
        self.errorBox.hide()
        self.conectadoAnim.show()
        #if checks[0]():
        #    if checks[1]():
        #        self.__Config.userList[entry_text] = contra_text
        #    else:
        #        self.__Config.userList[entry_text] = False
        self.__queueToServer.put((self.__Okeyko.login, (entry_text, contra_text),
                                  {}, post_conectar, (checks,), {}))

    def focusUserEntry(self):
        self.userEntry.set_flags(gtk.CAN_FOCUS)
        self.userEntry.grab_focus()

class gtk_LoginImage(gtk.Image):
    def __init__(self, path=None, height=None, width=None):
        gtk.Image.__init__(self)
        self.path = path
        self.LMheight = height
        self.LMwidth = width
        if path != None:
            self.pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            self.scalePixbuf(height, width)
            self.set_from_pixbuf(self.pixbuf)

    def set_from_path(self, path, height=None, width=None):
            self.pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            self.scalePixbuf(height, width)
            self.set_from_pixbuf(self.pixbuf)

    def scalePixbuf(self, height=None, width=None):
        if height == None and width == None:
            if self.LMheight == None and self.LMwidth == None:
                return
            height = self.LMheight
            width = self.LMwidth
        if height != None and width != None:
                newWidth = width
                newHeight = height
        elif height != None:
            newHeight = height
            if round(self.pixbuf.get_height(), -1) == round(self.pixbuf.get_width(), -1):
                newWidth = height
            else:            
                newWidth = height * self.pixbuf.get_width() / self.pixbuf.get_height()
        elif width != None:
            newWidth = width
            if round(self.pixbuf.get_height(), -1) == round(self.pixbuf.get_width(), -1):
                newHeight = width
            else:            
                newHeight = width * self.pixbuf.get_height() / self.pixbuf.get_width()
        else:
            return
        self.pixbuf = self.pixbuf.scale_simple(newWidth, newHeight, gtk.gdk.INTERP_BILINEAR)
