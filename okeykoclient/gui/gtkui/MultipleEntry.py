import gtk

class MultipleEntry(gtk.HBox):
    ''' Entry widget with to add multiple Entries'''
    
    def __init__(self):
        gtk.HBox.__init__(self)
        self.completion = None
        entry = EntryNoSpace()
        entry.connect('key_press_event', self.entryKeyPressed)
        self.pack_start(entry, False)
        self.entryList = [entry]
        
    def entryKeyPressed(self, widget, event):
        # espacio 32
        # backspace 65288
        # supr 65535
        index = self.entryList.index(widget)
        if event.keyval == 32:
            #widget.set_text("%s," % widget.get_text())
            widget.set_width_chars(len(widget.get_text()))
            entry = EntryNoSpace()
            if not self.completion is None:
                self.__set_completion(entry)
            entry.connect('key_press_event', self.entryKeyPressed)
            entry.show()
            self.pack_start(entry, False)
            entry.grab_focus()
            self.entryList.append(entry)
        elif len(widget.get_text()) == 0:
            if event.keyval == 65288 and index > 0:
                self.entryList[index - 1].grab_focus()
                self.entryList.remove(widget)
                widget.destroy()
            elif event.keyval == 65535 and index < len(self.entryList)-1 and len(self.entryList) >= 2:
                dwidget = self.entryList[index + 1]
                self.entryList.remove(dwidget)
                dwidget.destroy()

    def do_key_press_event(self, event):
        if not event.keyval == 65363 and not event.keyval == 65361:
            gtk.HBox.do_key_press_event(self, event)

    def get_text(self):       
        if len(self.entryList) == 1:
            text = self.entryList[0].get_text()
        else:
            text = []
            for entry in self.entryList:
                t = entry.get_text().replace(',','')
                if t != '':
                    text.append(entry.get_text().replace(',',''))
        return text

    def set_text(self, text):
        if type(text) == str:
            if len(self.entryList) > 1:
                for index in range(1, len(self.entryList)):
                    entry = self.entryList[index]
                    entry.destroy()
                    self.entryList.remove(entry)
            self.entryList[0].set_text(text)
        elif type(text) == tuple or type(text) == list:
            dif = len(self.entryList) - len(text)
            if dif > 0:
                for index in range(0, dif):
                    entry = self.entryList[index]
                    entry.destroy()
                    self.entryList.remove(entry)
            elif 0 > dif:
                for index in range(0, dif):
                    entry = EntryNoSpace()
                    if not self.completion is None:
                        self.__set_completion(entry)
                    entry.connect('key_press_event', self.entryKeyPressed)
                    self.pack_start(entry, False)
                    self.entryList.append(entry)
            for t in range(0, len(text)):
                self.entryList[t].set_text(text[t])

    def set_completion(self, completion):
        self.completion = completion
        for entry in self.entryList:
            self.__set_completion(entry, completion)


    def __set_completion(self, entry, completion=None):
        def match_func(completion, key, iter):
            model = completion.get_model()
            for posib in model[iter]:
                if type(posib) == str:
                    posib = posib.lower()
                    if posib.find(entry.get_text().lower()) != -1:
                        ret = True
                        break
            else:
                ret = False
            return ret    
        def completionCB(comple, model, iterC):
            #text = "%s," % model.get_value(iterC, comple.get_property('text-column'))
            text = model.get_value(iterC, comple.get_property('text-column'))
            enCB = comple.get_entry()
            enCB.set_text(text)
            enCB.set_width_chars(len(enCB.get_text()))
            index = self.entryList.index(enCB)
            if  index == len(self.entryList) -1:
                enN = EntryNoSpace()
                self.entryList.append(enN)
                enN.connect('key_press_event', self.entryKeyPressed)
                self.__set_completion(enN, comple)
                enN.show()                
                self.pack_start(enN, False)
                enN.grab_focus()
            else:
                self.entryList[index+1].grab_focus()
            return True

        if completion == None:
            completion = self.completion
        newComple = gtk.EntryCompletion()
        newComple.set_match_func(match_func)
        newComple.set_model(completion.get_model())
        newComple.set_text_column(completion.get_text_column())
        newComple.set_property("popup-set-width", False)
        newComple.connect('match-selected', completionCB)
        entry.set_completion(newComple)
        

    def show(self):
        self.show_all()        

class EntryNoSpace(gtk.Entry):
    __gsignals__ = {
        'key_press_event': 'override',
    #    'key_release_event': 'override'
    }
    def __init__(self, maxE=0):
        gtk.Entry.__init__(self, maxE)
        self.set_has_frame(False)
        
    def do_key_press_event(self, event):
        if event.keyval == 65363:
            if not self.get_property('cursor-position') == \
            self.get_text_length():
                self.set_position(self.get_property('cursor-position')+1)
                return True
            elif self.get_property('selection-bound') ==  0:
                self.set_position(0)
                return True            
        elif event.keyval == 65361:
            if not self.get_property('cursor-position') == 0:
                self.set_position(self.get_property('cursor-position')-1)
                return True
        elif not event.keyval == 32:
            gtk.Entry.do_key_press_event(self, event)

    #def do_key_release_event(self, event):
    #    self.set_width_chars(len(self.get_text()))
    #    gtk.Entry.do_key_release_event(self, event)
