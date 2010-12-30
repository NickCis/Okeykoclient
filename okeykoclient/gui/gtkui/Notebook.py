import gtk
import gobject

class NotebookLabel(gtk.EventBox):
    __gsignals__ = {
        'img-clicked': (gobject.SIGNAL_RUN_LAST, None, () ),
        'left-click': (gobject.SIGNAL_RUN_LAST, None, (gtk.gdk.Event,) ),
        'right-click': (gobject.SIGNAL_RUN_LAST, None, (gtk.gdk.Event,) ),
        'middle-click': (gobject.SIGNAL_RUN_LAST, None, (gtk.gdk.Event,) ),
    }
    def __init__(self, textlabel, stockid, size=gtk.ICON_SIZE_MENU):
        gtk.EventBox.__init__(self)
        #gtk.HBox.__init__(self, False, 0)
        self.HBox = gtk.HBox(False, 0)

        self.label = gtk.Label(textlabel)

        iconBox = gtk.HBox(False, 0)
        image = gtk.image_new_from_stock(stockid, size)
        iconBox.pack_start(image, True, False, 0)
        iconBox.show()
        
        self.button = gtk.Button()
        self.button.add(iconBox)
        self.button.set_property('relief', gtk.RELIEF_NONE)
        settings = self.button.get_settings()
        (w,h) = gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_MENU)
        self.button.set_size_request(w + 4, h + 7)

        self.button.connect('clicked', self.__imgClicked)
       
        self.HBox.pack_start(self.label)
        self.HBox.pack_end(self.button, True, False, 0)        

        self.connect("button-press-event", self.__butoonPressCB)
        self.add(self.HBox)
        self.show_all()

    def set_text(self, text):
        self.label.set_text(text)

    def get_text(self):
        return self.label.get_text()

    def __imgClicked(self, button, *args, **kargs):
        self.emit("img-clicked")

    def __butoonPressCB(self, widget, event):
        if event.button == 1:
            self.emit('left-click', event)
        elif event.button == 2:
            self.emit('middle-click', event)
        elif event.button == 3:
            self.emit('right-click', event)

    def pack_start(self, child, expand=True, fill=True, padding=0):
        self.HBox.pack_start(child, expand, fill, padding)

    def pack_end(self, child, expand=True, fill=True, padding=0):
        self.HBox.pack_end(child, expand, fill, padding)

class Notebook(gtk.Notebook):
    def __init__(self, redrawActionGroup):
        gtk.Notebook.__init__(self)
        
        self.redrawActionGroup = redrawActionGroup
        self.dictTabs = {}
        self.dictOverr = {}

        self.set_property('scrollable', True)
        self.set_tab_pos(gtk.POS_TOP)
        self.set_size_request(300,-1)

    def append_page(self, child, tab_label=None, connects=None, append=True):
        label = self.__pend_page(child, tab_label, connects)
        if append:
            gtk.Notebook.append_page(self, child, label)
            self.set_tab_reorderable(child, True)

    def prepend_page(self, child, tab_label=None, connects=None, append=True):
        label = self.__pend_page(child, tab_label, connects)
        if append:
            gtk.Notebook.prepend_page(self, child, label)
            self.set_tab_reorderable(child, True)

    def __pend_page(self, child, tab_label=None, connects=None):
        if type(tab_label) in (list, tuple):
            tab_label, tab_label_name = tab_label
            self.dictOverr.update({ tab_label_name: tab_label})
        else:
            tab_label, tab_label_name = tab_label, tab_label
            if self.dictOverr.has_key(tab_label_name):
                self.dictOverr.pop(tab_label_name)
        label = NotebookLabel(tab_label, gtk.STOCK_CLOSE)
        self.dictTabs.update({ tab_label_name: (label, child) })
        self.set_tab_reorderable(child, True)
        try:
            if type(connects) in (list, tuple):
                for con in connects:
                    if type(con) in (list, tuple):
                        label.connect(*con)
                    else:
                        label.connect(*connects)
                        break
            elif type(connects) != None:
                print "Exception in append_page connects wrong type"
        except:
            print "Exception in append_page while connecting"
        return label
            
    def showHideTab(self, name=None, page_num=None, toggleAction=False):
        def showHideTab(name=None, page_num=None):
            if name != None:
                #if name == 'tabR' or name == 'tabE' or name == 'tabF' or name == 'tabP':
                if self.dictOverr.has_key(name):
                    #nameinlab = self.dictTabs[name][0].get_text()
                    nameinlab = self.dictOverr[name]
                else:
                    nameinlab = name
                for npage in range(0, self.get_n_pages()):
                    page = self.get_nth_page(npage)
                    pagelabel = self.get_tab_label(page)
                    if pagelabel.get_text() == nameinlab:
                        self.dictTabs.update({ name: (pagelabel, page)  })
                        self.remove_page(npage)
                        break
                else:
                    if self.dictTabs.has_key(name):
                        tablabel, tabchild = self.dictTabs[name]
                        self.insert_page(tabchild, tablabel)
                        self.set_tab_reorderable(tabchild, True)
                        #gtk.Notebook.append_page(self, tabchild, tablabel)
                        tablabel.show_all()
                        tabchild.show_all()
                        #self.show_all()
                    else:
                        print "Exepction while showing tabs, no existe tab %s" % name
                        return
                
            elif page_num != None and page_num <= self.get_n_pages():
                page = self.get_nth_page(page_num)
                pagelabel = self.get_tab_label(page)
                pagelabelname = pagelabel.get_text()
                #for a in ('tabR', 'tabE', 'tabF', 'tabP'):
                for a, b in self.dictOverr.iteritems():
                    #if pagelabelname == self.dictTabs[a][0].get_text():
                    if pagelabelname == b:
                        nameput = a
                        break
                else:
                    nameput = pagelabelname
                self.dictTabs.update({ nameput: (pagelabel, page)  })
                self.remove_page(page_num)
            else:
                print 'Exception in showHideTab No name of page_num set'
        if toggleAction:
            showHideTab(name=name, page_num=page_num)
        else:
            if page_num != None and name == None:
                page = self.get_nth_page(page_num)
                pagelabel = self.get_tab_label(page)
                pagelabelname = pagelabel.get_text()
                for a, b in self.dictOverr.iteritems():
                    if pagelabelname == b:
                        nameput = a
                        break
                else:
                    nameput = pagelabelname
            elif name != None:
                pagelabelname = name
            else:
                print 'Exception in showHideTab No name of page_num set'
                return
            act = self.redrawActionGroup.get_action(pagelabelname)
            if act != None:
                active = False if (act.get_active()) else True
                act.set_active(active)
            else:
                showHideTab(name=name, page_num=page_num)
