# -*- coding: utf-8 -*-

#   This file was taken from emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

import gtk
import time
import gobject
import pango
import os

CAN_PYNOTIFY = True
try:
    import pynotify    
except:
    CAN_PYNOTIFY = False
#import Plugin
#import dialog
#import desktop

#import paths
#from emesenelib.common import escape
#from emesenelib.common import unescape
#from Theme import resizePixbuf

# Replacing the use of from emesenelib.common import escape
import xml.sax.saxutils
dic = {
    '\"'    :    '&quot;',
    '\''    :    '&apos;'
}
def escape(string):
    return xml.sax.saxutils.escape(string, dic)

#Replacing the use of from Theme import resizePixbuf
def resizePixbuf(pixbuf, height, width):
    pWidth, pHeight = pixbuf.get_width(), pixbuf.get_height()
    
    if pWidth == width and pHeight == height:
        return pixbuf
            
    destX = destY = 0
    destWidth, destHeight = width, height
    if pWidth > pHeight:
        scale = float(width) / pWidth
        destHeight = int(scale * pHeight)
        destY = int((height - scale * pHeight) / 2)
    elif pHeight > pWidth:
        scale = float(height) / pHeight
        destWidth = int(scale * pWidth)
        destX = int((width - scale * pWidth) / 2)
    else:
        return pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
    
    if scale == 1:
        return pixbuf
    
    scaled = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
    pixbuf.scale(scaled, 0, 0, width, height, \
                    destX, destY, scale, scale, \
                    gtk.gdk.INTERP_BILINEAR)
    return scaled

growFactor = 20 # the number of pixels to grow every iteration

# This code is used only on Windows to get the location on the taskbar
taskbarOffsety = 0
taskbarOffsetx = 0
if os.name == "nt":
    import ctypes
    from ctypes.wintypes import RECT, DWORD
    user = ctypes.windll.user32
    MONITORINFOF_PRIMARY = 1
    HMONITOR = 1

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', DWORD),
            ('rcMonitor', RECT),
            ('rcWork', RECT),
            ('dwFlags', DWORD)
            ]

    taskbarSide = "bottom"
    taskbarOffset = 30
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(info)
    info.dwFlags =  MONITORINFOF_PRIMARY
    user.GetMonitorInfoW(HMONITOR, ctypes.byref(info))
    if info.rcMonitor.bottom != info.rcWork.bottom:
        taskbarOffsety = info.rcMonitor.bottom - info.rcWork.bottom
    if info.rcMonitor.top != info.rcWork.top:
        taskbarSide = "top"
        taskbarOffsety = info.rcWork.top - info.rcMonitor.top
    if info.rcMonitor.left != info.rcWork.left:
        taskbarSide = "left"
        taskbarOffsetx = info.rcWork.left - info.rcMonitor.left
    if info.rcMonitor.right != info.rcWork.right:
        taskbarSide = "right"
        taskbarOffsetx = info.rcMonitor.right - info.rcWork.right



class PixmapDialog(gtk.Dialog):
    '''a dialog to set Notification Pixmap'''
    def __init__(self, filename, font, color, online, offline, \
                newMsg, typing, newMail, started, idle, position, scroll):

        gtk.Dialog.__init__(self , _('Notification Config'), None, \
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, \
            gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
        self.set_border_width(4)
        self.set_position(gtk.WIN_POS_CENTER)
        self.vbox.set_spacing(4)

        self.filename = filename
        self.fontdesc = font
        self.FColor = color

        self.set_property('can-focus', False)
        self.set_property('accept-focus', False)

        self.hbox = gtk.HBox()
        self.lbox = gtk.HBox()

        self.image = gtk.Image()

        self.sample = gtk.Label()
        self.sample.set_label('<span foreground="%s">%s</span>' % \
            (self.FColor, _('Sample Text')))
        self.sample.set_use_markup(True)

        try:
            self.sample.modify_font(pango.FontDescription(self.fontdesc))
        except:
            print 'Font Error'

        self.fontlabel = gtk.Label(_("Font: "))

        self.fonttype = gtk.ToolButton()
        self.fonttype.set_stock_id(gtk.STOCK_SELECT_FONT)

        self.fontColor = gtk.ToolButton()
        self.fontColor.set_stock_id(gtk.STOCK_SELECT_COLOR)

        self.updateImage()

        self.button = gtk.Button(_('Image'))

        self.hbox.pack_start(self.image)
        self.hbox.pack_start(self.button)

        self.lbox.pack_start(self.fontlabel, False, False, 5)
        self.lbox.pack_start(self.fonttype, False, False)
        self.lbox.pack_start(self.fontColor, False, False)
        self.lbox.pack_start(self.sample, True, True)

        self.vbox.pack_start(self.hbox)
        self.vbox.pack_start(self.lbox)

        self.button.connect('clicked', self.clickPixmap)
        self.fonttype.connect('clicked', self.clickFont)
        self.fontColor.connect('clicked', self.clickColor)

        self.chbuOnline = gtk.CheckButton(_('Notify when someone gets online'))
        self.chbuOnline.set_active(online)
        self.chbuOffline = gtk.CheckButton(_('Notify when someone gets offline'))
        self.chbuOffline.set_active(offline)
        self.chbuNewMail = gtk.CheckButton(_('Notify when receiving an email'))
        self.chbuNewMail.set_active(newMail)
        self.chbuTyping = gtk.CheckButton(_('Notify when someone starts typing'))
        self.chbuTyping.set_active(typing)
        self.chbuNewMsg = gtk.CheckButton(_('Notify when receiving a message'))
        self.chbuNewMsg.set_active(newMsg)
        self.chbuStarted = gtk.CheckButton(_('Don`t notify if conversation is started'))
        self.chbuStarted.set_active(started)
        self.chbuIdle = gtk.CheckButton(_('Disable notifications when busy'))
        self.chbuIdle.set_active(idle)

        self.lblPos = gtk.Label()
        self.lblPos.set_label(_('Position'))
        self.coboPosition = gtk.combo_box_new_text()
        self.coboPosition.append_text(_('Top Left'))
        self.coboPosition.append_text(_('Top Right'))
        self.coboPosition.append_text(_('Bottom Left'))
        self.coboPosition.append_text(_('Bottom Right'))
        self.coboPosition.set_active(position)

        self.pbox = gtk.HBox()
        self.pbox.pack_start(self.lblPos)
        self.pbox.pack_start(self.coboPosition)

        self.lblScr = gtk.Label()
        self.lblScr.set_label(_('Scroll'))
        self.coboScroll = gtk.combo_box_new_text()
        self.coboScroll.append_text(_('Horizontal'))
        self.coboScroll.append_text(_('Vertical'))
        self.coboScroll.set_active(scroll)

        self.sbox = gtk.HBox()
        self.sbox.pack_start(self.lblScr)
        self.sbox.pack_start(self.coboScroll)

        self.vbox.pack_start(self.chbuOnline)
        self.vbox.pack_start(self.chbuOffline)
        self.vbox.pack_start(self.chbuNewMail)
        self.vbox.pack_start(self.chbuTyping)
        self.vbox.pack_start(self.chbuNewMsg)
        self.vbox.pack_start(self.chbuStarted)
        self.vbox.pack_start(self.chbuIdle)
        self.vbox.pack_start(self.pbox)
        self.vbox.pack_start(self.sbox)

        self.show_all()
        
    def updateImage(self):
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.filename)
            pixbuf = resizePixbuf(pixbuf, 128, 200)
            self.image.set_from_pixbuf(pixbuf)
            self.image.show()
        except:
            self.filename = None
            self.image.hide()

    def clickPixmap(self, arg):
        def _on_image_selected(response, path):
            if response == gtk.RESPONSE_ACCEPT:
                self.filename = path
                self.updateImage()

        dialog.ImageChooser(paths.HOME_DIR, _on_image_selected).run()

    def clickFont(self, arg):
        fontDialog = gtk.FontSelectionDialog(_('Choose a font'))
        if self.fontdesc != None:
            fontDialog.set_font_name(self.fontdesc)
        response = fontDialog.run()
        if response == gtk.RESPONSE_OK:
            pangoDesc = pango.FontDescription(fontDialog.get_font_name())
            self.sample.modify_font(pangoDesc)
            self.fontdesc = pangoDesc.to_string()
        fontDialog.destroy()

    def clickColor(self, arg):
        colorDialog = gtk.ColorSelectionDialog(_('Choose a color'))
        colorDialog.colorsel.set_has_palette(True)
        response = colorDialog.run()
        if response == gtk.RESPONSE_OK:
            color = colorDialog.colorsel.get_current_color()
            red = color.red >> 8
            green = color.green >> 8
            blue = color.blue >> 8
            self.FColor = '#%02X%02X%02X' % (red, green, blue)
            self.sample.set_label('<span foreground="%s">%s</span>' % \
                    (self.FColor, _('Sample Text')))
            self.sample.set_use_markup(True)
        colorDialog.destroy()

    def get_config_values(self):
        return [self.filename, self.fontdesc, self.FColor, \
                 int(self.chbuOnline.get_active()), \
                 int(self.chbuOffline.get_active()), \
                 int(self.chbuNewMsg.get_active()), \
                 int(self.chbuTyping.get_active()), \
                 int(self.chbuNewMail.get_active()), \
                 int(self.chbuStarted.get_active()), \
                 int(self.chbuIdle.get_active()), \
                 self.coboPosition.get_active(), \
                 self.coboScroll.get_active()]

class NotificationManager:
    ''' This class manages the creation display and destruction of the notifications. '''

    def __init__(self, defaultHeight = 128, defaultWidth = 200):
        ''' Contructor '''

        self.defaultHeight = defaultHeight
        self.defaultWidth = defaultWidth

        self.offset = 0

        #[[Notification, timestamp], [Notification, timestamp]]
        #[[Notification, timestamp, duration], [Notification, timestamp, duration]]
        self.list = []

        self.animate = None

    def newNotification(self, string, pos, scroll, pixmap = None, \
                closePixmap = None, callback = None, params = None, \
                userPixbuf = None, font = None, color = None, duration= 7):
        '''
        create a new notification, pixmap is the background image (as a pixbuf),
        closepixmap is a pixbuf for the close button.
        callback is the method that will be called when the message in the Notification
        is clicked
        '''
        if pixmap != None:
            width, height = pixmap.get_size()
        else:
            width = self.defaultWidth
            height = self.defaultHeight

        rgb = gtk.gdk.screen_get_default().get_rgb_colormap()
        gtk.widget_push_colormap(rgb)
        g = Notification(pos, scroll, self.offset, string, height, width, \
                pixmap, closePixmap, callback, params, userPixbuf, font, color)
        g.show()
                
        gtk.widget_pop_colormap()

        self.offset = g.getOffset()

        #self.list.append([g, int(time.time())])
        self.list.append([g, int(time.time()), duration])


        if len(self.list) <= 1:
            self.animate = gobject.timeout_add(100, self.refresh)

    def refresh(self):
        '''
        check which notifications should be closed
        resize and move notifications
        '''

        self.offset = 0

        if self.list == []:
            return False
        else:
            timestamp = int(time.time())
            count = 0
            for i in self.list:

                if not i[0].get_property('visible'):
                    del self.list[count]
#                elif i[1] + 7 <= timestamp:
                elif (i[1] + i[2] <= timestamp) & (i[2] > 0):
                    i[0].hide()
                    del self.list[count]
                else:
                    self.list[count][0].grow(self.offset)
                    self.offset = self.list[count][0].getOffset()

                count += 1

            return True

    def closeAll(self):
        ''' close all the notifications '''

        if self.animate:
            gobject.source_remove(self.animate)

        for i in range(len(self.list)):
            self.list[i][0].hide()

        self.offset = 0
        self.list = []

class Notification(gtk.Window):
    def callbackrealize(self,widget, pixmap):
        self.window.set_back_pixmap(pixmap, False)
        return True        

    def __init__(self, corner, scroll, offset, string, height = 128, \
                width = 200, pixmap = None, closePixmap = None, \
                callback = None, params = None, userPixbuf = None, \
                font = None, color = None):

        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)    

        if corner == 0:
            self.set_gravity(gtk.gdk.GRAVITY_NORTH_WEST)
        elif corner == 1:
            self.set_gravity(gtk.gdk.GRAVITY_NORTH_EAST)
        elif corner == 2:
            self.set_gravity(gtk.gdk.GRAVITY_SOUTH_WEST)
        else:
            self.set_gravity(gtk.gdk.GRAVITY_SOUTH_EAST)

        #self.set_accept_focus(False)
        #self.set_decorated(False)
        #self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_UTILITY)

        self.corner = corner
        self.scroll = scroll

        if scroll == 0:
            self.height = height
            self.max = width
            self.width = 1
        else:
            self.width = width
            self.max = height
            self.height = 1

        self.callback = callback

        self.set_geometry_hints(None, min_width=-1, min_height=-1, \
                max_width=width, max_height=height)
        if pixmap != None:
            self.set_app_paintable(True)
            #self.realize()            
            #self.window.set_back_pixmap(pixmap, False)
            #self.connect("realize", self.callbackrealize, pixmap)
            self.connect_after("realize", self.callbackrealize, pixmap)

        messageLabel = gtk.Label('<span foreground="' + color +'">' \
                + escape(str(string)) + '</span>')
        messageLabel.set_use_markup(True)
        messageLabel.set_justify(gtk.JUSTIFY_CENTER)
        messageLabel.set_ellipsize(pango.ELLIPSIZE_END)
        try:
            messageLabel.modify_font(pango.FontDescription(font))
        except e:
            print e

    
        if closePixmap == None:
            close = gtk.Label()
            #close.set_label("<span background=\"#cc0000\" foreground=" \
            close.set_label("<span background=\"#cc0000\" foreground=\"" \
                    + color + "\"> X </span>")
            close.set_use_markup(True)
        else:
            close = gtk.Image()
            close.set_from_pixbuf(closePixmap)

        closeEventBox = gtk.EventBox()
        closeEventBox.set_visible_window(False)
        closeEventBox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        closeEventBox.connect("button_press_event", self.close)        
        closeEventBox.add(close)

        hbox = gtk.HBox()
        vbox = gtk.VBox()
        lbox = gtk.HBox()
        title = gtk.Label("")
        title.set_use_markup(True)

        if userPixbuf != None:
            avatarImage = gtk.Image()
            userPixbuf = resizePixbuf(userPixbuf, 48, 48)
            avatarImage.set_from_pixbuf(userPixbuf)

        lboxEventBox = gtk.EventBox()
        lboxEventBox.set_visible_window(False)
        lboxEventBox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        lboxEventBox.connect("button_press_event", self.onClick, params)
        lboxEventBox.add(lbox)
        
        self.connect("button_press_event", self.onClick, params)

        hbox.pack_start(title, True, True)
        hbox.pack_end(closeEventBox, False, False)
        if userPixbuf != None: lbox.pack_start(avatarImage, False, False, 10)
        lbox.pack_start(messageLabel, True, True, 5)

        vbox.pack_start(hbox, False, False)
        vbox.pack_start(lboxEventBox, True, True)

        self.grow(offset, False)
        self.add(vbox)

        vbox.show_all()

    def onClick(self, widget, event, params):
        if event.button == 1 and self.callback != None:
            self.callback(params)
        self.close()

    def _resize(self):
        ''' change the size and position '''

        if self.offset == 0:
            sumx = taskbarOffsetx
            sumy = taskbarOffsety
        else:
            sumx = 0
            sumy = 0
        if self.scroll == 0:
            if self.corner == 0 or self.corner == 2:
                l = self.offset + sumx
            else:
                l = gtk.gdk.screen_width() - self.offset - self.width - sumx

            if self.corner == 0 or self.corner == 1:
                t = 0 + taskbarOffsety
            else:
                t = gtk.gdk.screen_height() - self.height - taskbarOffsety
        else:
            if self.corner == 0 or self.corner == 2:
                l = 0 + taskbarOffsetx
            else:
                l = gtk.gdk.screen_width() - self.width - taskbarOffsetx

            if self.corner == 0 or self.corner == 1:
                t = self.offset + sumy
            else:
                t = gtk.gdk.screen_height() - self.offset - self.height - sumy

        self.move(l, t)
        self.resize(self.width, self.height)

    def show(self):
        ''' show it '''
        self.show_all()

    def close(self , *args):
        ''' hide the Notification '''
        self.hide()
        self.destroy()

    def grow(self, offset, animate=True):
        ''' increase the size of the notification and position '''

        if animate and offset < self.offset:
            self.offset -= growFactor
            if offset < self.offset:
                self.offset = offset
        else:
            self.offset = offset

        if self.scroll == 0:
            if self.width < self.max:
                if self.width > self.max:
                    self.width = self.max
                else:
                    self.width += growFactor
        else:
            if self.height < self.max:
                if self.height + growFactor > self.max:
                    self.height = self.max
                else:
                    self.height += growFactor

        self._resize()

    def getOffset(self):
        ''' returns next notifications offset '''

        if self.scroll == 0: 
            if self.corner == 0 or self.corner == 2:
                return self.get_position()[0] + self.width
            else:
                return gtk.gdk.screen_width() - self.get_position()[0]
        else:
            if self.corner == 0 or self.corner == 1:
                return self.get_position()[1] + self.height
            else:
                return gtk.gdk.screen_height() - self.get_position()[1]

class MainClass:
    def __init__(self, Control):
        ''' Constructor '''
		# TODO: Agregar soporte de themes
        #self.theme = controller.theme
        self.Config = Control['Config']
        self.Config.user['notCanPyNotify'] = CAN_PYNOTIFY
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
        self.PyNotify = self.Config.user['notPyNotify']
        if self.PyNotify and CAN_PYNOTIFY:
            pynotify.init('okeykoclient')
        else:
            self.Noti = NotificationManager(128, 200)

    def pyNotification(self, string, title=None, callback=None, params=None, userPixbuf=None):
        if CAN_PYNOTIFY:
            userPixbuf = self.Config.avatarLoad(userPixbuf,
                         False)[1] if (userPixbuf) else "okeykoclient"
            title = 'Okeyko Client' if (not title) else title
            Noti = pynotify.Notification(title, string, userPixbuf)
            Noti.show()

    def newNotification(self,string,dura=7):   
        if self.Config.user['enableNot']:
            if self.PyNotify and CAN_PYNOTIFY:
                Noti = pynotify.Notification('Okeyko Client', string, 'okeykoclient')
                Noti.show()
            else:
                self.Noti.newNotification(string, self.corner, self.scroll, self.NotiPixmap, self.NotiClosePixmap, color=self.NotiCol, duration=dura)


    def mensajeNew(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowRecibido'] and self.Config.user['enableNot']:
            string = "Has recibido un mensaje de %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(text, string, callback, params, userPixbuf)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, 0)
    def pensamientoNew(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowPensamiento'] and self.Config.user['enableNot']:
            string = "Nuevo Pensamiento de %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(text, string, callback, params, userPixbuf)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, 7)
    def enviar(self, user=None, callback=None, params=None, userPixbuf=None, text=None):
        if self.Config.user['notshowEnviar'] and self.Config.user['enableNot']:
            string = "Mensaje enviado a %s" % user
            if self.PyNotify and CAN_PYNOTIFY:
                self.pyNotification(string, text, callback, params, userPixbuf)
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.avatarLoad(
                             userPixbuf, False)[1]) if (userPixbuf) else None
                self.Noti.newNotification(string, self.corner, self.scroll,\
                                    self.NotiPixmap, self.NotiClosePixmap,\
                                    callback, params, userPixbuf, self.font,\
                                    self.color, 7)

    def preview(self, pos, scroll, font, color, theme, pynot=False):
        if self.Config.user['enableNot']:
            string = "Ejemplo de Notificacion en Pantalla"
            if pynot and CAN_PYNOTIFY:
                pynotify.init('okeykoclient')
                self.pyNotification(string, title="Ejemplo")
            else:
                userPixbuf = gtk.gdk.pixbuf_new_from_file(self.Config.pathFile(
                             'theme-logo.png'))
                self.Noti = NotificationManager(128, 200)
                NotiPixmapF = self.Config.themePathFile(theme, 'guif.png')
                notipx, NotiPMask = gtk.gdk.pixbuf_new_from_file(NotiPixmapF).render_pixmap_and_mask()
                NotiPixmapCloseF = self.Config.themePathFile(theme, 'close.png')
                closepx = gtk.gdk.pixbuf_new_from_file(NotiPixmapCloseF)
                self.Noti.newNotification(string, pos, scroll,\
                                    notipx, closepx,\
                                    None, None, userPixbuf, font,\
                                    color, 7)
