import gtk
import gobject

import MensajeVen
import TextField

class mainWindow(gtk.Window):
    ''' Clase que implementa todo lo relacionado a la interfaz grafica'''    

    __gsignals__ = {
        'redraw-done' :
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                ()),
    }
    def __init__(self, Control):
    #def __init__(self, okeyko, colaOut, notificaciones=None):
        ''' Crea ventana '''
        self.__Control = Control
        self.__Okeyko = Control['Okeyko']
        self.__queueToServer = Control['queueToServer']
        #Agregar notificaciones (para mensaje enviado correcto) hasta mejor idea
        #self.__Notificaciones = notificaciones
        self.__Notification = Control['Notification']
        self.__Config = Control['Config']

        # create a new window
        #self.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        gtk.Window.__init__(self)
        self.set_position(gtk.WIN_POS_NONE)
        self.connect("delete_event", self.showHide)
        #self.mainWindow.set_size_request(200, 100)
        self.set_default_size(300, 700)
        self.set_title("Okeyko ::: Cliente")
        
        vbox = gtk.VBox(False, 0)
        self.add(vbox)
        
        hentry = gtk.HBox(False, 0)
        vbox.pack_start(hentry, False, False, 0)
        
        labentry = gtk.Label("Usuario:")
        hentry.pack_start(labentry, True, False, 0)

        entry = gtk.Entry()
        entry.set_max_length(50)
        hentry.pack_start(entry, True, False, 0)        

        hcontra = gtk.HBox(False, 0)
        vbox.pack_start(hcontra, False, False, 0)
        
        labcontra = gtk.Label("Password:")
        hcontra.pack_start(labcontra, True, False, 0)

        contra = gtk.Entry()
        contra.set_max_length(50)
        contra.set_visibility(False)
        contra.connect("activate", self.conectar, entry, contra)
        hcontra.pack_start(contra, True, False, 0)

        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)
                          
        check = gtk.CheckButton("Editable")
        hbox.pack_start(check, True, False, 0)
        #check.connect("toggled", self.entry_toggle_editable, entry)
        check.set_active(True)
    
        check = gtk.CheckButton("Visible")
        hbox.pack_start(check, True, False, 0)
        #check.connect("toggled", self.entry_toggle_visibility, entry)
        check.set_active(True)

        button = gtk.Button("Conectar")
        button.connect("clicked", self.conectar, entry, contra)
        vbox.pack_start(button, False, False, 0)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()

        butsalir = gtk.Button("Salir")
        butsalir.connect("clicked", self.close_application)
        vbox.pack_start(butsalir, False, False, 0)

        self.show_all()

    def conectar(self, widget, user, contra):
        ''' Callback para conectar '''
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.THEME_PATH + "loading.gif")
        anim = gtk.Image()
        anim.set_from_animation(PBanim)
        label = gtk.Label("\n Conectando \n")
        label.set_use_markup(True)
        self.child.pack_start(anim, False, False, 0)
        self.child.pack_start(label, False, False, 0)
        anim.show()
        label.show()
        entry_text = user.get_text()
        contra_text = contra.get_text()
        print "---- Conectando -----"
        self.__queueToServer.put((self.__Okeyko.login, (entry_text, contra_text), {}, self.post_conectar, (anim, label), {}))

    def post_conectar(self, arg, arg2):
        conectado, error = self.__Okeyko.conectado()
        if conectado:
            self.redraw_ventana()
        else:
            anim = arg2[0]
            anim.destroy()
            label = arg2[1]
            label.set_text(error)

    def showHide(self, widget=None, *args):
        '''Show or hide the main window'''
        
#        self.tray.set_blinking(False)

        if self.flags() & gtk.VISIBLE:
            self.hide()
        else:
            self.deiconify()
            self.show()
        return True

    def redraw_ventana(self):
        '''Cambia la ventana despues de conectarse '''
        #Aca ya esta conectado, damos la senal que se conecto y cambia la ventana
    #    self.conectwindow = self.mainWindow.child
        self.remove(self.child)     

        vbox = gtk.VBox(False, 0)
        self.add(vbox)
        
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
        userEstE = TextField.TextField('','', False)
        userEstE.text = userEstado
        userEstE.connect("text-changed", self.estadoSet )
        userInVbox.pack_start(userEstE, True, True)

        hboxmenu = gtk.HBox(False, 0)
        #vbox.add(hboxmenu)
        vbox.pack_start(hboxmenu, False, False)

        butredac = gtk.Button("Redactar")
        hboxmenu.pack_start(butredac, True, True)
        butredac.connect("clicked", self.redactar_ventana)

        butagen = gtk.Button("Agenda")
        hboxmenu.pack_start(butagen, True, True)
        butagen.connect("clicked", self.agenda_ventana)

        butsalir = gtk.Button("Salir")
        hboxmenu.pack_start(butsalir, True, True)
        butsalir.connect("clicked", self.close_application)

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
        frame1.add(sw)

        sw2 = gtk.ScrolledWindow()
        #sw2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw2.set_policy(gtk.POLICY_NEVER , gtk.POLICY_AUTOMATIC)
        sw2.set_shadow_type(gtk.SHADOW_IN)
        #vbox.pack_start(sw, True, True)
        frame2.add(sw2)
        
        # === Recividos
        #Crear el ListStore 
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido, fav
        #self.inbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, gtk.gdk.Pixbuf, int, int)
        self.inbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, int, int)
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        mensajeslist = gtk.TreeView(self.inbox_store)
        mensajeslist.set_headers_visible(False)
        mensajeslist.connect("row-activated", self.mostrarmensaje)

        #crear Column
        columnPix = gtk.TreeViewColumn("Avatar")
        #columnPix.set_max_width(24)
        columnText = gtk.TreeViewColumn("Mensaje")

        #agrega las Column al TreeView
        mensajeslist.append_column(columnPix)
        mensajeslist.append_column(columnText)

        #crear cellrender para mostrar data
        cellPixbuf = gtk.CellRendererPixbuf()
        cellText = gtk.CellRendererText()

        #anade las celdas a las columnas
        columnPix.pack_start(cellPixbuf, False)
        columnText.pack_start(cellText, False)
        
        #anadir atributos a las columns
        columnPix.set_attributes(cellPixbuf, pixbuf=0)
        columnText.set_attributes(cellText, markup=1)

        columnPix.set_sort_column_id(0)
        columnText.set_sort_column_id(1)

        sw.add(mensajeslist)

        # == Enviados
        #Crear el ListStore
        # muestra_avatar, muestra_mensaje, de, hora, mensaje, okid, avatar, leido
        #self.outbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, gtk.gdk.Pixbuf, int)
        self.outbox_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, int)
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        enviadoslist = gtk.TreeView(self.outbox_store)
        enviadoslist.set_headers_visible(False)        

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


    def set_inbox(self, mensajes):
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido, fav
        self.inbox_store.clear()
        self.__menAdd(self.inbox_store, mensajes, False)
        
    def new_inbox(self, mensajes):
        pass
        
    def set_outbox(self, mensajes):
        # muestra_avatar, muestra_texto, de, hora, mensaje, Oik, avatar, leido
        self.outbox_store.clear()
        self.__menAdd(self.outbox_store, mensajes, False)
        
    def new_outbox(self, mensajes):
        pass

    def __menAdd(self, store, mensajes, pre=False):
        '''Agrega los mensajes al store especificado'''
        imgcache = {"estado0" : gtk.gdk.pixbuf_new_from_file(\
                        self.__Config.THEME_PATH + "new.png"),
                    "estado1" : gtk.gdk.pixbuf_new_from_file(\
                        self.__Config.THEME_PATH + "leido_pc.png"),
                    "estado2" : gtk.gdk.pixbuf_new_from_file(\
                        self.__Config.THEME_PATH + "leido_cel.png")}
        for mensaje in mensajes:            
            texto = '%s' +\
                '\n<span size="small" foreground="#A4A4A4">%s</span>'
            texto = texto % (mensaje[0], mensaje[2].replace("\n",""))
            if mensaje[5] == "0": # Mensaje Nuevo
                estado = imgcache["estado0"]
                texto = '<span background="#F7BE81">%s</span>' % texto
            elif mensaje[5] == "1": # Leido Pc
                estado = imgcache["estado1"]
            else: # Leido Cel
                estado = imgcache["estado2"]
            avatar =  gtk.gdk.PixbufLoader()
            avatar.write(mensaje[4])
            avatarG = avatar.get_pixbuf()
            avatar.close()
            avatarG_w = avatarG.get_width()
            avatarG_h = avatarG.get_height()
            avatarM_h = 40 * avatarG_h / avatarG_w
            avatarM = avatarG.scale_simple(40,avatarM_h,gtk.gdk.INTERP_NEAREST)
            gtk.gdk.threads_enter()
            #print estado
            avatarM = self.add_status(avatarM, estado, avatarM.get_width() - 15, avatarM.get_height() - 15)
            gtk.gdk.threads_leave()
            row = [avatarM, texto]
            for c in mensaje:
                row.append(c)
            if pre:
                store.prepend(row)
            else:
                store.append(row)
        return
        
    def add_status(self, pixbuf, adpixbuf, posx, posy):
        pixmap,_ = pixbuf.render_pixmap_and_mask()
        gc = pixmap.new_gc()
        pixmap.draw_pixbuf(gc, adpixbuf, 0, 0, posx, posy)
        return pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, -1, -1)
        
    def estadoSet(self, widget, estado, *args, **kargs):
        self.__Okeyko.estadoSet(estado)

    def redactar_ventana(self, widget=None, destinatario=None, data=None):
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
        mensaje.set_left_margin(6)
        mensaje.set_right_margin(6)
        mensaje.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        mensaje.set_size_request(275,100)
        redactar.vbox.pack_start(mensaje)
        mensaje.show()
        numlabel = gtk.Label()
        redactar.vbox.pack_start(numlabel)
        numlabel.show()
        redactar.show()
        enviar.connect("clicked", self.mandarmensaje, para, mensaje)
        mensaje.get_buffer().connect("changed", self.actnumlabel, numlabel)
    
    def actnumlabel(self, wid, numlabel):
        #length = len(wid.get_text(wid.get_start_iter(), wid.get_end_iter())
        length = wid.get_char_count()
        numlabel.set_text("%s" % length)

    def mandarmensaje(self, widget, widpara, widmensaje):
        '''Callback para mandar mensaje '''
        Hbox = gtk.HBox()
        PBanim = gtk.gdk.PixbufAnimation(self.__Config.THEME_PATH + "loading.gif")
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
        self.__queueToServer.put((self.__Okeyko.enviar_mensaje, (para, mensaje), {}, self.post_mandarmensaje, (widget.get_parent().get_parent(), widget.get_parent().get_parent().get_parent()), {}))
        return

    def post_mandarmensaje(self, arg, arg2):
        bol, error = arg
        container, window = arg2
        if bol:        
            tit = "Mensaje Enviado!"
            window.destroy()
        else:
            tit = "Error Mandando Mensaje"
            label = gtk.Label(error)
            container.pack_start(label)
            label.show()
        self.__Notification.newNotification(tit)
        return

    def agenda_ventana(self, widget, data=None):
        '''Creador de la ventana de agenda'''
        agenda = gtk.Dialog("Agenda", self)
        vbox = gtk.VBox()
        
        #Crear el ListStore
        agenda_store = gtk.ListStore(str, str, str)        
        
        #crear TreeView usando el ListStore y setear sus caracteristicas
        agendaTreeView = gtk.TreeView(agenda_store)
        agendaTreeView.set_rules_hint(True)
        agendaTreeView.connect("row-activated", self.click_agenda)

        #crear Column
        columnText0 = gtk.TreeViewColumn("Avatar")
        columnText1 = gtk.TreeViewColumn("Nombre")
        columnText2 = gtk.TreeViewColumn("Descripcion")

        #agrega las Column al TreeView
        #agendaTreeView.append_column(columnText0)
        agendaTreeView.append_column(columnText1)
        agendaTreeView.append_column(columnText2)

        #crear cellrender para mostrar data
        cellText0 = gtk.CellRendererText()
        cellText1 = gtk.CellRendererText()
        cellText2 = gtk.CellRendererText()

        #anade las celdas a las columnas
        columnText0.pack_start(cellText0, False)
        columnText1.pack_start(cellText1, False)
        columnText2.pack_start(cellText2, False)
        
        #anadir atributos a las columns
        columnText0.set_attributes(cellText0, text=0)
        columnText1.set_attributes(cellText1, text=1)
        columnText2.set_attributes(cellText2, text=2)

        columnText0.set_sort_column_id(0)
        columnText1.set_sort_column_id(1)
        columnText2.set_sort_column_id(2)

        agenda.vbox.pack_start(agendaTreeView, True, True, 0)

        agenda.show_all()
        self.__queueToServer.put((self.__Okeyko.agenda_lista, (), {}, \
                            self.agenda_ventana_add, (agenda_store), {}))
        return

    def agenda_ventana_add(self, arg, store):
        contactos = arg
        for contacto in contactos:
            nombre = contacto[0]
            desc = contacto[1]
            #imgavatar = self.okeyko.pagina(mensaje[4])
            #avatar =  gtk.gdk.PixbufLoader()
            #avatar.write(imgavatar)        
            #store.append([avatar.get_pixbuf(), nombre, desc])
            store.append(["nose", nombre, desc])
        #avatar.close()
        return

    def click_agenda(self, widget, row, col):
        model = widget.get_model()
        self.redactar_ventana( None, model[row][1])

    def mostrarmensaje(self, widget, row, col):
        model = widget.get_model()
        MensajeVen.MensajeVen(model, row, self.__Control)
        if model[row][7] == 0:
            self.__queueToServer.put((self.__Okeyko.set_leido, (model[row][5],),\
                                {}, self.Nulo, (), {}))
            texto = model[row][1].replace(" background=\"#F7BE81\"","")
            pixbuf = self.add_status(model[row][0], gtk.gdk.pixbuf_new_from_file(\
                        self.__Config.THEME_PATH + "leido_pc.png"),\
                        model[row][0].get_width() - 15,\
                        model[row][0].get_height() - 15)
            model.set_value(model.get_iter_from_string("%s:0" % (row)),0,pixbuf)
            model.set_value(model.get_iter_from_string("%s:1" % (row)),1,texto)
            model.set_value(model.get_iter_from_string("%s:7" % (row)),7,1)


    def Nulo(self, *args, **kwargs):
        return

    def blink(self):
        ''' Hace titilar al tray icon '''
        self.tray.tray.set_blinking(True)

    def close_application(self, widget, event=None, data=None):
        gtk.main_quit()
        exit()

