import gtk
import gobject

#class NotebookLabel(gtk.HBox):
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
        
        
