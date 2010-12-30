#import gtk
import time
import paths
import Queue
import threading

import inspect
import ctypes

def queue_manager(cola):
    try:
        while True:
            method, args, kwargs = cola.get(True, 0.1)
            #print 'ejecutando', method.__name__, 'con', args, kwargs
            method(*args, **kwargs)
    except Queue.Empty:
        pass

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

def getThreadId(self):
    if not self.isAlive():
        return
    # do we have it cached?
    if hasattr(self, "_thread_id"):
        return self._thread_id

    # no, look for it in the _active dict
    for tid, tobj in threading._active.items():
        if tobj is self:
            self._thread_id = tid
            return tid

def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ThreadHandler():
    def __init__(self):
        self.threadDict = {}
        
        self.queueToGui = Queue.Queue()
        self.queueToServer = Queue.Queue()
        
        threadServer = server(self.queueToServer, self.queueToGui)
        self.threadDict.update({ 'Server': threadServer })

    def setControl(self, control):
        self.__Control = control

    def setgui(self, MainWindow, Notificaciones=None):
        '''MainWindow debe tener funciones:
            set_inbox() new_inbox()
            set_outbox() new_outbox()
            set_fav()
            new_inbox()
            new_outbox()
             '''
        self.__MainWindow = MainWindow
        self.__Notifications = Notificaciones

    def startActMen(self):
        actmenThread = actmen(self.__Control)
        actmenThread.setgui(self.__MainWindow, self.__Notifications)
        self.threadDict.update({ 'ActMen': actmenThread })
        actmenThread.start()

    def kill(self, name):
        if self.threadDict.has_key(name):
            thread = self.threadDict[name]
            if thread.isAlive():
                thread.join()
                print "Thread %s killed" % name
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
        self.newThread(self.kill, ('ActMen',) )
        #return ret

    def killall(self):
        for threadName, thread in self.threadDict.iteritems():
            if thread.isAlive():
                self.kill(threadName)

    def forcekill(self, name):
        if self.threadDict.has_key(name):
            thread = self.threadDict[name]
            threadId = getThreadId(thread)
            _async_raise( threadId, threading.ThreadError)
            while thread.isAlive():
                time.sleep ( 0.1 )
                _async_raise( threadId, threading.ThreadError)
            print "Thread %s killed" % name

    def forcekillall(self):
        for threadName, thread in self.threadDict.iteritems():
            if thread.isAlive():
                self.forcekill(threadName)

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
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            try:
                method, args, kwargs, callback, cargs, ckwargs= self.colaIn.get(True, 0.1)
                #print 'serv.ejecutando', method.__name__, 'con', args, kwargs
                resultado = method(*args, **kwargs)
                cb = True
            except Queue.Empty:
                resultado = None
                cb = False
            if cb:
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
                #if (cargs) and (ckwargs):
                #    self.colaOut.put((callback, (resultado, cargs,), ckwargs))
                #elif ckwargs:
                #    self.colaOut.put((callback, (resultado,), ckwargs))
                #elif cargs:
                #    self.colaOut.put((callback, (resultado, cargs), {}))
                #else:
                #    self.colaOut.put((callback, (resultado,), {}))
            time.sleep(1)



class actmen(threading.Thread):
    ''' Thread que actualiza los mensajes y avisa si hay nuevos '''
    def __init__(self, Control):
    #def __init__(self, ventana, okeyko, cola, sound=None, notification=None, condition=None):
        '''
        okeyko = Funcion de libokeyko (creada y conectada)
        condition = Condicion que se activa al conectarse
        sound = Funcion para alerta de sonido
        notificaciones = Funcion para notificaciones OSD
        '''
        threading.Thread.__init__(self)
        self.__Control = Control
        self.__Cola = Control['queueToGui']
        self.__Okeyko = Control['Okeyko']
        #self.__Condition = condition
        self.__Condition = None
        self.__Sound = Control['Sound']
        self.__Config = Control['Config']
        self.__MinId = None
        self.loop = True
        self.setDaemon(True)
        #self.start()
        
    def setgui(self, MainWindow, Notificaciones=None):
        '''MainWindow debe tener funciones:
            set_inbox() new_inbox()
            set_outbox() new_outbox()
            set_fav()
            new_inbox()
            new_outbox()
             '''
        self.__MainWindow = MainWindow
        self.__Notifications = Notificaciones
        
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

    def run(self):
        #if self.__Condition != None:
        #    self.__Condition.acquire()
        #    self.__Condition.wait()
        #    self.__Condition.release()
        self.__Config.setCurrentUser(self.__Okeyko.getUser())

        inbox = self.__Okeyko.inbox()[:]
        try:
            self.__MinId = inbox[0][3]
        except:
            pass

        iterDownAvatar(inbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.__MainWindow.set_inbox, [inbox], {}))

        outbox = self.__Okeyko.outbox()
        iterDownAvatar(outbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.__MainWindow.set_outbox, [outbox], {}))

        favbox = self.__Okeyko.favbox()
        iterDownAvatar(favbox, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.__MainWindow.set_fav, [favbox], {}))

        pensamientos = self.__Okeyko.pensamientos()
        iterDownAvatar(pensamientos, self.__Config.avatarLoad, self.__Okeyko.avatar,\
                        self.__Config.avatarSave)

        self.__Cola.put((self.__MainWindow.set_pen, [pensamientos], {}))

        while self.loop:
            time.sleep(15) #TODO: evaluar el tiempo. Convertirlo a config
            mensajes = self.__Okeyko.inboxNew(self.__MinId)
            if mensajes != False and self.loop:
                self.__MinId = mensajes[0][3]
                iterDownAvatar(mensajes, self.__Config.avatarLoad,\
                    self.__Okeyko.avatar, self.__Config.avatarSave)
                self.__Cola.put((self.__MainWindow.new_inbox, [mensajes], {}))
                # TODO: ponerlo en forma que sea multi plataforma (usando modulo os)
                if self.__Sound != None:
                    self.__Cola.put((self.__Sound.recibido, (), {}))
                #self.__MainWindow.blink()
                if self.__Notifications != None:
                    self.__Cola.put((self.__Notifications.newNotification, \
                                        ("Mensaje Nuevo", 0), {}))
                   #notificaciones.newNotification("Mensaje Nuevo", 0, 1, color=col)
            outbox, pensamientos = self.__Okeyko.newOutPen()
            if outbox != False and self.loop:
                iterDownAvatar(outbox, self.__Config.avatarLoad,\
                    self.__Okeyko.avatar, self.__Config.avatarSave)
                self.__Cola.put((self.__MainWindow.new_outbox, [outbox], {}))

            if pensamientos != False and self.loop:
                iterDownAvatar(pensamientos, self.__Config.avatarLoad,\
                    self.__Okeyko.avatar, self.__Config.avatarSave)
                self.__Cola.put((self.__MainWindow.new_pen, [pensamientos], {}))
                if self.__Sound != None:
                    self.__Cola.put((self.__Sound.pensamiento, (), {}))   
