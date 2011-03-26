import webkit

import EventHandler

class WebEngine(webkit.WebView):
    def __init__(self, Control):
        webkit.WebView.__init__(self)
        
        self.Control = Control
        self.Config = Control['Config']
        #self.EventHandler = Control['EventHandler']
        self.EventHandler = EventHandler.EventHandler(Control, self)
        
        self.load_uri("file://%s" % self.Config.pathFile('theme-main.html'))
        
        self.connect('navigation-requested', self.on_navigation_requested)
        self.connect('script-alert', self.on_script_alert)


    def on_navigation_requested(self, view, webframe, request):
        uri=request.get_uri()
        if uri.startswith("okeyko://"):
            self.okeyko_action(uri[9:])
            return True
        else:
            return False

    def on_script_alert(self, view, webframe, message):
        if message.startswith('okeyko:'):
            self.okeyko_action(message[7:])
            return True
        return False

    def okeyko_action(self, uri):
        self.EventHandler.action(uri)

    def getEventHandler(self):
        return self.EventHandler

    
