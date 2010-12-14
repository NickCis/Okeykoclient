import gtk
import gobject

import MensajeVen
import TextField

UI = '''<ui>
    <menubar name="MenuBar">
      <menu action="Cuenta">
        <menuitem action="Desconectar"/>
        <menuitem action="Salir"/>
      </menu>
      <menu action="Mensajes">
        <menuitem action="Redact"/>
        <menuitem action="Sms"/>
      </menu>
      <menu action="Contactos">
        <menuitem action="AgeAdd"/>
        <menuitem action="Agenda"/>
      </menu>
      <menu action="Ayuda">
        <menuitem action="OkePag"/>
        <menuitem action="Pag"/>
        <separator/>
        <menuitem action="About"/>
      </menu>
    </menubar>
    <toolbar name="Toolbar">
      <toolitem action="Redact"/>
      <toolitem action="Sms"/>
      <separator/>
      <toolitem action="AgeAdd"/>
      <toolitem action="Agenda"/>
      <separator/>
      <toolitem action="Desconectar"/>
      <toolitem action="Salir"/>
    </toolbar>
    </ui>'''

class mainWindow(gtk.Window):
    ''' Clase que implementa todo lo relacionado a la interfaz grafica'''    

    __gsignals__ = {
        'redraw-done' :
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                ()),
        'redraw-disconnect' :
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                ()),
    }
    def __init__(self, Control):
    #def __init__(self, okeyko, colaOut, notificaciones=None):
        ''' Crea ventana '''
        gtk.Window.__init__(self)

        self.__Control = Control
        self.__Okeyko = Control['Okeyko']
        self.__queueToServer = Control['queueToServer']
        #Agregar notificaciones (para mensaje enviado correcto) hasta mejor idea
        #self.__Notificaciones = notificaciones
        self.__Notification = Control['Notification']
        self.__Config = Control['Config']
        iconPath = self.__Config.pathFile('theme-logo.png')
        icon = gtk.gdk.pixbuf_new_from_file_at_size(iconPath, 64, 64)
        self.set_icon_list(icon)

        # create a new window
        #self.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)        
        #self.set_position(gtk.WIN_POS_NONE)
        #self.mainWindow.set_size_request(200, 100)
        #self.set_default_size(300, 700)
        self.parse_geometry(self.__Config.glob['mainWindowGeometry'])
        self.connect("delete_event", self.showHide)
        self.set_title("Okeyko ::: Cliente")
        self.LoginWin()


    def LoginWin(self):
        if self.child:
            self.remove(self.child)
        vbox = gtk.VBox(False, 0)
        self.add(vbox)
        
        hentry = gtk.HBox(False, 0)
        vbox.pack_start(hentry, False, False, 0)
        
        labentry = gtk.Label("Usuario:")
        hentry.pack_start(labentry, True, False, 0)

        entry = gtk.Entry()
        entry.set_max_length(50)
        hentry.pack_start(entry, True, False, 0)  
        entryComp = gtk.EntryCompletion()
        entry.set_completion(entryComp)
        userListStore = gtk.ListStore (str, str)
        for a, b in self.__Config.userList:
            userListStore.append([a,'foto',])
        entryComp.set_model (userListStore)
        entryComp.set_text_column(0)

        hcontra = gtk.HBox(False, 0)
        vbox.pack_start(hcontra, False, False, 0)
        
        labcontra = gtk.Label("Password:")
        hcontra.pack_start(labcontra, True, False, 0)

        contra = gtk.Entry()
        contra.set_max_length(50)
        contra.set_visibility(False)
        hcontra.pack_start(contra, True, False, 0)

        buttonBox = gtk.VBox(False, 0)
        vbox.pack_start(buttonBox, False, False, 0)
        
        checkRe = gtk.CheckButton("Recordar Me")
        buttonBox.pack_start(checkRe, True, False, 0)
        #check.connect("toggled", self.entry_toggle_editable, entry)
        checkRe.set_active(self.__Config.glob['rememberMe'])
    
        checkRC = gtk.CheckButton("Recordar Password")
        buttonBox.pack_start(checkRC, True, False, 0)
        #check.connect("toggled", self.entry_toggle_visibility, entry)
        checkRC.set_active(self.__Config.glob['rememberMyPassword'])

        checkAL = gtk.CheckButton("Auto Login")
        buttonBox.pack_start(checkAL, True, False, 0)
        #check.connect("toggled", self.entry_toggle_visibility, entry)
        checkAL.set_active(False)

        button = gtk.Button("Conectar")
        contra.connect("activate", self.conectar, entry, contra,
            (checkRe.get_active, checkRC.get_active, checkAL.get_active))
        button.connect("clicked", self.conectar, entry, contra,
            (checkRe.get_active, checkRC.get_active, checkAL.get_active))
        vbox.pack_start(button, False, False, 0)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()

        butsalir = gtk.Button("Salir")
        butsalir.connect("clicked", self.close_application)
        vbox.pack_start(butsalir, False, False, 0)

        entry.connect('focus-out-event', self.entryUFocusOut,
            contra, (checkRe.set_active, checkRC.set_active,
            checkAL.set_active))
        entryComp.connect('match-selected', self.seterCompletionEntry,
            entry, contra, (checkRe.set_active, checkRC.set_active,
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

    def conectar(self, widget, user, contra, checks):
        ''' Callback para conectar '''
        def post_conectar(arg):
            conectado, error = self.__Okeyko.conectado()
            if conectado:
                self.redraw_ventana()
            else:
                self.child.set_property("sensitive", True)
                anim.destroy()
                label.set_text(error)

        self.child.set_property("sensitive", False)
        entry_text = user.get_text()
        contra_text = contra.get_text()
        if checks[0]():
            if checks[1]():
                self.__Config.userList[entry_text] = contra_text
            else:
                self.__Config.userList[entry_text] = False
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        label = gtk.Label("\n Conectando \n")
        label.set_use_markup(True)
        self.child.pack_start(anim, False, False, 0)
        self.child.pack_start(label, False, False, 0)
        anim.show()
        label.show()
        print "---- Conectando -----"
        self.__queueToServer.put((self.__Okeyko.login, (entry_text, contra_text),
                                  {}, post_conectar, (), {}))

    def redraw_ventana(self):
        '''Cambia la ventana despues de conectarse '''
        def launchPag(*args): #TODO
            print args[0].get_name()
            
        def aboutClient(*args): #TODO
            print "About Client"

        #Aca ya esta conectado, damos la senal que se conecto y cambia la ventana
    #    self.conectwindow = self.mainWindow.child
        self.remove(self.child)     

        vbox = gtk.VBox(False, 0)
        self.add(vbox)

        uimanager = gtk.UIManager() #Create a Uimanager instance   
             
        accelgroup = uimanager.get_accel_group() # add accelartor group
        self.add_accel_group(accelgroup)         # to the toplevel win
        
        actiongroup = gtk.ActionGroup('UIManagerMenuTool') # Create Action Group
        
        #create actions        
        # (Name, StockItem, Label, accelerator, ToolTip, CallBack)
        ageAddcb = lambda x: self.agendaAdd()
        actiongroup.add_actions([('Cuenta', None, '_Cuenta'),
                                 ('Salir', gtk.STOCK_QUIT, '_Salir', "<Ctrl><Alt>q",
                                    'Salir', self.close_application),
                                 ('Desconectar', gtk.STOCK_DISCONNECT,
                                    '_Desconectar', None, 'Desconectar Okeyko',
                                        self.disconnect),
                                 ('Mensajes', None, '_Mensajes'),
                                 ('Nada', None, '_Proximamente'),
                                 ('Contactos', None, '_Contactos'),
                                 ('AgeAdd', gtk.STOCK_ADD, '_Agregar', None, 
                                    'Agregar a Agenda', ageAddcb),
                                 ('Agenda', gtk.STOCK_DND, '_Agenda', None, 
                                    'Mostrar Agenda', self.agenda_ventana),
                                 ('Ayuda', None, '_Ayuda'),
                                 ('OkePag', gtk.STOCK_HOME, 'Pagina de _Inicio',
                                    None, None, launchPag),
                                 ('Pag', gtk.STOCK_INFO, 'Pagina del _Cliente',
                                    None, None, launchPag),
                                 ('About', gtk.STOCK_ABOUT, 'Acerca _de', None,
                                    "Borrar Mensaje", aboutClient),
                                 ('Redact', gtk.STOCK_EDIT, '_Redactar', None,
                                    'Escribir un Oky', self.redactar_ventana),
                                 ('Sms', 'okc-foky', '_OkySms', None,
                                    'Escribir un OkySms', self.Sms_ventana)])

        uimanager.insert_action_group(actiongroup, 0) #Add actiongroup to the uimanager        
        uimanager.add_ui_from_string(UI) #Add UI description         
        menubar = uimanager.get_widget('/MenuBar') #Create MenuBar
        vbox.pack_start(menubar, False)
        
        toolbar = uimanager.get_widget('/Toolbar') # Create a Toolbar+

        #for a in range(0, toolbar.get_n_items()):
        #    toolbar.get_nth_item(a).set_is_important(True)
        #toolbar.set_property('toolbar-style', gtk.TOOLBAR_BOTH)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        toolbar.set_property('icon-size', gtk.ICON_SIZE_SMALL_TOOLBAR)
        vbox.pack_start(toolbar, False)
                
        userHbox = gtk.HBox(False, 0)
        vbox.pack_start(userHbox, False, False)
        userNick, userAvatar, userEstado = self.__Okeyko.userinfo()
        uAvatar =  gtk.gdk.PixbufLoader()
        uAvatar.write(userAvatar)
        userAvatar = uAvatar.get_pixbuf()
        uAvatar.close()
        userIm = gtk.Image()
        userIm.set_from_pixbuf(userAvatar)
        userHbox.pack_start(userIm, False, False)
        userInVbox = gtk.VBox(False, 0)
        userHbox.pack_start(userInVbox, True, True)
        userNickHbox = gtk.HBox(False, 0)
        userNick = gtk.Label("@%s" % userNick)
        userNickHbox.pack_start(userNick, False, False)
        userInVbox.pack_start(userNickHbox, False, False)
        userEstE = TextField.TextField('','Contanos que estas pensando... compartelo con tus amigos!', True)
        userEstE.set_size_request(200,-1)
        if userEstado != "":
            userEstE.text = userEstado
        userEstE.connect("text-changed", self.estadoSet, userEstE._get_text )
        userInVbox.pack_start(userEstE, True, True)

        #hboxmenu = gtk.HBox(False, 0)
        ##vbox.add(hboxmenu)
        #vbox.pack_start(hboxmenu, False, False)
        #butredac = gtk.Button("Redactar")
        #hboxmenu.pack_start(butredac, True, True)
        #butredac.connect("clicked", self.redactar_ventana)
        #butagen = gtk.Button("Agenda")
        #hboxmenu.pack_start(butagen, True, True)
        #butagen.connect("clicked", self.agenda_ventana)
        #butsalir = gtk.Button("Salir")
        #hboxmenu.pack_start(butsalir, True, True)
        #butsalir.connect("clicked", self.close_application)

        # Crea sistema de tabs
        tabsys = gtk.Notebook()
        tabsys.set_tab_pos(gtk.POS_TOP)
        tabsys.set_size_request(300,-1)
        vbox.pack_start(tabsys, True, True)

        #Anade tabs        
        tab1name = "Recividos"
        tab2name = "Enviados"

        frame1 = gtk.Frame()
        frame2 = gtk.Frame()

        tabsys.append_page(frame1, gtk.Label(tab1name))
        tabsys.append_page(frame2, gtk.Label(tab2name))

        sw = gtk.ScrolledWindow()
        #sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_policy(gtk.POLICY_NEVER , gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)
        #vbox.pack_start(sw, True, True)

        inboxVbox = gtk.VBox()        
        inboxVbox.pack_start(sw, True, True)

        inboxMoreBut = gtk.Button("Anteriores Mensajes")
        inboxMoreBut.connect("clicked", self.getMoreInbox)
        inboxVbox.pack_end(inboxMoreBut, False)

        frame1.add(inboxVbox)

        sw2 = gtk.ScrolledWindow()
        #sw2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw2.set_policy(gtk.POLICY_NEVER , gtk.POLICY_AUTOMATIC)
        sw2.set_shadow_type(gtk.SHADOW_IN)
        #vbox.pack_start(sw, True, True)       

        outboxVbox = gtk.VBox()        
        outboxVbox.pack_start(sw2, True, True)
        
        outboxMoreBut = gtk.Button("Anteriores Mensajes")
        outboxMoreBut.connect("clicked", self.getMoreOutbox)
        outboxVbox.pack_end(outboxMoreBut, False)        

        frame2.add(outboxVbox)
        
        # === Recividos
        #Crear el ListStore 
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido, fav
        #self.inbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, gtk.gdk.Pixbuf, int, int)
        self.inbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, int, int, bool)
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        mensajeslist = gtk.TreeView(self.inbox_store)
        mensajeslist.set_headers_visible(False)
        mensajeslist.connect("row-activated", self.mostrarmensaje)
        mensajeslist.connect("button_press_event", self.popUpMenMenu, 'in')
        
        #self.mListS2N = mensajeslist.scroll_to_cell #TODO: fix scrolling
        
        #self.inbox_store.connect('row-inserted', self.scroll2N, 
        #                         mensajeslist.scroll_to_cell)

        #crear Column
        #columnPix = gtk.TreeViewColumn("Avatar")
        #columnPix.set_max_width(24)
        #columnText = gtk.TreeViewColumn("Mensaje")
        columnPT = gtk.TreeViewColumn('PT')

        #agrega las Column al TreeView
        #mensajeslist.append_column(columnPix)
        #mensajeslist.append_column(columnText)
        mensajeslist.append_column(columnPT)

        #crear cellrender para mostrar data
        cellPixbuf = gtk.CellRendererPixbuf()
        cellPixbuf.set_property('cell-background', 'orange')
        cellText = gtk.CellRendererText()
        cellText.set_property('cell-background', 'orange')

        #anade las celdas a las columnas
        #columnPix.pack_start(cellPixbuf, False)
        #columnText.pack_start(cellText, False)
        columnPT.pack_start(cellPixbuf, False)
        columnPT.pack_start(cellText, True)
        
        #anadir atributos a las columns
        #columnPix.set_attributes(cellPixbuf, pixbuf=0)
        #columnText.set_attributes(cellText, markup=1,
        #                          cell_background_set=9)
        columnPT.set_attributes(cellPixbuf, pixbuf=0,
                                  cell_background_set=9)
        columnPT.set_attributes(cellText, markup=1,
                                  cell_background_set=9)

        #columnPix.set_sort_column_id(0)
        #columnText.set_sort_column_id(1)
        columnPT.set_sort_column_id(0)

        sw.add(mensajeslist)

        # == Enviados
        #Crear el ListStore
        # muestra_avatar, muestra_mensaje, de, hora, mensaje, okid, avatar, leido
        #self.outbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, gtk.gdk.Pixbuf, int)
        self.outbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, int, bool)
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        enviadoslist = gtk.TreeView(self.outbox_store)
        enviadoslist.set_headers_visible(False)
        enviadoslist.connect("row-activated", self.mostrarenviado)
        enviadoslist.connect("button_press_event", self.popUpMenMenu, 'out')

        #crear Column
        EcolumnPix = gtk.TreeViewColumn("Avatar")
        EcolumnText = gtk.TreeViewColumn("Mensaje")

        #agrega las Column al TreeView
        enviadoslist.append_column(EcolumnPix)
        enviadoslist.append_column(EcolumnText)

        #crear cellrender para mostrar data
        EcellPixbuf = gtk.CellRendererPixbuf()
        EcellText = gtk.CellRendererText()
        
        #anade las celdas a las columnas
        EcolumnPix.pack_start(EcellPixbuf, False)
        EcolumnText.pack_start(EcellText, False)        
        
        #anadir atributos a las columns
        EcolumnPix.set_attributes(EcellPixbuf, pixbuf=0)
        EcolumnText.set_attributes(EcellText, markup=1)

        EcolumnPix.set_sort_column_id(0)
        EcolumnText.set_sort_column_id(1)

        sw2.add(enviadoslist)

        self.show_all()

        self.emit('redraw-done')

        #Agregar los textos al ListStore (al final para no colgar la interfaz)
        #self.__men_list(self.mensajes_store, self.__Okeyko.bandeja())
        #self.__env_list(self.enviados_store, self.__Okeyko.salida())

    def scroll2N(self, treemodel, path, iter, scrollFunc):
        scrollFunc(path)        

    def popUpMenMenu(self, widget, event, box):
        if event.type == gtk.gdk.BUTTON_PRESS: # Single click
            if event.button == 3: # Right Click - Show popup
                self.popMenuBuilder(widget, box).popup(None, None, None,
                    event.button, event.time)

    def popMenuBuilder(self, treeView, box):
        menu = gtk.Menu()
        if box == 'in':
            labRes = 'Responder'
            res = 'res'
            favs = True
            bor = 'borIn'
        else:
            labRes = 'Reenviar'
            res = 'reenv'
            favs = False
            bor = 'borOut'
        menuItemRes = gtk.MenuItem(labRes)
        menuItemRes.connect('activate', self.popMenuCallb, res, treeView)
        menu.append(menuItemRes)

        if favs:
            menuItemFav = gtk.MenuItem("Favoritos")
            menuItemFav.connect('activate', self.popMenuCallb, 'fav', treeView)
            menu.append(menuItemFav)

        menuItemAg = gtk.MenuItem("Agegar a Agenda")
        menuItemAg.connect('activate', self.popMenuCallb, 'ag', treeView)
        menu.append(menuItemAg)

        menuItemBor = gtk.ImageMenuItem( gtk.STOCK_DELETE )
        menuItemBor.connect('activate', self.popMenuCallb, bor, treeView)
        menu.append(menuItemBor)

        menu.show_all()
        return menu

    def popMenuCallb(self, menuitem, action, treeView):
        listStore, lIter = treeView.get_selection().get_selected()
        name, men, Oid = listStore.get(lIter, 2, 4, 5)    
        if action == "res":
            self.redactar_ventana(None, name)
        elif action == "reenv":
            self.redactar_ventana(None, name, men)
        elif action == "fav":
            pass
        elif action == "ag":
            self.agendaAdd(name)
        elif action == "borIn":
            self.borInbox(Oid)
        elif action == "borOut":
            self.borOutbox(Oid)

    def borInbox(self, Oid):
        for row in self.inbox_store:
            if str(row[5]) == str(Oid):
                self.inbox_store.remove(row.iter)
                break
        self.__Okeyko.inbox_bor(Oid)

    def borOutbox(self, Oid):
        for row in self.outbox_store:
            if str(row[5]) == str(Oid):
                self.outbox_store.remove(row.iter)
                break
        self.__Okeyko.outbox_bor(Oid)

    def getMoreInbox(self, button):    
        def getMoreInboxPost(mensajes):
            self.__menAdd(self.inbox_store, mensajes, False)
            button.set_property("sensitive", True)
            button.set_property("image", None)
            button.set_label("Anteriores Mensajes")
    
        button.set_property("sensitive", False)
        self.__queueToServer.put((self.__Okeyko.getMoreInbox, (), {},
                                  getMoreInboxPost, (), {}))
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        button.set_image(anim)
        anim.show()

    def getMoreOutbox(self, button):
        def getMoreOutboxPost(mensajes):
            self.__menAdd(self.outbox_store, mensajes, False)
            button.set_property("sensitive", True)
            button.set_property('image', None)
            button.set_label("Anteriores Mensajes")

        button.set_property("sensitive", False)
        self.__queueToServer.put((self.__Okeyko.getMoreOutbox, (), {},
                                  getMoreOutboxPost, (), {}))
        button.set_label("Cargando")
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        button.set_image(anim)
        anim.show()

    def set_inbox(self, mensajes):
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido, fav
        self.inbox_store.clear()
        mensajes.reverse()
        #self.__menAdd(self.inbox_store, mensajes, False)
        self.__menAdd(self.inbox_store, mensajes, True)
        
    def new_inbox(self, mensajes):
        mensajes.reverse()
        self.__menAdd(self.inbox_store, mensajes, True)
        pass
        
    def set_outbox(self, mensajes):
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido
        self.outbox_store.clear()
        self.__menAdd(self.outbox_store, mensajes, False)
        
    def new_outbox(self, mensajes):
        mensajes.reverse()
        self.__menAdd(self.outbox_store, mensajes, True)
        pass

    def __menAdd(self, store, mensajes, pre=False):
        '''Agrega los mensajes al store especificado'''

        for mensaje in mensajes:
            texto = '%s' +\
                '\n<span size="small" foreground="#A4A4A4">%s</span>'
            texto = texto % (mensaje[0], mensaje[2].replace("\n",""))
            if str(mensaje[5]) == "0": # Mensaje Nuevo
                estado = self.__Config.pathFile("theme-new.png")
                #texto = '<span background="#F7BE81">bla%s</span>' % texto
                nuevo = True
            elif str(mensaje[5]) == "1": # Leido Movil
                estado = self.__Config.pathFile("theme-leido_cel.png")
                nuevo = False
            else: # Leido PC
                estado = self.__Config.pathFile("theme-leido_pc.png")
                nuevo = False
            #avatar =  gtk.gdk.PixbufLoader()
            #avatar.write(self.__Config.avatarLoad(mensaje[4])[1])
            #avatarG = avatar.get_pixbuf()
            #avatar.close()
            avatarG = gtk.gdk.pixbuf_new_from_file(
                self.__Config.avatarLoad(mensaje[4],False)[1])
            avatarG_w = avatarG.get_width()
            avatarG_h = avatarG.get_height()
            avatarM_h = 40 * avatarG_h / avatarG_w
            avatarM = avatarG.scale_simple(40,avatarM_h,gtk.gdk.INTERP_NEAREST)
            #gtk.gdk.threads_enter()
            avatarM = self.add_status(avatarM, estado, avatarM.get_width() - 15, avatarM.get_height() - 15)
            #gtk.gdk.threads_leave()
            row = list([avatarM, texto])
            for c in mensaje:
                row.append(c)
            row.append(nuevo)
            if pre:
                store.prepend(row)
            else:
                store.append(row)
        return

    def add_status(self, pixbuf, pathAdpixbuf, posx, posy):
        '''Agrega la fotito de donde se leyo (cel,pc,no)'''
        adpixbuf = gtk.gdk.pixbuf_new_from_file_at_size(pathAdpixbuf, 15, 15)
        pixmap,_ = pixbuf.render_pixmap_and_mask()
        gc = pixmap.new_gc()
        pixmap.draw_pixbuf(gc, adpixbuf, 0, 0, posx, posy)
        return pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, -1, -1)

    def estadoSet(self, widget, estado, getText, *args, **kargs):
        self.__Okeyko.estadoSet(getText)

    def redactar_ventana(self, widget=None, destinatario=None, men=None, data=None):
        ''' Callback que crea la ventana para redactar mensajes'''
        redactar = gtk.Dialog("Redactar", self)
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        labpara = gtk.Label("Para:")
        hbox.pack_start(labpara)        
        labpara.show()
        para = gtk.Entry()        
        autocompletado = gtk.EntryCompletion ()
        para.set_completion(autocompletado)
        contactos_store = gtk.ListStore (gobject.TYPE_STRING)
        for cont in self.__Okeyko.agenda_lista(True):
            contactos_store.append([cont,])
        autocompletado.set_model (contactos_store)
        autocompletado.set_text_column (0)       
        if destinatario != None: para.set_text(destinatario)
        hbox.pack_start(para)
        para.show()
        enviar = gtk.Button("Enviar")
        hbox.pack_end(enviar)        
        enviar.show()         
        redactar.vbox.pack_start(hbox)
        hbox.show()
        labmen = gtk.Label("Mensaje:")
        redactar.vbox.pack_start(labmen)
        labmen.show()
        mensaje = gtk.TextView()
        mensaje.set_wrap_mode(gtk.WRAP_WORD)
        mensaje.set_accepts_tab(False)
        mensaje.set_left_margin(6)
        mensaje.set_right_margin(6)
        mensaje.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        mensaje.set_size_request(275,100)
        if men != None:
            mensaje.get_buffer().set_text(men)
        redactar.vbox.pack_start(mensaje)
        mensaje.show()
        numlabel = gtk.Label()
        redactar.vbox.pack_start(numlabel)
        numlabel.show()
        redactar.show()
        enviar.connect("clicked", self.mandarmensaje, redactar, para, mensaje)
        mensaje.get_buffer().connect("changed", self.actnumlabel, numlabel)

    def Sms_ventana(self, widget=None, destinatario=None, men=None, data=None):
        ''' Callback que crea la ventana para redactar mensajes'''

        def mandarSms(*args, **kargs):
            '''Callback para mandar mensaje '''
            def post_mandarmensaje(arg):
                bol, error = arg
                if bol:        
                    tit = "OkySms Enviado!"
                    redactar.destroy()
                else:
                    redactar.child.set_property('sensitive', True)
                    tit = "Error Mandando OkySms"
                    redactar.vbox.pack_start(gtk.Label(error))
                    uCaptcha =  gtk.gdk.PixbufLoader()
                    uCaptcha.write(self.__Okeyko.captcha())
                    Captcha.set_from_pixbuf(uCaptcha.get_pixbuf())
                    uCaptcha.close()
                    redactar.show_all()
                    anim.destroy()
                self.__Notification.newNotification(tit)
                return
    
            redactar.child.set_property('sensitive', False)
            CBHbox = gtk.HBox()
            PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
            anim = gtk.Image()
            anim.set_from_animation(PBanim)
            CBHbox.pack_start(anim, False, False, 0)
            CBHbox.pack_start(gtk.Label("Enviando"), False, False, 0)
            redactar.vbox.pack_start(CBHbox, False, False, 0)
            redactar.show_all()
            celpara = para.get_text()
            celpara2 = para2.get_text()
            CbPara = (celpara, celpara2)
            CbCaptcha = codigo.get_text()
            textmensaje = mensaje.get_buffer().get_text(\
                        mensaje.get_buffer().get_start_iter(),\
                        mensaje.get_buffer().get_end_iter())
            self.__queueToServer.put((self.__Okeyko.enviarSms, (CbPara, textmensaje, CbCaptcha),
                                      {}, post_mandarmensaje, (), {}))
            return        
        
        redactar = gtk.Dialog("OkySms", self)
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        labpara = gtk.Label("Para:")
        hbox.pack_start(labpara)        
        #labpara.show()
        para = gtk.Entry()
        hbox.pack_start(para)
        para2 = gtk.Entry()
        hbox.pack_start(para2)
        enviar = gtk.Button("Enviar")
        hbox.pack_end(enviar)        
        #enviar.show()         
        redactar.vbox.pack_start(hbox)
        #hbox.show()
        labmen = gtk.Label("Mensaje:")
        redactar.vbox.pack_start(labmen)
        #labmen.show()
        mensaje = gtk.TextView()
        mensaje.set_wrap_mode(gtk.WRAP_WORD)
        mensaje.set_accepts_tab(False)
        mensaje.set_left_margin(6)
        mensaje.set_right_margin(6)
        mensaje.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        mensaje.set_size_request(275,100)
        if men != None:
            mensaje.get_buffer().set_text(men)
        redactar.vbox.pack_start(mensaje)
        #mensaje.show()
        numlabel = gtk.Label()
        redactar.vbox.pack_start(numlabel)
        uCaptcha =  gtk.gdk.PixbufLoader()
        uCaptcha.write(self.__Okeyko.captcha())
        Captcha = gtk.image_new_from_pixbuf(uCaptcha.get_pixbuf())
        uCaptcha.close()
        redactar.vbox.pack_start(Captcha)
        codigo = gtk.Entry()
        redactar.vbox.pack_start(codigo)
        redactar.show_all()
        enviar.connect("clicked", mandarSms)
        mensaje.get_buffer().connect("changed", self.actnumlabel, numlabel)
    
    def actnumlabel(self, wid, numlabel):
        #length = len(wid.get_text(wid.get_start_iter(), wid.get_end_iter())
        length = wid.get_char_count()
        numlabel.set_text("%s" % length)

    def mandarmensaje(self, widget, alert, widpara, widmensaje):
        '''Callback para mandar mensaje '''
        def post_mandarmensaje(arg):
            bol, error = arg
            if bol:        
                tit = "Mensaje Enviado!"
                window.destroy()
            else:
                alert.child.set_property('sensitive', True)
                tit = "Error Mandando Mensaje"
                label = gtk.Label(error)
                container.pack_start(label)
                label.show()
            self.__Notification.newNotification(tit)
            return

        alert.child.set_property('sensitive', False)
        Hbox = gtk.HBox()
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.pathFile("theme-loading.gif"))
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        label = gtk.Label("Enviando")
        Hbox.pack_start(anim, False, False, 0)
        Hbox.pack_start(label, False, False, 0)
        widget.parent.parent.pack_start(Hbox, False, False, 0)
        widget.parent.parent.show_all()
        para = widpara.get_text()
        mensaje = widmensaje.get_buffer().get_text(\
                    widmensaje.get_buffer().get_start_iter(),\
                    widmensaje.get_buffer().get_end_iter())
        container = widget.get_parent().get_parent()
        window = widget.get_parent().get_parent().get_parent()
        self.__queueToServer.put((self.__Okeyko.enviar_mensaje, (para, mensaje),
                                  {}, post_mandarmensaje, (), {}))
        return

    def agendaAdd(self, nom=None, desc=None):
        '''Alert para agregar a la agenda'''
        agenda = gtk.Dialog("Agenda", self)
        Hbox1 = gtk.HBox()
        label1 = gtk.Label("Usuario")
        entry1 = gtk.Entry()
        if nom != None:
            entry1.set_text(nom)
        Hbox1.pack_start(label1)
        Hbox1.pack_start(entry1)
        Hbox2 = gtk.HBox()
        label2 = gtk.Label("Descripcion")
        entry2 = gtk.Entry()
        if desc != None:
            entry2.set_text(desc)
        Hbox2.pack_start(label2)
        Hbox2.pack_start(entry2)
        button = gtk.Button('Agregar')
        callb = lambda x: self.__agendaAdd(u=entry1.get_text(),
                                           d=entry2.get_text(),
                                           w=agenda)
        #button.connect('clicked', self.__agendaAdd, u=entry1.get_text(),
        #                                            d=entry2.get_text())
        button.connect('clicked', callb)
        agenda.vbox.pack_start(Hbox1)
        agenda.vbox.pack_start(Hbox2)
        agenda.vbox.pack_start(button)
        agenda.show_all()

    def __agendaAdd(self, *args, **kargs):
        def post(*args):
            print args
            if r:
                w.destroy()
                n("Agregado correctamente")
            else:
                w.vbox.pack_start(gtk.Label('Error'))
        u = kargs['u']
        d = kargs['d']
        w = kargs['w']
        n = self.__Notification.newNotification
        self.__queueToServer.put((self.__Okeyko.agendaAdd, (u, d), {},
                                  post, (w, n), {}))        
        
    def agenda_ventana(self, widget=None, data=None):
        '''Creador de la ventana de agenda'''
        agenda = gtk.Dialog("Agenda", self)
        vbox = gtk.VBox()
        
        #Crear el ListStore
        agenda_store = gtk.ListStore(str, str, str, str, str)        
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        agendaTreeView = gtk.TreeView(agenda_store)
        agendaTreeView.set_rules_hint(True)
        agendaTreeView.connect("row-activated", self.click_agenda)

        #crear Column
        #columnText0 = gtk.TreeViewColumn("Avatar")
        columnText1 = gtk.TreeViewColumn("Nombre")
        columnText2 = gtk.TreeViewColumn("Descripcion")
        columnBut = gtk.TreeViewColumn("Borrar")
        columnBut2 = gtk.TreeViewColumn("Bloquear")

        #agrega las Column al TreeView
        #agendaTreeView.append_column(columnText0)
        agendaTreeView.append_column(columnText1)
        agendaTreeView.append_column(columnText2)
        agendaTreeView.append_column(columnBut)
        agendaTreeView.append_column(columnBut2)

        #crear cellrender para mostrar data
        cellText0 = gtk.CellRendererText()
        cellText1 = gtk.CellRendererText()
        cellText2 = gtk.CellRendererText()
        cellPix = gtk.CellRendererPixbuf()
        cellPix2 = gtk.CellRendererPixbuf()

        #anade las celdas a las columnas
        #columnText0.pack_start(cellText0, False)
        columnText1.pack_start(cellText1, False)
        columnText2.pack_start(cellText2, False)
        columnBut.pack_start(cellPix, False)
        columnBut2.pack_start(cellPix2, False)
        
        #anadir atributos a las columns
        #columnText0.set_attributes(cellText0, text=0)
        columnText1.set_attributes(cellText1, text=1)
        columnText2.set_attributes(cellText2, text=2)
        columnBut.set_attributes(cellPix, stock_id=3)
        columnBut2.set_attributes(cellPix2, stock_id=4)

        #columnText0.set_sort_column_id(0)
        columnText1.set_sort_column_id(0)
        columnText2.set_sort_column_id(1)
        columnBut.set_sort_column_id(2)
        columnBut2.set_sort_column_id(3)

        agenda.vbox.pack_start(agendaTreeView, True, True, 0)

        agenda.show_all()
        #self.__queueToServer.put((self.__Okeyko.agenda_lista, (), {}, \
        #                    self.agenda_ventana_add, (agenda_store), {}))        
        self.agenda_ventana_add(self.__Okeyko.agenda_lista(), agenda_store)
        return

    def agenda_ventana_add(self, arg, store):
        #print arg, store
        contactos = arg
        for contacto in contactos:
            nombre = contacto[0]
            desc = contacto[1]
            uId = contacto[2]
            #imgavatar = self.okeyko.pagina(mensaje[4])
            #avatar =  gtk.gdk.PixbufLoader()
            #avatar.write(imgavatar)        
            #store.append([avatar.get_pixbuf(), nombre, desc])
            store.append([uId, nombre, desc, gtk.STOCK_DELETE, gtk.STOCK_STOP])
        #avatar.close()
        return

    def click_agenda(self, widget, row, col):
        model = widget.get_model()
        colT = col.get_title()
        if colT == "Borrar":
            pass
        elif colT == "Bloquear":
            pass
        else:
            self.redactar_ventana( None, model[row][1])

    def mostrarmensaje(self, widget, row, col):
        model = widget.get_model()
        MensajeVen.MensajeVen(model, row, self.__Control)
        if model[row][9]:
            self.__queueToServer.put((self.__Okeyko.set_leido, (model[row][5],),\
                                {}, self.Nulo, (), {}))
            #texto = model[row][1].replace(" background=\"#F7BE81\"","")
            #pixbuf = self.add_status(model[row][0], gtk.gdk.pixbuf_new_from_file(\
            #            self.__Config.pathFile("theme-leido_pc.png")),\
            #            model[row][0].get_width() - 15,\
            #            model[row][0].get_height() - 15)
            pixbuf = self.add_status(model[row][0], self.__Config.pathFile(
                        "theme-leido_pc.png"),
                        model[row][0].get_width() - 15,
                        model[row][0].get_height() - 15)
            model.set_value(model.get_iter_from_string("%s:0" % (row)), 0, pixbuf)
            #model.set_value(model.get_iter_from_string("%s:1" % (row)), 1,texto)
            model.set_value(model.get_iter_from_string("%s:9" % (row)), 9, False)

    def mostrarenviado(self, widget, row, col):
        model = widget.get_model()
        MensajeVen.EnviadoVen(model, row, self.__Control)        

    def Nulo(self, *args, **kwargs):
        return

    def blink(self):
        ''' Hace titilar al tray icon '''
        self.tray.tray.set_blinking(True)

    def close_application(self, widget, event=None, data=None):
        self.saveMainWindowGeometry()
        gtk.main_quit()
        exit()

    def saveMainWindowGeometry(self):
        xPos, yPos = self.get_position()
        wWin, hWin = self.get_size()
        mainWinGeometry = "%sx%s+%s+%s" % (wWin, hWin, xPos, yPos)
        if self.__Config.glob['mainWindowGeometry'] != mainWinGeometry:
            self.__Config.glob['mainWindowGeometry'] = mainWinGeometry

    def showHide(self, widget=None, *args):
        '''Show or hide the main window'''
#        self.tray.set_blinking(False)
        if self.flags() & gtk.VISIBLE:
            self.saveMainWindowGeometry()
            self.hide()
        else:
            self.deiconify()
            self.show()
        return True

    def disconnect(self, *args, **kargs):
        self.LoginWin()
        self.emit('redraw-disconnect')
