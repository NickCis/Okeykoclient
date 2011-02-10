import gtk

class ShowEntry(gtk.Entry):
    '''Entry that shows a text, which is erase when the entry grabs focus'''
    __gsignals__ = {
        'key_press_event': 'override',
    }
    def __init__(self, showEntryText, *args):
        '''showEntryText text that is showed and removed'''
        gtk.Entry.__init__(self, *args)
        
        self.showEntryText = showEntryText
        self.KeyvalsAllowed = False
        self.KeyvalsForbid = False
        
        self.set_text(showEntryText)
        
        self.connect("focus-in-event", self.focus)
        self.connect("focus-out-event", self.focusOut)

    def focus(self, widget, event, *args):
        if self.get_text() == self.showEntryText:
            self.set_text('')

    def focusOut(self, widget, event, *args):
        text = self.get_text().lstrip()
        if text == '':
            self.set_text(self.showEntryText)

    def get_showEntryText(self):
        '''Returns showEntryText'''
        return self.showEntryText

    def set_showEntryText(self, showEntryText):
        '''Sets showEntryText'''
        self.showEntryText = showEntryText

    def set_keyvalsAllowed(self, keyvals):
        self.KeyvalsAllowed = keyvals
    def get_keyvalsAllowed(self, keyvals):
        return self.KeyvalsAllowed
    
    def set_keyvalsForbid(self, keyvals):
        self.KeyvalsForbid = keyvals
    def get_keyvalsForbid(self, keyvals):
        return self.KeyvalsForbid

    def do_key_press_event(self, event):
        if self.KeyvalsAllowed:
            if event.keyval in self.KeyvalsAllowed:
                gtk.Entry.do_key_press_event(self, event)
        elif self.KeyvalsForbid:
            if not event.keyval in self.KeyvalsForbid:
                gtk.Entry.do_key_press_event(self, event)
        else:
            gtk.Entry.do_key_press_event(self, event)
