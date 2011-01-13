# -*- coding: utf-8 -*-
import gtk
CAN_PYNOTIFY = True
try:
    import pynotify    
except:
    CAN_PYNOTIFY = False

import gtkPopupNotify
import EmeseneNotification

class MainClass:
    def __init__(self, Control):
        ''' Constructor '''
		# TODO: Agregar soporte de themes
        #self.theme = controller.theme
        self.Config = Control['Config']
        self.Config.glob['notCanPyNotify'] = CAN_PYNOTIFY
        #self.updateConfig()


    def updateConfig(self):
        '''args:
            string, pos, scroll, pixmap = None,
            closePixmap = None, callback = None, params = None,
            userPixbuf = None, font = None, color = None, duration= 7'''

        self.corner = int(self.Config.user['notCorner'])
        self.scroll = int(self.Config.user['notScroll'])
        self.offset = self.Config.user['notOffset']
        self.height = self.Config.user['notHeight']
        self.width = self.Config.user['notWidth']
        self.font = self.Config.user['notFont']
        self.color = self.Config.user['notColor']
        #self.NotiCol = '#%02X%02X%02X' % (00, 00, 00)
        self.NotiCol = self.Config.user['notColor']
        #NotiPixmapF = paths.DEFAULT_THEME_PATH + "guif.png"
        NotiPixmapF = self.Config.pathFile('Not-guif.png')
        self.NotiPixmap, NotiPMask = gtk.gdk.pixbuf_new_from_file(NotiPixmapF).render_pixmap_and_mask()
        NotiPixmapCloseF = self.Config.pathFile('Not-close.png')
        self.NotiClosePixmap = gtk.gdk.pixbuf_new_from_file(NotiPixmapCloseF)
        self.notShowTime = int(self.Config.user['notShowTime'])
        self.notType = int(self.Config.user['notType'])
        if self.notType == 2:
            self.GtkNotify = False
            self.PyNotify = True
            self.EmeNotify = False
        elif self.notType == 1:
            self.GtkNotify = True
            self.PyNotify = False
            self.EmeNotify = False
        else:
            self.GtkNotify = False
            self.PyNotify = False
            self.EmeNotify = True
        if CAN_PYNOTIFY:
            pynotify.init('okeykoclient')
        self.Noti = EmeseneNotification.NotificationManager(128, 200)
        self.GtkNoti = gtkPopupNotify.NotificationStack(size_x=320, size_y=83, sep_y=10)
        self.GtkNoti.timeout = self.notShowTime

    def pyNotification(self, string, title=None, callback=None, params=None, userPixbuf=None):
        if CAN_PYNOTIFY:
            if userPixbuf:
                userpixbufPath = self.Config.avatarLoad(userPixbuf, False)[1]
            else:
                userpixbufPath = self.Config.pathFile('theme-logo.png')
            userPixbuf = gtk.gdk.pixbuf_new_from_file(userpixbufPath)
            #userPixbuf = resizePixbuf(userPixbuf, 48, 48)                
            title = 'Okeyko Client' if (not title) else title
            Noti = pynotify.Notification(title, string)
            Noti.set_hint_string ("x-canonical-append", "allowed")
            Noti.set_icon_from_pixbuf(userPixbuf)
            Noti.show()

    def gtkNotification(self, string, title=None, callback=None, params=None,
                        userPixbuf=None, timeout=7):
        if userPixbuf:
            userpixbufPath = gtk.gdk.pixbuf_new_from_file_at_size(
                             self.Config.avatarLoad(userPixbuf, False)[1], 48,48)
        else:
            userpixbufPath = self.Config.pathFile('theme-logo.png')
        if not title:
            title = "Okeyko Client"
        if self.corner == 0:
            corner = (True, True)
        elif self.corner == 1:
            corner = (False, True)
        elif self.corner == 2:
            corner = (True, False)
        else:
            corner = (False, False)
        self.GtkNoti.corner = corner
        self.GtkNoti.timeout = timeout
        self.GtkNoti.fg_color = gtk.gdk.color_parse(self.color)
        self.GtkNoti.bg_pixmap = self.Config.pathFile('Not-back.png')
        self.GtkNoti.close_but = False
        self.GtkNoti.fontdesc = self.font
        self.GtkNoti.edge_offset_y = 30
        self.GtkNoti.edge_offset_x = 10
        self.GtkNoti.new_popup(title, string, userpixbufPath, callback, rightCb=lambda *x: 0)

    def newNotification(self,string,dura=7):   
        if self.Config.user['enableNot']:
            if self.PyNotify and CAN_PYNOTIFY:
                Noti = pynotify.Notification('Okeyko Client', string, 'okeykoclient')
                Noti.show()
            elif self.GtkNotify:
                self.gtkNotification(string)
            else:
                self.Noti.newNotification(string, self.corner, self.scroll, self.NotiPixmap, self.NotiClosePixmap, color=self.NotiCol, duration=dura)


    def mensajeNew(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowRecibido'] and self.Config.user['enableNot']:
            string = "Has recibido un mensaje de %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(text, string, callback, params, userPixbuf)
            elif self.GtkNotify:
                self.gtkNotification(text, string, callback, params, userPixbuf, 999)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, self.notShowTime)
    def pensamientoNew(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowPensamiento'] and self.Config.user['enableNot']:
            string = "Nuevo Pensamiento de %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(text, string, callback, params, userPixbuf)
            elif self.GtkNotify:
                self.gtkNotification(text, string, callback, params, userPixbuf)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, self.notShowTime)
    def enviar(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowEnviar'] and self.Config.user['enableNot']:
            string = "Mensaje enviado a %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(string, text, callback, params, userPixbuf)
            elif self.GtkNotify:
                self.gtkNotification(string, text, callback, params, userPixbuf)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, self.notShowTime)

    def preview(self, pos, scroll, font, color, theme, nottype=0):
        if self.Config.user['enableNot']:
            string = "Ejemplo de Notificacion en Pantalla"
            if int(nottype) == 2 and CAN_PYNOTIFY:
                self.pyNotification(string, title="Ejemplo")
            elif int(nottype) == 1:
                self.gtkNotification(string, title="Ejemplo")
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.pathFile(
                             'theme-logo.png'))                
                NotiPixmapF = self.Config.themePathFile(theme, 'guif.png')
                notipx, NotiPMask = gtk.gdk.pixbuf_new_from_file(NotiPixmapF).render_pixmap_and_mask()
                NotiPixmapCloseF = self.Config.themePathFile(theme, 'close.png')
                closepx = gtk.gdk.pixbuf_new_from_file(NotiPixmapCloseF)
                self.Noti.newNotification(string, pos, scroll,\
                                    notipx, closepx,\
                                    None, None, userPixbuf, font,\
                                    color, 7)
