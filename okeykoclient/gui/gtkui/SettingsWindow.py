# -*- coding: utf-8 -*-
import os
import gtk

LIST = [ 
    {'stock_id' : gtk.STOCK_HOME, 'text' : 'General'},
    {'stock_id' : gtk.STOCK_SELECT_COLOR,'text' : 'Tema'},
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
        self.pageSonido = pageSonido(Control)
        self.pageEscritorio = pageEscritorio(Control)
        
        self.page_dict = [self.pageGeneral, self.pageTema, self.pageSonido, 
                          self.pageEscritorio]

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
    
class pageEscritorio(gtk.VBox):
    def __init__(self, Control):
        gtk.VBox.__init__(self)

    def save(self):
        pass
