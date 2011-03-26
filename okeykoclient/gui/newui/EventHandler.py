class EventHandler():
    def __init__(self, Control, WebView):
        self.Control = Control
        self.Config = Control['Config']
        self.Okeyko = Control['Okeyko']
        self.queueToServer = Control['queueToServer']
        self.WebView = WebView

    def action(self, uri):
        print uri
        if uri.startswith("login:"):
            self.login(uri)            
        elif uri.startswith("LoginAutoComplete"):
            self.loginAutoComplete(uri)


    def login(self, uri):
        def post_login(arg, check1, check2, check3):
            conectado, error = self.Okeyko.conectado()
            if conectado:
                print "Conecto =D"
                if check1 == "true":
                    if check2 == "true":
                        self.Config.userList[entry_text] = data[1]
                    else:
                        self.Config.userList[entry_text] = False
        data = uri[6:-1].split('|')
        self.queueToServer.put((self.Okeyko.login, (data[0], data[1]),
                              {}, post_login, (data[2],data[3],data[4]), {}))
        print data

    def loginAutoComplete(self, uri):
        if uri.startswith("LoginAutoComplete:Complete:"):
            data = uri[len("LoginAutoComplete:Complete:"):]
            avatar = self.Config.profileAvatarLoad(data, False)[1]
            passw = False
            for user in self.Config.userList:
                if user[0] == data:
                    passw = user[1]
                else:
                    break
            if passw:
                avatar = "%s', '%s" % (avatar, passw)
            js = "LoginAutoCompleteCBPy('%s')" % avatar
            self.WebView.execute_script(js)                
        else:
            data = ''
            for user in self.Config.userList:
              data = "%s '%s'," % (data, user[0])
            data = "LoginAutoComplete([%s])" % data
            self.WebView.execute_script(data)
