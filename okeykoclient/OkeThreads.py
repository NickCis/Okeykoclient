import time
import paths
import Queue
import threading
from urllib2 import URLError, HTTPError #Handling exceptions
import HTTPResponses #Handling exceptions

#import inspect
#import ctypes

def queue_manager(cola):
    try:
        while True:
            method, args, kwargs = cola.get(True, 0.1)
            #print 'ejecutando', method.__name__, 'con', args, kwargs
            method(*args, **kwargs)
    except Queue.Empty:
        pass

    except Exception, exception:
        print 'Exception queue_manager file OkeThreads.py line: 17:'
        print "    'method(*args, **kwargs)' %s" % exception
        try:
            print "    'method'", method
        except:
            print "    'method' not setted"
        try:
            print "    'args'", args
        except:
            print "    'args' not setted"
        try:
            print "    'kwargs'", kwargs
        except:
            print "    'kwargs' not setted"
    return True

def queue_maker():
    return Queue.Queue(), Queue.Queue()

def iterDownAvatar(store, Load, Down, Save):
    if store == None:
        return
    for st in store:
        avE, avatar = Load(st[4], False)
        if not avE:
            avatar = Down(st[4])
            Save(st[4], avatar)

#def getThreadId(self):
#    if not self.isAlive():
#        return
#    # do we have it cached?
#    if hasattr(self, "_thread_id"):
#        return self._thread_id

#    # no, look for it in the _active dict
#    for tid, tobj in threading._active.items():
#        if tobj is self:
#            self._thread_id = tid
#            return tid

#def _async_raise(tid, exctype):
#    '''Raises an exception in the threads with id tid'''
#    if not inspect.isclass(exctype):
#        raise TypeError("Only types can be raised (not instances)")
#    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
#    if res == 0:
#        raise ValueError("invalid thread id")
#    elif res != 1:
#        # """if it returns a number greater than one, you're in trouble, 
#        # and you should call it again with exc=NULL to revert the effect"""
#        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
#        raise SystemError("PyThreadState_SetAsyncExc failed")


class ThreadHandler():
    def __init__(self):
        self.threadDict = {}
        
        self.queueToGui = Queue.Queue()
        self.queueToServer = Queue.Queue()
        
        threadServer = server(self.queueToServer, self.queueToGui)
        self.threadDict.update({ 'Server': threadServer })

    def setControl(self, control):
        self.__Control = control

    def ActMenConnect(self, action, callback):
        ''' Connects de actions: newInbox newPensamiento newOutbox'''
        self.threadDict['ActMen'].connect(action, callback)

    def Connect(self, action, callback):
        ''' Connects de actions: newInbox newPensamiento newOutbox'''
        if action == 'setError':
            self.threadDict['ActMen'].connect(action, callback)
            self.threadDict['Server'].connect(action, callback)

    def createActMen(self):
        actmenThread = actmen(self.__Control)
        #actmenThread.setgui(self.__MainWindow, self.__Notifications)
        self.threadDict.update({ 'ActMen': actmenThread })
        
    def startActMen(self):
        self.threadDict['ActMen'].start()

    def kill(self, name):
        if self.threadDict.has_key(name):
            thread = self.threadDict[name]
            if thread.isAlive():
                thread.join()
                print "Thread '%s' killed" % name
                return True
            else:
                return False
        else:
            print "No existe thread llamado: %s" % (name,)
            return False

    def killActMen(self):
        actmenThread = self.threadDict['ActMen']
        actmenThread.loop = False
        #ret = self.kill('ActMen')
        #self.newThread(self.kill, ('ActMen',) )
        self.queueToServer.put( (self.kill, ('ActMen',), {}, lambda x: x, (), {} ) )
        #return ret

    def killall(self):
        for threadName, thread in self.threadDict.iteritems():
            if thread.isAlive():
                self.kill(threadName)

    #def forcekill(self, name):
    #    if self.threadDict.has_key(name):
    #        thread = self.threadDict[name]
    #        threadId = getThreadId(thread)
    #        _async_raise( threadId, threading.ThreadError)
    #        while thread.isAlive():
    #            time.sleep ( 0.1 )
    #            _async_raise( threadId, threading.ThreadError)
    #        print "Thread %s killed" % name

    #def forcekillall(self):
    #    for threadName, thread in self.threadDict.iteritems():
    #        if thread.isAlive():
    #            self.forcekill(threadName)

    def newThread(self, target, args=(), kargs={}, name=None):
        if name == None:
            name = "NewThread-%s" % len(self.threadDict)
        new = threading.Thread(target=target, args=args, name=name)
        new.setDaemon(True)
        self.threadDict.update({ name: new })
        new.start()
        return name, new

class server(threading.Thread):
    ''' Recibe que funcion ejecutar en thread y pone en colaOut funcion callback 
        colaIn debe ser: method, args, kwargs, callback, cargs, ckwargs
                         func, (), {}, func, (), {}
        cola out devuelve: callback, (resultado, cargs,), ckwargs
                           func, (),(), {}
    '''

    def __init__(self, colaIn, colaOut):
        threading.Thread.__init__(self)
        self.colaIn = colaIn
        self.colaOut = colaOut
        self.errorCB = lambda *x, **y: 1
        self.setDaemon(True)
        self.start()

    def connect(self, action, callback):
        if action == 'setError':
            self.errorCb = callback

    def run(self):
        while True:
            try:
                method, args, kwargs, callback, cargs, ckwargs= self.colaIn.get(True, 0.1)
                #print 'serv.ejecutando', method.__name__, 'con', args, kwargs
                try: #Evoids server crashing
                    resultado = method(*args, **kwargs)
                    if cargs:
                        resul = [resultado]
                        for arg in cargs:
                            resul.append(arg)
                        resultado = tuple(resul)
                    else:
                        resultado = (resultado,)
                    if not ckwargs:
                        ckwargs = {}
                    self.colaOut.put((callback, resultado, ckwargs))                    
                except HTTPError, e:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                    resp = HTTPResponses.responses[e.code]
                    error = "%s : %s \n %s" % (e.code, resp[0], resp[1])
                    print error
                    self.errorCB(error)
                except URLError, e:
                    print 'We failed to reach a server.'
                    print 'Reason: ', e.reason
                    self.errorCB(e.reason)
                except Exception, exception:
                    print 'Exception in Server file OkeThreads.py line 176:'
                    print "    'resultado = method(*args, **kwargs)'"
                    print exception
                    try:
                        print "    'method'", method
                    except:
                        print "    'method' not setted"
                    try:
                        print "    'args'", args
                    except:
                        print "    'args' not setted"                    
                    try:
                        print "    'kwargs'", kwargs
                    except:
                        print "    'kwargs' not setted"
                    try:
                        print "    'callback'", cargs
                    except:
                        print "    'callback' not setted"
                    try:
                        print "    'ckwargs'", ckwargs
                    except:
                        print "    'ckwargs' not setted"
            except Queue.Empty:
                time.sleep(1)



class actmen(threading.Thread):
    ''' Thread que actualiza los mensajes y avisa si hay nuevos '''
    def __init__(self, Control):
        ''' Control, diccionario. actmen requiere solo de Okeyko y queueToGui'''
        threading.Thread.__init__(self)
        self.__Control = Control
        self.__Cola = Control['queueToGui']
        self.__Okeyko = Control['Okeyko']
        self.__Condition = None
        #self.__Sound = Control['Sound']
        #self.__Config = Control['Config']
        self.__MinId = None
        self.loop = True
        self.errorCB = lambda *x, **y: 1
        self.setInCB = lambda *x, **y: 1
        self.setPenCB = lambda *x, **y: 1
        self.setOutCB = lambda *x, **y: 1
        self.setFavCB = lambda *x, **y: 1
        self.newInCB = lambda *x, **y: 1
        self.newPenCB = lambda *x, **y: 1
        self.newOutCB = lambda *x, **y: 1
        self.setDaemon(True)
        #self.start()
        
    #def setgui(self, MainWindow, Notificaciones=None):
    #    '''MainWindow debe tener funciones:
    #        set_inbox() new_inbox()
    #        set_outbox() new_outbox()
    #        set_fav()
    #        new_inbox()
    #        new_outbox()
    #         '''
    #    self.__MainWindow = MainWindow
    #    self.__Notifications = Notificaciones
        
    def thStart(self, *args, **kargs):
        while self.isAlive():
            threading.Thread(target=self.join)
            time.sleep(1)
        try:
            self.start()
        except:
            MainWindow = self.__MainWindow
            Notifications = self.__Notifications
            Control = self.__Control
            self.join()
            self = actmen(Control)
            self.__MainWindow = MainWindow
            self.__Notifications = Notifications
            self.start()

    def thStop(self, *args, **kargs):
        self.loop = False
        threading.Thread(target=self.join)

    def connect(self, action, callback):
        if action == 'setError':
            self.errorCb = callback
        elif action == 'setInbox':
            self.setInCB = callback
        elif action == 'setPensamiento':
            self.setPenCB = callback
        elif action == 'setOutbox':
            self.setOutCB = callback
        elif action == 'setFavorito':
            self.setFavCB = callback
        elif action == 'newInbox':
            self.newInCB = callback
        elif action == 'newPensamiento':
            self.newPenCB = callback
        elif action == 'newOutbox':
            self.newOutCB = callback

    def run(self):
        try:
            realRun()
        except HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            resp = HTTPResponses.responses[e.code]
            error = "%s : %s \n %s" % (e.code, resp[0], resp[1])
            print error
            self.errorCB(error)
        except URLError, e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            self.errorCB(e.reason)

    
    def realRun(self):
        self.__Config.setCurrentUser(self.__Okeyko.getUser())

        inbox = self.__Okeyko.inbox()[:]
        try:
            self.__MinId = inbox[0][3]
        except:
            pass

        self.__Config.profileAvatarSave(*self.__Okeyko.avatarinfo()) #SavesUserAva
        
        iterDownAvatar(inbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.setInCB, [inbox], {}))

        outbox = self.__Okeyko.outbox()
        iterDownAvatar(outbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.setOutCB, [outbox], {}))

        favbox = self.__Okeyko.favbox()
        iterDownAvatar(favbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.setFavCB, [favbox], {}))

        pensamientos = self.__Okeyko.pensamientos()
        iterDownAvatar(pensamientos, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.setPenCB, [pensamientos], {}))

        while self.loop:
            wait = 0
            while self.loop and wait <= 15: #TODO: Convertirlo a config
                time.sleep(1)
                wait += 1
            if self.loop:
                mensajes = self.__Okeyko.inboxNew(self.__MinId)
                if mensajes != False and self.loop:
                    self.__MinId = mensajes[0][3]
                    iterDownAvatar(mensajes, self.__Config.avatarLoad,\
                        self.__Okeyko.avatar, self.__Config.avatarSave)
                    self.__Cola.put((self.newInCB, [mensajes], {}))
            if self.loop:
                if self.__Okeyko.inboxNew() == False: #TODO: HACK: prevenir poner mensajes nuevos como leidos
                    outbox, pensamientos = self.__Okeyko.newOutPen()
                    if outbox != False and self.loop:
                        iterDownAvatar(outbox, self.__Config.avatarLoad,\
                            self.__Okeyko.avatar, self.__Config.avatarSave)
                        self.__Cola.put((self.newOutCB, [outbox], {}))            
                    if pensamientos != False and self.loop:
                        iterDownAvatar(pensamientos, self.__Config.avatarLoad,\
                            self.__Okeyko.avatar, self.__Config.avatarSave)
                    self.__Cola.put((self.newPenCB, [pensamientos], {}))
