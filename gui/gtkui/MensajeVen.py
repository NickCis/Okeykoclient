import gtk

import htmltextview
import paths

class MensajeVen(gtk.Window):
    ''' Ventana que muestra mensaje recivido'''

    UI = '''<ui>
    <menubar name="MenuBar">
      <menu action="Archivo">
        <menuitem action="Salir"/>
      </menu>
      <menu action="Mensajes">
        <menuitem action="Nada"/>
      </menu>
      <menu action="Contactos">
        <menuitem action="Nada"/>
        <menuitem action="Nada"/>
        <menuitem action="Nada"/>
      </menu>
    </menubar>
    <toolbar name="Toolbar">
      <toolitem action="Resp"/>
      <separator/>
      <toolitem action="Age"/>
      <separator/>
      <toolitem action="Favs"/>
      <separator/>
      <toolitem action="Bor"/>
    </toolbar>
    </ui>'''

    #def __init__(self, okid, para, hora, mensaje, avatar):
    def __init__(self, model, row, Control):
        def agendar(*args, **kargs):
            Control['MainWindow'].agendaAdd(para)

        def closeWin(*args,**kargs):
            self.destroy()

        def responder(*args, **kargs):
            Control['MainWindow'].redactar_ventana(None, para)

        def borrar(*args, **kargs):
            Control['MainWindow'].borInbox(okid)
            self.destroy()

        
        def actcallb(*args, **kargs):
            print args, kargs
        gtk.Window.__init__(self)
        self.__Config = Control['Config']
        okid = model[row][5]
        para = model[row][2]
        hora = model[row][3]
        mensaje = model[row][4]
        avatarName = model[row][6]
        avatar = self.__Config.avatarLoad(avatarName, False)[1]
        #self.set_default_size(300,300)
        self.parse_geometry(self.__Config.user['menWindowGeometry'])
        self.connect("delete_event", self.saveMenWindowGeometry)
        self.set_title(para)

        MainVbox = gtk.VBox(False,0)
        self.add(MainVbox)

        #BHbox = gtk.HBox(False, 0)
        #BHbox.set_size_request(24,24)
        UpperHbox = gtk.HBox()
        UIVBox = gtk.VBox()
        LowerHbox = gtk.HBox()
        #MainVbox.pack_start(gtk.HSeparator(), False, 0)
        MainVbox.pack_start(UIVBox, False, 0)
        #MainVbox.pack_start(BHbox, False, 0)
        #MainVbox.pack_start(gtk.HSeparator(), False, 0)
        MainVbox.pack_start(UpperHbox)
        MainVbox.pack_start(LowerHbox)
        
        #Ui Manager --------------------------------------------
        uimanager = gtk.UIManager() #Create a Uimanager instance   
             
        accelgroup = uimanager.get_accel_group() # add accelartor group
        self.add_accel_group(accelgroup)         # to the toplevel win
        
        actiongroup = gtk.ActionGroup('UIManagerMenuTool') # Create Action Group
        
        #create actions        
        # (Name, StockItem, Label, accelerator, ToolTip, CallBack)
        actiongroup.add_actions([('Salir', gtk.STOCK_QUIT, '_Cerrar Ventana', "<Ctrl><Alt>q",
                                    'Cerrar Ventana', closeWin),
                                 ('Nada', gtk.STOCK_QUIT, '_Nada', None,
                                    'No hace nada', actcallb),
                                 ('Archivo', None, '_Archivo'),
                                 ('Contactos', None, '_Contactos'),
                                 ('Mensajes', None, '_Mensajes'),
                                 ('Resp', gtk.STOCK_REDO, 'Responder',
                                    '<Ctrl>r', None, responder ),
                                 ('Age', None, 'Agendar', '<ctrl>a',
                                    None, agendar),
                                 ('Favs', gtk.STOCK_ABOUT, 'Favoritos',
                                    '<Ctrl>f', 'Agregar a favoritos', actcallb ),
                                 ('Bor', gtk.STOCK_DELETE, 'Borrar', None,
                                    "Borrar Mensaje", borrar)])


        uimanager.insert_action_group(actiongroup, 0) #Add actiongroup to the uimanager
        
        uimanager.add_ui_from_string(self.UI) #Add UI description
         
        menubar = uimanager.get_widget('/MenuBar') #Create MenuBar
        UIVBox.pack_start(menubar, False)
        
        toolbar = uimanager.get_widget('/Toolbar') # Create a Toolbar
        toolbar.set_property('toolbar-style', gtk.TOOLBAR_BOTH)
        toolbar.set_property('icon-size', gtk.ICON_SIZE_SMALL_TOOLBAR)
        UIVBox.pack_start(toolbar, False)        


        #Reemplazar por gtk.UIManager --------------------------
        #ImResp = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "resp.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImResp.set_from_pixbuf(pixbuf)
        #ButResp = gtk.Button()
        #ButResp.set_image(ImResp)
        #ButResp.set_relief(gtk.RELIEF_NONE)
        #ImAg = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "ag.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImAg.set_from_pixbuf(pixbuf)
        #ButAg = gtk.Button()
        #ButAg.set_image(ImAg)
        #ButAg.set_relief(gtk.RELIEF_NONE)
        ##ImFav = gtk.Image()
        ##pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "fav.png")
        ##pixbuf = pixbuf.scale_simple(16,16,gtk.gdk.INTERP_NEAREST)
        ##ImFav.set_from_pixbuf(pixbuf)
        #ButFav = gtk.Button("Favoritos")
        ##ButFav.set_image(ImFav)
        #ButFav.set_relief(gtk.RELIEF_NONE)
        #ImBor = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "bor.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImBor.set_from_pixbuf(pixbuf)
        #ButBor = gtk.Button()
        #ButBor.set_image(ImBor)
        #ButBor.set_relief(gtk.RELIEF_NONE)

        #BHbox.pack_start(ButResp, False, False, 0)
        #BHbox.pack_start(ButAg, False, False, 0)
        #BHbox.pack_start(ButFav, False, False, 0)
        #BHbox.pack_start(ButBor, False, False, 0)
        
        # ------------------------------------------
        sw = gtk.ScrolledWindow()
        sw.set_size_request(200,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC , gtk.POLICY_AUTOMATIC)
        UpperHbox.pack_start(sw)

        fecha = hora[:hora.find("|")]
        hora = hora[hora.find("|") + 1:]
        #texto = "%s\n%s:\n    [%s] %s" % (fecha, para, hora, mensaje)
        texto = "<div>%s<br/>\n<span style='font-weight: bold'>%s:</span>" +\
            "<br/><span syle='text-indent: 2em'>[%s] %s</span></div>"
        texto = texto % (fecha, para, hora, mensaje)
        textbuffer = gtk.TextBuffer()
        textbuffer.set_text(texto)
        #TVmensaje = gtk.TextView()
        TVmensaje = htmltextview.HtmlTextView()
        TVmensaje.display_html(texto)
        TVmensaje.set_wrap_mode(gtk.WRAP_WORD)
        #TVmensaje.set_editable(False)
        #TVmensaje.set_buffer(textbuffer)
        #TVmensaje.set_left_margin(6)
        #TVmensaje.set_right_margin(6)
        #TVmensaje.set_wrap_mode(gtk.WRAP_WORD_CHAR)

        sw.add(TVmensaje)
        #avatarPixLoad =  gtk.gdk.PixbufLoader()
        #avatarPixLoad.write(avatar)
        #avatarT = avatarPixLoad.get_pixbuf()
        #avatarPixLoad.close()
        avatarT = gtk.gdk.pixbuf_new_from_file(avatar)
        avatar_w = avatarT.get_width()
        avatar_h = avatarT.get_height()
        avatarN_h = 100 * avatar_h / avatar_w
        avatarN = avatarT.scale_simple(100,avatarN_h,gtk.gdk.INTERP_NEAREST)
        Imagen = gtk.image_new_from_pixbuf(avatarN)
        UpperHbox.pack_start(Imagen)

        self.show_all()

    def saveMenWindowGeometry(self, *args, **kargs):
        xPos, yPos = self.get_position()
        wWin, hWin = self.get_size()
        menWinGeometry = "%sx%s+%s+%s" % (wWin, hWin, xPos, yPos)
        if self.__Config.user['menWindowGeometry'] != menWinGeometry:
            self.__Config.user['menWindowGeometry'] = menWinGeometry

class EnviadoVen(gtk.Window):
    ''' Ventana que muestra mensaje Enviado'''

    UI = '''<ui>
    <menubar name="MenuBar">
      <menu action="Archivo">
        <menuitem action="Salir"/>
      </menu>
      <menu action="Mensajes">
        <menuitem action="Nada"/>
      </menu>
      <menu action="Contactos">
        <menuitem action="Nada"/>
        <menuitem action="Nada"/>
        <menuitem action="Nada"/>
      </menu>
    </menubar>
    <toolbar name="Toolbar">
      <toolitem action="Resp"/>
      <separator/>
      <toolitem action="Age"/>
      <separator/>
      <toolitem action="Bor"/>
    </toolbar>
    </ui>'''

    #def __init__(self, okid, para, hora, mensaje, avatar):
    def __init__(self, model, row, Control):
        def agendar(*args, **kargs):
            Control['MainWindow'].agendaAdd(para)

        def closeWin(*args,**kargs):
            self.destroy()

        def responder(*args, **kargs):
            Control['MainWindow'].redactar_ventana(None, para, model[row][4])

        def borrar(*args, **kargs):
            Control['MainWindow'].borOutbox(okid)
            self.destroy()

        
        def actcallb(*args, **kargs):
            print args, kargs
        gtk.Window.__init__(self)
        self.__Config = Control['Config']
        okid = model[row][5]
        para = model[row][2]
        hora = model[row][3]
        mensaje = model[row][4]
        avatarName = model[row][6]
        avatar = self.__Config.avatarLoad(avatarName, False)[1]
        #self.set_default_size(300,300)
        self.parse_geometry(self.__Config.user['menWindowGeometry'])
        self.connect("delete_event", self.saveMenWindowGeometry)
        self.set_title(para)

        MainVbox = gtk.VBox(False,0)
        self.add(MainVbox)

        #BHbox = gtk.HBox(False, 0)
        #BHbox.set_size_request(24,24)
        UpperHbox = gtk.HBox()
        UIVBox = gtk.VBox()
        LowerHbox = gtk.HBox()
        #MainVbox.pack_start(gtk.HSeparator(), False, 0)
        MainVbox.pack_start(UIVBox, False, 0)
        #MainVbox.pack_start(BHbox, False, 0)
        #MainVbox.pack_start(gtk.HSeparator(), False, 0)
        MainVbox.pack_start(UpperHbox)
        MainVbox.pack_start(LowerHbox)
        
        #Ui Manager --------------------------------------------
        uimanager = gtk.UIManager() #Create a Uimanager instance   
             
        accelgroup = uimanager.get_accel_group() # add accelartor group
        self.add_accel_group(accelgroup)         # to the toplevel win
        
        actiongroup = gtk.ActionGroup('UIManagerMenuTool') # Create Action Group
        
        #create actions        
        # (Name, StockItem, Label, accelerator, ToolTip, CallBack)
        actiongroup.add_actions([('Salir', gtk.STOCK_QUIT, '_Cerrar Ventana', "<Ctrl><Alt>q",
                                    'Cerrar Ventana', closeWin),
                                 ('Nada', gtk.STOCK_QUIT, '_Nada', None,
                                    'No hace nada', actcallb),
                                 ('Archivo', None, '_Archivo'),
                                 ('Contactos', None, '_Contactos'),
                                 ('Mensajes', None, '_Mensajes'),
                                 ('Resp', gtk.STOCK_REDO, 'Reenviar',
                                    '<Ctrl>r', None, responder ),
                                 ('Age', None, 'Agendar', '<ctrl>a',
                                    None, agendar),
                                 ('Bor', gtk.STOCK_DELETE, 'Borrar', None,
                                    "Borrar Mensaje", borrar)])


        uimanager.insert_action_group(actiongroup, 0) #Add actiongroup to the uimanager
        
        uimanager.add_ui_from_string(self.UI) #Add UI description
         
        menubar = uimanager.get_widget('/MenuBar') #Create MenuBar
        UIVBox.pack_start(menubar, False)
        
        toolbar = uimanager.get_widget('/Toolbar') # Create a Toolbar
        toolbar.set_property('toolbar-style', gtk.TOOLBAR_BOTH)
        toolbar.set_property('icon-size', gtk.ICON_SIZE_SMALL_TOOLBAR)
        UIVBox.pack_start(toolbar, False)        


        #Reemplazar por gtk.UIManager --------------------------
        #ImResp = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "resp.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImResp.set_from_pixbuf(pixbuf)
        #ButResp = gtk.Button()
        #ButResp.set_image(ImResp)
        #ButResp.set_relief(gtk.RELIEF_NONE)
        #ImAg = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "ag.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImAg.set_from_pixbuf(pixbuf)
        #ButAg = gtk.Button()
        #ButAg.set_image(ImAg)
        #ButAg.set_relief(gtk.RELIEF_NONE)
        ##ImFav = gtk.Image()
        ##pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "fav.png")
        ##pixbuf = pixbuf.scale_simple(16,16,gtk.gdk.INTERP_NEAREST)
        ##ImFav.set_from_pixbuf(pixbuf)
        #ButFav = gtk.Button("Favoritos")
        ##ButFav.set_image(ImFav)
        #ButFav.set_relief(gtk.RELIEF_NONE)
        #ImBor = gtk.Image()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(paths.DEFAULT_THEME_PATH + "bor.png")
        #pixbuf = pixbuf.scale_simple(24,24,gtk.gdk.INTERP_NEAREST)
        #ImBor.set_from_pixbuf(pixbuf)
        #ButBor = gtk.Button()
        #ButBor.set_image(ImBor)
        #ButBor.set_relief(gtk.RELIEF_NONE)

        #BHbox.pack_start(ButResp, False, False, 0)
        #BHbox.pack_start(ButAg, False, False, 0)
        #BHbox.pack_start(ButFav, False, False, 0)
        #BHbox.pack_start(ButBor, False, False, 0)
        
        # ------------------------------------------
        sw = gtk.ScrolledWindow()
        sw.set_size_request(200,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC , gtk.POLICY_AUTOMATIC)
        UpperHbox.pack_start(sw)

        fecha = hora[:hora.find("|")]
        hora = hora[hora.find("|") + 1:]
        #texto = "%s\n%s:\n    [%s] %s" % (fecha, para, hora, mensaje)
        texto = "<div>%s<br/>\n<span style='font-weight: bold'>Para %s:</span>" +\
            "<br/><span syle='text-indent: 2em'>[%s] %s</span></div>"
        texto = texto % (fecha, para, hora, mensaje)
        textbuffer = gtk.TextBuffer()
        textbuffer.set_text(texto)
        #TVmensaje = gtk.TextView()
        TVmensaje = htmltextview.HtmlTextView()
        TVmensaje.display_html(texto)
        TVmensaje.set_wrap_mode(gtk.WRAP_WORD)
        #TVmensaje.set_editable(False)
        #TVmensaje.set_buffer(textbuffer)
        #TVmensaje.set_left_margin(6)
        #TVmensaje.set_right_margin(6)
        #TVmensaje.set_wrap_mode(gtk.WRAP_WORD_CHAR)

        sw.add(TVmensaje)
        #avatarPixLoad =  gtk.gdk.PixbufLoader()
        #avatarPixLoad.write(avatar)
        #avatarT = avatarPixLoad.get_pixbuf()
        #avatarPixLoad.close()
        avatarT = gtk.gdk.pixbuf_new_from_file(avatar)
        avatar_w = avatarT.get_width()
        avatar_h = avatarT.get_height()
        avatarN_h = 100 * avatar_h / avatar_w
        avatarN = avatarT.scale_simple(100,avatarN_h,gtk.gdk.INTERP_NEAREST)
        Imagen = gtk.image_new_from_pixbuf(avatarN)
        UpperHbox.pack_start(Imagen)

        self.show_all()

    def saveMenWindowGeometry(self, *args, **kargs):
        xPos, yPos = self.get_position()
        wWin, hWin = self.get_size()
        menWinGeometry = "%sx%s+%s+%s" % (wWin, hWin, xPos, yPos)
        if self.__Config.user['menWindowGeometry'] != menWinGeometry:
            self.__Config.user['menWindowGeometry'] = menWinGeometry

def parse_emot(text, dict=None):
    if dict == None:
        dict = { ':)': 'emot-feliz.png',\
                    ':(': 'emot-triste.png',\
                    '(H)': 'emot-banana.png',\
                    ':-#': 'emot-callate.png',\
                    ':$': 'emot-colorado.png',\
                    ':?': 'emot-loco.png',\
                    ':S': 'emot-mmm.png',\
                    '+o(': 'emot-puag.png',\
                    '(6)': 'emot-diablo.png',\
                    '(A)': 'emot-angel.png',\
                    ':@': 'emot-enfadado.png',\
                    '=@': 'emot-enojado.png',\
                    ';)': 'emot-ok.png',\
                    '8-|': 'emot-nerd.png',\
                    '(N)': 'emot-ninja.png',\
                    ':0': 'emot-oo.png',\
                    ':]': 'emot-jeje.png',\
                    ':\'(': 'emot-llora.png',\
                    ':^(': 'emot-pomada.png',\
                    '(^)': 'emot-torta.png',\
                    '(ip)': 'emot-playa.png',\
                    '(Pi)': 'emot-burger.png',\
                    '(L)': 'emot-corazon.gif' }
