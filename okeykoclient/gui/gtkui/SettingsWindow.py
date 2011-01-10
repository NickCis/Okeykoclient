# -*- coding: utf-8 -*-
import os
import gtk
import pango

LIST = [ 
    {'stock_id' : gtk.STOCK_HOME, 'text' : 'General'},
    {'stock_id' : gtk.STOCK_SELECT_COLOR,'text' : 'Tema'},
    {'stock_id' : gtk.STOCK_INDEX,'text' : 'Notificaciones'},
    {'stock_id' : gtk.STOCK_MEDIA_NEXT,'text' : 'Sonidos'},
    {'stock_id' : gtk.STOCK_LEAVE_FULLSCREEN,'text' : 'Escritorio'},
]

SPACING = 8
PADDING = 5

class SettingsWindow(gtk.Window):

    def __init__(self, Control, parent, setPage=0):
        gtk.Window.__init__(self)
        
        self.__Config = Control['Config']

        self.set_default_size(600, 400)
        self.set_title('Ajustes')
        self.set_role('preferences')
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_resizable(False)

        icon = self.render_icon(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
        self.set_icon(icon)
        
        self.set_transient_for(parent)
        
        self.set_border_width(6)
        
        # Create the list store model for the treeview.
        listStore = gtk.ListStore(gtk.gdk.Pixbuf, str)
        
        for i in LIST:
            #we should use always the same icon size, we can remove that field in LIST
            listStore.append([self.render_icon(i['stock_id'], \
                              gtk.ICON_SIZE_LARGE_TOOLBAR), i['text']])

        treeView = gtk.TreeView(listStore) # Create the TreeView

        # Create the renders
        cellText = gtk.CellRendererText()
        cellPix = gtk.CellRendererPixbuf()

        # Create the single Tree Column
        treeViewColumn = gtk.TreeViewColumn('Categories')

        treeViewColumn.pack_start(cellPix, expand=False)
        treeViewColumn.add_attribute(cellPix, 'pixbuf',0)
        treeViewColumn.pack_start(cellText, expand=True)
        treeViewColumn.set_attributes(cellText, text=1)

        treeView.append_column(treeViewColumn)
        treeView.set_headers_visible(False)
        treeView.connect('cursor-changed', self._on_row_activated)
        self.treeview = treeView

        #Notebook        
        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_resize_mode(gtk.RESIZE_QUEUE)
        self.notebook.set_scrollable(True)

        #Pack everything
        vbox = gtk.VBox()
        vbox.set_spacing(4)
        hbox = gtk.HBox(homogeneous=False, spacing=5)
        hbox.pack_start(treeView, True,True) # False, True
        hbox.pack_start(self.notebook, True, True)
        vbox.pack_start(hbox, True,True) # hbox, True, True

        # BUTTON BOX FOR CLOSE BUTTON
        bClose = gtk.Button(stock=gtk.STOCK_CLOSE)
        hButBox = gtk.HButtonBox()
        hButBox.set_spacing(4)
        hButBox.set_layout(gtk.BUTTONBOX_END)
        hButBox.pack_start(bClose)
        vbox.pack_start(hButBox, False, False)
        
        self.pageGeneral = pageGeneral(Control)
        self.pageTema = pageTema(Control)
        self.pageNot = pageNot(Control)
        self.pageSonido = pageSonido(Control)
        self.pageEscritorio = pageEscritorio(Control)
        
        self.page_dict = [self.pageGeneral, self.pageTema, self.pageNot,
                          self.pageSonido, self.pageEscritorio]

        for p in self.page_dict:
            self.notebook.append_page(p)

        self.add(vbox)

        self.treeview.set_cursor(setPage) #the row-selected signal callback calls the showPage

        self.show_all()

        # Register events for the close button and window
        self.connect('delete-event', self.close)
        bClose.connect('clicked', self.close)

    def close(self, *args):
        '''Close the window'''
        self.hide()
        self.save()
        self.destroy()

    def save(self):
        ''' Call code to save the preferences'''
        for page in self.page_dict:
                page.save()

    def _on_row_activated(self,treeview):
        # Get information about the row that has been selected
        cursor, obj = treeview.get_cursor()
        self.showPage(cursor[0])

    def showPage(self, index):
        self.notebook.set_current_page(index)
        self.current_page = index


class pageGeneral(gtk.VBox):
    def __init__(self, Control):
        gtk.VBox.__init__(self)

    def save(self):
        pass

class pageNot(gtk.VBox):
   ''' This represents the Notification page. '''
   def __init__(self, Control):
      gtk.VBox.__init__(self)
      self.control = Control
      self.config = self.control['Config']
      
      self.notFont = self.config.user['notFont']
      self.notColor = self.config.user['notColor']

      self.set_spacing(SPACING-3) #to fit the actual height
      self.set_border_width(10)
      self.installNewText = 'Instalar nuevo...'


      
      lbTitle = gtk.Label()
      lbTitle.set_markup('<b>Notificaciones en Pantalla</b>')
      hbTitleLabel = gtk.HBox()
      hbTitleLabel.pack_start(lbTitle, False, True, padding=5)
      self.pack_start(hbTitleLabel, False, False, padding=5)
      
      self.enablenot = gtk.CheckButton('_Activar Notificaciones en Pantalla')
      self.enablenot.set_active(self.config.user['enableNot'])
      self.enablenot.connect('toggled', self.notToggled) #TODO
      
      themes = list(self.config.themesNot)

      self.theme = gtk.combo_box_new_text()
      labelTheme = gtk.Label('_Tema:')
      labelTheme.set_alignment(0.0, 0.5)
      labelTheme.set_use_underline(True)
      self.values2 = {}
      count=0
      self.notDefaultIndex = None
      for name in themes:
          self.theme.append_text(name)
          self.values2[name]=int(count)
          if name == 'default':
              self.notDefaultIndex = count
          count += 1
      self.theme.append_text(self.installNewText)
      if self.config.user['themeNot'] in themes:
          self.theme.set_active(self.values2[self.config.user['themeNot']])
      else:
          self.theme.set_active(0)
      self.theme.connect("changed", self.savetheme)
      
      vboxlabel = gtk.VBox(homogeneous=False, spacing=5)
      vboxlabel.pack_start(labelTheme, True, True)
      
      vboxentry = gtk.VBox(homogeneous=False, spacing=5)
      vboxentry.pack_start(self.theme, True, True)

      self.previewButton = gtk.Button()
      self.previewButton.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY,gtk.ICON_SIZE_SMALL_TOOLBAR))
      self.previewButton.connect('clicked', self.showPreview)      
      self.previewButton.set_tooltip_text("Vista Previa de tema de Notificacion en Pantalla entrante seleccionado.")
      
      hbox = gtk.HBox(homogeneous=False, spacing=SPACING)
      hbox.pack_start(vboxlabel, False, True)
      hbox.pack_start(vboxentry, True, True)
      hbox.pack_start(self.previewButton, False, False)
       
      self.showrecibido = gtk.CheckButton('Mostrar notificacion en pantalla al recibir mensajes')
      self.showrecibido.set_active(self.config.user['notshowRecibido'])
      
      self.showpensamiento =  gtk.CheckButton('Mostrar notificacion en pantalla cunado halla un nuevo pensamiento')
      self.showpensamiento.set_active(self.config.user['notshowPensamiento'])
      
      self.showenviar =  gtk.CheckButton('Mostrar notificacion en pantalla cuando se envie un mensaje')
      self.showenviar.set_active(self.config.user['notshowEnviar'])
      
      settings1 = gtk.VBox()
      settings1.pack_start(self.showrecibido)
      settings1.pack_start(self.showpensamiento)
      settings1.pack_start(self.showenviar)
      
      frame1 = gtk.Frame('Notificaciones de eventos')
      frame1.set_border_width(4)
      frame1.add(settings1)

      hboxnotType = gtk.VBox()
      labelnotType = gtk.Label('Tipo de notificacion:')
      labelnotType.set_alignment(0.0, 0.5)
      self.notType = gtk.combo_box_new_text() #FIXME: Use for
      self.notType.append_text('Emesene Style')
      self.notType.append_text('Gtk Notifications')
      self.notType.append_text('PyNotify Notification (require pynotify lib)')
      self.notType.set_active(int(self.config.user['notType']))
      hboxnotType.pack_start(labelnotType)
      hboxnotType.pack_start(self.notType)

      tipografia = gtk.HBox()
      
      self.tipografialabel = gtk.Label('Tipografia')
      tipostockimg1 = gtk.image_new_from_stock(gtk.STOCK_SELECT_COLOR, 
                                               gtk.ICON_SIZE_MENU )
      self.tipografiabut1 = gtk.Button()
      self.tipografiabut1.add(tipostockimg1)
      self.tipografiabut1.connect('clicked', self.clickColor)
      tipostockimg2 = gtk.image_new_from_stock(gtk.STOCK_SELECT_FONT, 
                                               gtk.ICON_SIZE_MENU )
      self.tipografiabut2 = gtk.Button()
      self.tipografiabut2.add(tipostockimg2)
      self.tipografiabut2.connect('clicked', self.clickFont)
      tipografia.pack_start(self.tipografialabel, False, False, 3)
      tipografia.pack_start(self.tipografiabut1, False, False, 10)
      tipografia.pack_start(self.tipografiabut2, False, False)
      
      posicion = gtk.HBox()
      self.posicionlabel = gtk.Label('Posicion')
      self.posicionCombo = gtk.combo_box_new_text()
      self.posicionCombo.append_text('Superior izquierda')
      self.posicionCombo.append_text('Superior derecha')
      self.posicionCombo.append_text('Inferior izquierda')
      self.posicionCombo.append_text('Inferior derecha')
      self.posicionCombo.set_active(int(self.config.user['notCorner']))
      
      posicion.pack_start(self.posicionlabel, False, False, 3)
      posicion.pack_start(self.posicionCombo, True, True, 10)
      
      desplazamiento = gtk.HBox()
      self.desplazamientolabel = gtk.Label('Desplazamiento')
      self.desplazamientoCombo = gtk.combo_box_new_text()
      self.desplazamientoCombo.append_text('Horizontal')
      self.desplazamientoCombo.append_text('Vertical')
      self.desplazamientoCombo.set_active(int(self.config.user['notScroll']))
      
      desplazamiento.pack_start(self.desplazamientolabel, False, False, 3)
      desplazamiento.pack_start(self.desplazamientoCombo, True, True, 10)

      settings2 = gtk.VBox()
      settings2.pack_start(hboxnotType)
      settings2.pack_start(tipografia)
      settings2.pack_start(posicion)
      settings2.pack_start(desplazamiento)
      
      frame2 = gtk.Frame('Configuracion de notificaciones')
      frame2.set_border_width(4)
      frame2.add(settings2)
      
      self.pack_start(self.enablenot, False, False)
      self.pack_start(hbox, False, False)
      self.pack_start(frame1, False, False)
      self.pack_start(frame2, False, False)
      
      self.show_all()
      self.notToggled(self.enablenot)

   #def playPreview(self, button):
   def showPreview(self, *args):
      pos = self.posicionCombo.get_active()
      scroll = self.desplazamientoCombo.get_active()
      font = self.notFont
      color = self.notColor
      theme = self.theme.get_active_text()
      notType = self.notType.get_active()
      self.control['Notification'].preview(pos, scroll, font, color, theme, notType)

   def savetheme(self, combo):
      active = combo.get_active_text()
      if active == self.installNewText:
         installed = self.installTheme(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,self.notInstaller)
         if not installed == "":
            active = installed
            print active
            combo.prepend_text(active)
            self.notDefaultIndex += 1
            combo.set_active(0)
         else:
            combo.set_active(self.notDefaultIndex)
            active = "default"
      self.config.user['themeNot'] = active
      self.control['Notification'].updateConfig()
   
   def notInstaller(self, path):
      themeName = path.split(os.sep)[-1]
      themes = list(self.config.themesNot)
      themes = [x for x in themes if not x.startswith('.')]
      if themeName in themes:
         print "There's already a Notification theme with the same name"
         return ""
      return self.config.installTheme(themeName, path)
   
   def installTheme(self, chooserAction, installFunction, chooserTitle="Seleccionar carpeta del Tema", validateFunction=None):
      ''' chooserAction is a gtk.FILE_CHOOSER_ACTION specifying file or folder action '''
      fileChooser = gtk.FileChooserDialog(title=chooserTitle, action=chooserAction,\
                                              buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,\
                                              gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
      fileChooser.set_select_multiple(False)
      response = fileChooser.run()
      if response == gtk.RESPONSE_ACCEPT:
         selectedPath = fileChooser.get_filename()
         themeName = installFunction(selectedPath)
         fileChooser.destroy()
         return themeName
      else:
         fileChooser.destroy()
         return ""
   
   def save(self):
      '''save the actual setting'''      
      self.config.user['notshowRecibido'] = self.showrecibido.get_active()
      self.config.user['notshowPensamiento'] = self.showpensamiento.get_active()
      self.config.user['notshowEnviar'] = self.showenviar.get_active()
      
      self.config.user['notCorner'] = self.posicionCombo.get_active()
      self.config.user['notScroll'] = self.desplazamientoCombo.get_active()
      
      self.config.user['notFont'] = self.notFont
      self.config.user['notColor'] = self.notColor

      self.config.user['notType'] = self.notType.get_active()

      self.config.user['enableNot'] = self.enablenot.get_active()
      
      #self.config.user['themeNot'] = self.theme.get_active_text()

      self.control['Notification'].updateConfig()
      #if self.enablesounds.get_active() == False and self.config.user['enableSounds'] == True:
      #   self.handler.stop()
      #elif self.enablesounds.get_active() == True and self.config.user['enableSounds'] == False:
      #   self.handler.__init__(self.controller, self.controller.msn, action='start')
     
   def notToggled(self, check):
      self.save()
      self.theme.set_sensitive(check.get_active())
      self.posicionlabel.set_sensitive(check.get_active())
      self.posicionCombo.set_sensitive(check.get_active())
      self.desplazamientolabel.set_sensitive(check.get_active())
      self.desplazamientoCombo.set_sensitive(check.get_active())
      self.tipografialabel.set_sensitive(check.get_active())
      self.tipografiabut1.set_sensitive(check.get_active())
      self.tipografiabut2.set_sensitive(check.get_active())
      self.showrecibido.set_sensitive(check.get_active())
      self.showpensamiento.set_sensitive(check.get_active())
      self.showenviar.set_sensitive(check.get_active())
      self.previewButton.set_sensitive(check.get_active())

   def clickFont(self, arg):
      fontDialog = gtk.FontSelectionDialog('Seleccionar Letra')
      if self.notFont != None:
         fontDialog.set_font_name(self.notFont)
      response = fontDialog.run()
      if response == gtk.RESPONSE_OK:
         pangoDesc = pango.FontDescription(fontDialog.get_font_name())
         self.notFont = pangoDesc.to_string()
      fontDialog.destroy()

   def clickColor(self, arg):
      colorDialog = gtk.ColorSelectionDialog('Elegir color')
      colorDialog.colorsel.set_has_palette(True)
      red = int(self.notColor[1:3], 16) << 8
      green = int(self.notColor[3:5], 16) << 8
      blue = int(self.notColor[5:7], 16) << 8
      colorDialog.colorsel.set_current_color(gtk.gdk.Color(red, green, blue))
      response = colorDialog.run()
      if response == gtk.RESPONSE_OK:
         color = colorDialog.colorsel.get_current_color()
         red = color.red >> 8
         green = color.green >> 8
         blue = color.blue >> 8
         self.notColor = '#%02X%02X%02X' % (red, green, blue)
      colorDialog.destroy()    

class pageSonido(gtk.VBox):
   ''' This represents the Sounds page. '''   
   def __init__(self, Control):
      gtk.VBox.__init__(self)
      self.control = Control
      self.config = self.control['Config']

      self.set_spacing(SPACING-3) #to fit the actual height
      self.set_border_width(10)
      self.installNewText = 'Instalar nuevo...'
      
      lbTitle = gtk.Label()
      lbTitle.set_markup('<b>Notificaciones de Sonido</b>')
      hbTitleLabel = gtk.HBox()
      hbTitleLabel.pack_start(lbTitle, False, True, padding=5)
      self.pack_start(hbTitleLabel, False, False, padding=5)
      
      self.enablesounds = gtk.CheckButton('_Activar Notificaciones de Sonido')
      self.enablesounds.set_active(self.config.user['enableSounds'])
      self.enablesounds.connect('toggled', self.soundsToggled)
      
      themes = list(self.config.themesSound)

      self.theme = gtk.combo_box_new_text()
      labelTheme = gtk.Label('Tema:')
      labelTheme.set_alignment(0.0, 0.5)
      labelTheme.set_use_underline(True)
      self.values2 = {}
      count=0
      self.soundsDefaultIndex = None
      for name in themes:
          self.theme.append_text(name)
          self.values2[name]=int(count)
          if name == 'default':
              self.soundsDefaultIndex = count
          count += 1
      self.theme.append_text(self.installNewText)
      if self.config.user['themeSound'] in themes:
          self.theme.set_active(self.values2[self.config.user['themeSound']])
      else:
          self.theme.set_active(0)
      self.theme.connect("changed", self.savetheme)
      
      vboxlabel = gtk.VBox(homogeneous=False, spacing=5)
      vboxlabel.pack_start(labelTheme, True, True)
      
      vboxentry = gtk.VBox(homogeneous=False, spacing=5)
      vboxentry.pack_start(self.theme, True, True)

      self.previewButton = gtk.Button()
      self.previewButton.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY,gtk.ICON_SIZE_SMALL_TOOLBAR))
      #self.previewButton.connect('clicked', self.playPreview)
      self.previewButton.connect('event', self.playPreview)
      self.previewButton.set_tooltip_text("Vista Previa de tema de Sonido entrante seleccionado.")
      
      hbox = gtk.HBox(homogeneous=False, spacing=SPACING)
      hbox.pack_start(vboxlabel, False, True)
      hbox.pack_start(vboxentry, True, True)
      hbox.pack_start(self.previewButton, False, False)
       
      self.playrecibido = gtk.CheckButton('Reproducir sonido al recibir mensajes')
      self.playrecibido.set_active(self.config.user['soundsplayRecibido'])
      
      self.playpensamiento =  gtk.CheckButton('Reproducir sonido cunado halla un nuevo pensamiento')
      self.playpensamiento.set_active(self.config.user['soundsplayPensamiento'])
      
      self.playenviar =  gtk.CheckButton('Reproducir sonido cuando se envie un mensaje')
      self.playenviar.set_active(self.config.user['soundsplayEnviar'])
      
      settings1 = gtk.VBox()
      settings1.pack_start(self.playrecibido)
      settings1.pack_start(self.playpensamiento)
      settings1.pack_start(self.playenviar)
      
      frame1 = gtk.Frame('Notificaciones de eventos')
      frame1.set_border_width(4)
      frame1.add(settings1)

      self.beep =  gtk.CheckButton('Usar el altavoz interno del sistema en vez de archivos de sonido')
      self.beep.set_active(self.config.user['soundsbeep'])
      
      settings2 = gtk.VBox()
      settings2.pack_start(self.beep)
      
      frame2 = gtk.Frame('Configuracion de notificaciones')
      frame2.set_border_width(4)
      frame2.add(settings2)
      
      self.pack_start(self.enablesounds, False, False)
      self.pack_start(hbox, False, False)
      self.pack_start(frame1, False, False)
      self.pack_start(frame2, False, False)
      
      self.show_all()
      self.soundsToggled(self.enablesounds)

   #def playPreview(self, button):
   def playPreview(self, widget=None, event=None, child=None, *args):
      def play(menuitem, sfile):
         self.control['Sound'].sound.play_theme(
                               self.theme.get_active_text(), sfile )
      if not event.type == gtk.gdk.BUTTON_PRESS:
         return

      menu = gtk.Menu()
      
      for sf in self.config.THEME_SOUND_FILES:
         menuItem = gtk.MenuItem(sf)
         menuItem.connect('activate', play, sf)
         menu.append(menuItem)
      menu.show_all()
      menu.popup(None, None, None, event.button, event.time)

   def savetheme(self, combo):
      active = combo.get_active_text()
      if active == self.installNewText:
         installed = self.installTheme(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,self.audioInstaller)
         if not installed == "":
            active = installed
            print active
            combo.prepend_text(active)
            self.soundsDefaultIndex += 1
            combo.set_active(0)
         else:
            combo.set_active(self.soundsDefaultIndex)
            active = "default"
      self.config.user['themeSound'] = active
      self.control['Sound'].update()
   
   def audioInstaller(self, path):
      #read theme name
      themeName = path.split(os.sep)[-1]
      #themes = os.listdir(paths.APP_PATH + os.sep + 'sound_themes')
      themes = list(self.config.themesSound)
      themes = [x for x in themes if not x.startswith('.')]
      if themeName in themes:
         print "There's already an audio theme with the same name"
         return ""
      #create the folder and copy the file inside
      #theme_path=paths.APP_PATH + os.sep + 'sound_themes' + os.sep + themeName.lower()
      #shutil.copytree(path,theme_path)
      #return themeName.lower()
      return self.config.installTheme(themeName, path)
   
   def installTheme(self, chooserAction, installFunction, chooserTitle="Seleccionar carpeta del Tema", validateFunction=None):
      ''' chooserAction is a gtk.FILE_CHOOSER_ACTION specifying file or folder action '''
      fileChooser = gtk.FileChooserDialog(title=chooserTitle, action=chooserAction,\
                                              buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,\
                                              gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
      fileChooser.set_select_multiple(False)
      response = fileChooser.run()
      if response == gtk.RESPONSE_ACCEPT:
         selectedPath = fileChooser.get_filename()
         themeName = installFunction(selectedPath)
         fileChooser.destroy()
         return themeName
      else:
         fileChooser.destroy()
         return ""
   
   def save(self):
      '''save the actual setting'''      
      self.config.user['soundsplayRecibido'] = self.playrecibido.get_active()
      self.config.user['soundsplayPensamiento'] = self.playpensamiento.get_active()
      self.config.user['soundsplayEnviar'] = self.playenviar.get_active()
      
      self.config.user['soundsbeep'] = self.beep.get_active()
      self.control['Sound'].update()
      #if self.enablesounds.get_active() == False and self.config.user['enableSounds'] == True:
      #   self.handler.stop()
      #elif self.enablesounds.get_active() == True and self.config.user['enableSounds'] == False:
      #   self.handler.__init__(self.controller, self.controller.msn, action='start')
      self.config.user['enableSounds'] = self.enablesounds.get_active()
     
   def soundsToggled(self, check):
      self.save()
      self.theme.set_sensitive(check.get_active())
      self.beep.set_sensitive(check.get_active())
      self.playrecibido.set_sensitive(check.get_active())
      self.playpensamiento.set_sensitive(check.get_active())
      self.playenviar.set_sensitive(check.get_active())
      self.previewButton.set_sensitive(check.get_active())

class pageTema(gtk.VBox):
    def __init__(self, Control):
        gtk.VBox.__init__(self)

    def save(self):
        pass

#class DesktopPage(gtk.VBox):pageEscritorio
class pageEscritorio(gtk.VBox):
    ''' This represents the desktop page. '''
    
    def __init__(self, Control):
        gtk.VBox.__init__(self)       
        self.config = Control['Config']        
        self.control = Control
        self.set_spacing(SPACING-3)
        self.set_border_width(10)

        lbTitle = gtk.Label()
        lbTitle.set_markup('<b>Integracion con el entorno de escritorio</b>')
        hbTitleLabel = gtk.HBox()
        hbTitleLabel.pack_start(lbTitle, False, True, padding=5)
        self.pack_start(hbTitleLabel, False, False, padding=5)

        self.urlSettings = UrlSettings(self.config, Control['desktop'])
        frame1 = gtk.Frame('Enlaces y Archivos')
#        frame1.set_border_width(4)
        frame1.add(self.urlSettings)
        
        #self.emailSettings = EmailSettings(config)
        #frame2 = gtk.Frame(_('E-mails'))
        ##frame2.set_border_width(4)
        #frame2.add(self.emailSettings)

        #self.rgba = gtk.CheckButton(_('Enable rgba colormap (requires restart)'))
        #self.rgba.set_active(self.config.glob['rgbaColormap'])
        #self.rgba.set_tooltip_text(_('If enabled, it gives the desktop theme the ability' \
        #                             ' to make transparent windows using the alpha channel'))

        self.disableTray = gtk.CheckButton('Desactivar icono en bandeja (requiere reiniciar)')
        self.disableTray.set_active(self.config.glob['disableTrayIcon'])

        #self.pack_start(self.rgba, False)
        self.pack_start(self.disableTray, False)
        self.pack_start(frame1, False)
        #self.pack_start(frame2, False)

    def save(self, widget=None):
        #self.config.glob['rgbaColormap'] = self.rgba.get_active()
        self.config.glob['disableTrayIcon'] = self.disableTray.get_active()
        self.urlSettings.save()
        #self.emailSettings.save()       


class UrlSettings(gtk.VBox):
    def __init__(self, config, desktop):
        gtk.VBox.__init__(self)
        self.desktop = desktop
        self.set_spacing(2)
        self.set_border_width(4)
        self.config = config

        detected = self.desktop.get_desktop(True)
        if detected:
            #commandline = ' '.join(self.desktop.get_command(detected, '')).strip()
            tmp = {
                'detected': detected,
                #'commandline': commandline,
            }
            #self.markup = 'El entorno de escritorio detectado es ' \
            #    '<b>"%(detected)s"</b>. ' \
            #    '<span face="Monospace">%(commandline)s</span> ' \
            #    'se usara para abrir enlaces y archivos' % tmp
            self.markup = 'El entorno de escritorio detectado es ' \
                '<b>"%(detected)s"</b>. ' \
                'se usara para abrir enlaces y archivos' % tmp
        else:
            self.markup = '<b>No se detecto entorno de escritorio.</b> ' \
                'El primer navegador encontrado se usara para abrir enlaces'

        self.infolabel = gtk.Label()

        self.infolabel.set_alignment(0.0, 0.0)

        self.hboxentry = gtk.HBox()
        self.entry = gtk.Entry()
        self.entry.connect('activate', self.save)
        self.hboxentry.set_spacing(3)
        self.hboxentry.pack_start(gtk.Label('Comando:'), False)
        self.hboxentry.pack_start(self.entry)

        self.override = gtk.CheckButton('Sobreescribir Configuracion detectada')
        self.override.set_active(self.config.glob['overrideDesktop'] != '')
        self.override.connect('toggled', self.toggleOverride)

        self.helplabel = gtk.Label()
        self.helplabel.set_markup('<i>Nota:</i> se reemplazara %s ' \
            'por la url a abrir' % '%url%')
        self.helplabel.set_alignment(0.5, 1.0)

        self.hboxtest = gtk.HBox()
        self.testbutton = gtk.Button('Click para probar')
        self.testbutton.connect('clicked', self.testDesktop)
        self.hboxtest.pack_start(self.helplabel, True, False)
        self.hboxtest.pack_start(self.testbutton, False, True, 6)

        self.hboxOverride = gtk.HBox()
        self.hboxOverride.set_spacing(10)
        self.hboxOverride.pack_start(self.override, False)
        self.hboxOverride.pack_start(self.hboxentry, True)

        self.pack_start(self.infolabel, False)
        self.pack_start(self.hboxOverride, False)
        self.pack_start(self.hboxtest, False)

        self.toggleOverride()
        self.connect('map', self.on_mapped)

    def toggleOverride(self, override=None):
        active = self.override.get_active()
        self.hboxentry.set_sensitive(active)
        self.hboxtest.set_sensitive(active)
        if active:
            self.entry.set_text(self.config.glob['overrideDesktop'])
        else:
            self.entry.set_text('')
        self.save()

    def save(self, widget=None):
        self.desktop.override = self.entry.get_text()
        self.config.glob['overrideDesktop'] = self.entry.get_text()

    def testDesktop(self, button):
        self.save()
        try:
            self.desktop.open('http://okeykoclient.sourceforge.net')
        except OSError:
            pass

    def on_mapped(self, widget):
        #hack to fix the line wrap
        self.infolabel.set_size_request(self.hboxOverride.size_request()[0],-1)
        self.infolabel.set_justify(gtk.JUSTIFY_FILL)
        self.infolabel.set_line_wrap(True)
        self.infolabel.set_markup(self.markup)
