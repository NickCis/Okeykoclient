#import gtk
import time
import paths
import Queue
import threading

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

class server(threading.Thread):
    ''' Recive que funcion ejecutar en thread y pone en colaOut funcion callback 
        colaIn debe ser: method, args, kwargs, callback, cargs, ckwargs
                         func, (), {}, func, (), {}
        cola out devuelve: callback, (resultado, cargs,), ckwargs
                           func, (),(), {}
    '''

    def __init__(self, colaIn, colaOut):
        threading.Thread.__init__(self)
        self.colaIn = colaIn
        self.colaOut = colaOut
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
                if (cargs) and (ckwargs):
                    self.colaOut.put((callback, (resultado, cargs,), ckwargs))
                elif ckwargs:
                    self.colaOut.put((callback, (resultado,), ckwargs))
                elif cargs:
                    self.colaOut.put((callback, (resultado, cargs), {}))
                else:
                    self.colaOut.put((callback, (resultado,), {}))
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
        self.__Cola = Control['queueToGui']
        self.__Okeyko = Control['Okeyko']
        #self.__Condition = condition
        self.__Condition = None
        self.__Sound = Control['Sound']        
        self.__MinId = None
        self.setDaemon(True)
        #self.start()
        
    def setgui(self, MainWindow, Notificaciones=None):
        '''MainWindow debe tener funciones:
            set_inbox() new_inbox()
            set_outbox() new_outbox()
             '''
        self.__MainWindow = MainWindow
        self.__Notifications = Notificaciones
        
    def thStart(self, *args, **kargs):
        self.start()

    def run(self):
        #if self.__Condition != None:
        #    self.__Condition.acquire()
        #    self.__Condition.wait()
        #    self.__Condition.release()

        inbox = self.__Okeyko.inbox()[:]
        try:
            self.__MinId = inbox[0][3]
        except:
            pass
        imgcache = {}
        for inb in inbox:
            try:
                avatar = imgcache[inb[4]]
            except:
                avatar = self.__Okeyko.avatar(inb[4])
                imgcache.update({inb[4] : avatar})
            inb[4] = avatar

        outbox = self.__Okeyko.outbox()
        for outb in outbox:
            try:
                avatar = imgcache[outb[4]]
            except:
                avatar = self.__Okeyko.avatar(outb[4])
                imgcache.update({outb[4] : avatar})
            outb[4] = avatar

        self.__Cola.put((self.__MainWindow.set_inbox, [inbox], {}))
        self.__Cola.put((self.__MainWindow.set_outbox, [outbox], {}))

        #gtk.gdk.threads_enter()
        #self.__MainWindow.set_inbox(inbox)  
        #self.__MainWindow.set_outbox(outbox)
        #gtk.gdk.threads_leave()

        while True:
            time.sleep(30)
            mensajes = self.__Okeyko.badeja_nuevos(self.__MinId)
            try: #Si no hay mensajes nuevos devuelve error
                self.__MinId = mensajes[0][3] 
                
                self.__Cola.put((self.__MainWindow.mensajes, ((mensajes), False, True,), {}))
                # TODO: ponerlo en forma que sea multi plataforma (usando modulo os)
                if self.__Sound != None:
                    self.__Cola.put((self.__Sound.play_path, \
                                        (paths.DEFAULT_THEME_PATH + \
                                        "new.wav",), {}))                               
                #self.__MainWindow.blink()
                if self.__Notification != None:
                    self.__Cola.put((self.__Notification.newNotification, \
                                        ("Mensaje Nuevo", 0), {}))
                    #notificaciones.newNotification("Mensaje Nuevo", 0, 1, color=col)
            except:
                pass
