# -*- coding: utf-8 -*-

#   This file was taken from emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

import os
# import TrayIcon
import gtk
import subprocess #Para reemplazar os.popen4

if os.name == 'nt':
    import winsound

# Sacamos el import paths de emesene y añadimos las variables a mano
import paths
# SOUNDS_PATH = APP_PATH + DIR_SEP + 'sound_themes'
#paths_SOUNDS_PATH = os.path.abspath('') + os.sep

try: 
    import gst
    GSTREAMER = True
except:
    GSTREAMER = False

try:
    from AppKit import NSSound
    MAC = True
except:
    MAC = False

class Sound:
    '''A plugin to play sounds using the available modules on the system'''

    def __init__(self, config):
        '''class constructor'''
    
        self.config = config
        self.beep = False
        self.command = ''
        self.canPlay = False
        self.canGstreamer = False
        self.isMac = False
        
        if os.name == "posix":
            self.checkAvailability()
            if self.canGstreamer:
                self.player = gst.element_factory_make("playbin", "player")
                bus = self.player.get_bus()
                bus.enable_sync_message_emission()
                bus.add_signal_watch()
                bus.connect('message', self.gst_on_message)
        else:
            self.canPlay = True

    def gst_on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)

    def checkAvailability(self):
        if self.beep:
            self.canPlay = True
        elif GSTREAMER:
            self.canPlay = True
            self.canGstreamer = True
        elif MAC:
            self.canPlay = True
            self.isMac = True
        elif self.is_on_path('aplay'):
            self.canPlay = True
            self.command = 'aplay'
        elif self.is_on_path('play'):
            self.canPlay = True
            self.command = 'play'
        
    def play(self, sound):
        if self.beep and not self.isMac:
            gtk.gdk.beep()
            return
        
        #for theme in (sound_theme, 'default'):
        #    soundPath = os.path.join(paths.SOUNDS_PATH, sound_theme,
        #        sound + ".wav")
        #    if os.path.exists(soundPath):
        #        break
        #    else:
        #        soundPath = ''
        soundPath = self.config.pathFile(sound)
        if not soundPath:
            return

        self.play_path(soundPath)

    def play_theme(self, soundTheme, soundFile):
        if self.beep and not self.isMac:
            gtk.gdk.beep()
            return
        soundPath = self.config.themePathFile(soundTheme, soundFile)
        if soundPath != False:
            self.play_path(soundPath)

    def play_path(self, soundPath):
        if os.name == "nt":
            winsound.PlaySound(soundPath, 
                winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif os.name == "posix":
            if self.canGstreamer:
                loc = "file://" + soundPath
                self.player.set_property('uri', loc)
                self.player.set_state(gst.STATE_PLAYING)
            elif self.isMac:
                macsound = NSSound.alloc()
                macsound.initWithContentsOfFile_byReference_( \
                    soundPath, True)
                macsound.play()
                while macsound.isPlaying():
                    pass
            else:
                # os.popen4(self.command + " " + soundPath)
                subprocess.Popen([self.command, soundPath])
            
    def getCommand(self):
        return self.command
        
    def setCommand(self, string):
        self.command = string
        
    def is_on_path(self, fname):
        for p in os.environ['PATH'].split(os.pathsep):
            if os.path.isfile(os.path.join(p, fname)):
                return True

class SoundHandler:
    def __init__(self, config, action=None):
        '''Contructor'''
        self.config = config
        self.sound = Sound(self.config)
        self.check()
        self.clearUpdate()

    def clearUpdate(self):
        self.playRecibido = False
        self.playPensamiento = False
        self.playEnviar = False
        self.muteSound = False
        self.sound.beep = False

    def update(self):
        self.playRecibido = self.config.user['soundsplayRecibido']
        self.playPensamiento = self.config.user['soundsplayPensamiento']
        self.playEnviar = self.config.user['soundsplayEnviar']
        self.muteSound = self.config.user['soundsmuteSound']
        #self.playOnline = self.config.user['soundsplayOnline']
        #self.playOffline = self.config.user['soundsplayOffline']
        #self.muteSound = self.config.user['soundsmuteSound']
        #self.checkBox.set_active(self.muteSound)
        #self.playMessage = self.config.user['soundsplayMessage']
        #self.playNudge = self.config.user['soundsplayNudge']
        #self.playTransfer = self.config.user['soundsplayTransfer']
        #self.playInactive = self.config.user['soundsplayInactive']
        #self.playSend = self.config.user['soundsplaySend']
        #self.playError = self.config.user['soundsplayError']
        #self.disableBusy = self.config.user['soundsdisableBusy']

        self.sound.beep = self.config.user['soundsbeep']
        
    def on_muteSounds_activate(self, truefalse):
        self.muteSound = truefalse
        if type(self.muteSound) == bool:
            self.config.user['soundsmuteSound'] = (self.muteSound)
    
    def check(self):
        if not self.sound.canPlay:
            return (False, _('gstreamer, NSSound, play and aplay not found.'))
        return (True, 'Ok')

    def recibido(self):
        if self.playRecibido and self.soundsEnabled():
            self.sound.play('Sound-recibido.wav')

    def pensamiento(self):
        if self.playPensamiento and self.soundsEnabled():
            self.sound.play('Sound-pensamiento.wav')

    def enviar(self):
        if self.playEnviar and self.soundsEnabled():
            self.sound.play('Sound-enviar.wav')
            
    def soundsEnabled(self):
        if self.muteSound or not self.config.user['enableSounds']:
            return False
        else:
            return True
    
    def updateTrayIconMenuList(self):
         if not (TrayIcon.disabled):
             #Generates the Systray list with the new feature
             #when the TrayIcon is enabled
            self.controller.trayIcon.menu.prepend(self.checkBox)
            self.controller.trayIcon.menu.show_all()
            self.controller.trayIcon.update(self.controller.msn.status)
