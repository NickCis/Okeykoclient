#   This file was inspired by emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

import os
import imp
import sys
import shutil
import base64
import shutil

import paths



THEME_SOUND_FILES = [ 'enviar.wav',
                      'pensamiento.wav',
                      'recibido.wav' ]

THEME_NOT_FILES = [ 'bor.png',
                    'guif.png',
                    'back.png' ]

THEME_THEME_FILES = [ 'ag.png',
                      'bor.png',
                      'fav.png',
                      'foky.png',
                      'leido_cel.png',
                      'leido_pc.png',
                      'loading.gif',
                      'logo.png',
                      'logo_chik.png',
                      'new.png',
                      'resp.png' ]

THEME_EMOT_FILES = [ 'emot-nerd.png',
                     'emot-angel.png',
                     'emot-banana.png',
                     'emot-burger.png',
                     'emot-callate.png',
                     'emot-colorado.png',
                     'emot-corazon.gif',
                     'emot-diablo.png',
                     'emot-enfadado.png',
                     'emot-enojado.png',
                     'emot-feliz.png',
                     'emot-jeje.png',
                     'emot-llora.png',
                     'emot-loco.png',
                     'emot-mmm.png',
                     'emot-ninja.png',
                     'emot-ok.png',
                     'emot-oo.png',
                     'emot-playa.png',
                     'emot-pomada.png',
                     'emot-puag.png',
                     'emot-torta.png',
                     'emot-triste.png' ]

DEFAULT_GLOBAL_CONFIG = {
    'mainWindowGeometry': '205x550+0+0',
    'theme': 'default',
    'rememberMe': True,
    'rememberMyPassword': False,
    'lastLoggedAccount': 'Nadie',
    'disableTrayIcon': False,
    'notCanPyNotify': False,
    'overrideDesktop': ''
}


DEFAULT_USER_CONFIG = {
    'menWindowGeometry': '205x150+0+0',
    'themeEmot': 'default',
    'themeSound': 'default',
    'soundsplayRecibido': True,
    'soundsplayPensamiento': False,
    'soundsplayEnviar': False,
    'soundsmuteSound': False,
    'enableSounds': True,
    'soundsbeep': False,
    'themeNot': 'default',
    'notshowRecibido': True,
    'notshowPensamiento': False,
    'notshowEnviar': True,
    'notColor': '#000000',
    'notCorner': '1',
    'notFont': 'sans',
    'notScroll': '1',
    'notOffset': '1',
    'notHeight': 128,
    'notWidth': 200,
    'notType': '0',
    'enableNot': True,
    'tabR': True,
    'tabE': True,
    'tabF': True,
    'tabP': True
}



class Main:
    ''' Manages everything related to configuration and themes'''
    def __init__(self):
        '''Constructor : this will create needed files for global configuration'''
        self.THEME_SOUND_FILES = THEME_SOUND_FILES
        self.THEME_NOT_FILES = THEME_NOT_FILES
        self.THEME_THEME_FILES = THEME_THEME_FILES
        self.THEME_EMOT_FILES = THEME_EMOT_FILES
        
        self.themePathFile = themePathFile
        
        self.currentUser = ''
        self.glob = {}
        self.user = {}
        self.userList = {}

        # This dict is a bit different from the two others
        # It's not a key : value dict but a plugin_name : [ key : value ] dict
        # Also it's a plain old dict, don't use it directly
        #self.pluginsConfigDict = {}

        if os.name != 'nt' or hasattr(sys, "frozen"):
            # home dirs don't work outside py2exe (!)
            _mkdir('', paths.HOME_DIR, '.config')
            _mkdir('Config dir', paths.CONFIG_DIR)
            _mkdir('Theme dir in config', paths.THEME_HOME_PATH)
            #_mkdir('Smilies dir in config', paths.SMILIES_HOME_PATH)
            #_mkdir('Convthemes dir in config', paths.CONVTHEMES_HOME_PATH)
            #_mkdir('Theme dir in config', paths.THEME_HOME_PATH)
            #_mkdir('Plugins dir in config', paths.PLUGIN_HOME_PATH)
            #open(os.path.join(paths.PLUGIN_HOME_PATH, '__init__.py'), 'w')\
            #    .write("__path__.append('%s')" % paths.PLUGIN_SYSTEM_WIDE_PATH)

        if _mkfile('Config file', paths.CONFIG_DIR, 'config'):
            self.glob = ConfigDict(self, self.writeGlobalConfig, \
                DEFAULT_GLOBAL_CONFIG)
            self.writeGlobalConfig()

        self.readGlobalConfig()

        if _mkfile('Users Save file', paths.CONFIG_DIR, 'users.dat'):
            self.userList = UserList(self, self.writeUserList)
            self.writeUserList()

        self.readUserList()

        self.__getAllThemes()

    def readGlobalConfig(self):
        '''read the config file and create a dictionarie with key and value
        of all the key=value\n in the config file'''

        globalConfigDict = DEFAULT_GLOBAL_CONFIG.copy()
        conf = None
        try:
            confPath = os.path.join(paths.CONFIG_DIR, 'config')
            conf = open(confPath, 'r')
            string = conf.read()

            for i in string.splitlines():
                if i != '':
                    try:
                        delim = i.find('=')
                        key = i[:delim]
                        value = i[delim+1:]
                        if key in DEFAULT_GLOBAL_CONFIG:
                            globalConfigDict[ key ] = value
                        else:
                            emesenelib.common.debug(key + ' is not a valid config key, ignored')
                    except Exception, e:
                        emesenelib.common.debug(key + ' config value is incorrect')

            conf.close()
        except:
            if conf:
                conf.close()

        self.glob = ConfigDict(self, self.writeGlobalConfig, DEFAULT_GLOBAL_CONFIG, globalConfigDict)
        
    def writeGlobalConfig(self):
        '''write the config to the file, overwrite current config file'''
        try:
            confPath = os.path.join(paths.CONFIG_DIR, 'config')
            conf = open(confPath, 'w')

            for k, v in self.glob:
                if type(v) == bool:
                    conf.write(k + '=' + str(int(v)) + '\n')
                else:
                    conf.write(k + '=' + str(v) + '\n')

            conf.close()
        except Exception, e:
            print "exception writing config:\n %s" % e
    # -- USER LIST -- #
    def writeUserList(self):
        '''write the UserList to the file, overwrite current config file'''
        try:
            confPath = os.path.join(paths.CONFIG_DIR, 'users.dat')
            conf = open(confPath, 'w')
            for k, v in self.userList:
                if type(v) == bool:
                    conf.write(k + ':' + '\n')
                else:
                    conf.write(k + ':' + base64.b64encode(str(v)) + '\n')

            conf.close()
        except Exception, e:
            print "exception writing userList:\n %s" % e
            
    def readUserList(self):
        '''read the user list file and create a dictionarie with key and value
        of all the nick=pass\n in the config file'''

        UserListDict = {}
        conf = None
        try:
            confPath = os.path.join(paths.CONFIG_DIR, 'users.dat')
            conf = open(confPath, 'r')
            string = conf.read()

            for i in string.splitlines():
                if i != '':
                    delim = i.find(':')
                    key = i[:delim]
                    value = base64.b64decode(i[delim+1:])
                    if str(value) != '0':
                        UserListDict[key] = value
                    else:
                        UserListDict[key] = False
            conf.close()
        except:
            if conf:
                conf.close()
                
        self.userList = UserList(self, self.writeUserList, UserListDict)

    # -- USER CONFIG -- #
    def setCurrentUser(self, user):
        ''' Create and/or read needed file for user config
        /!\ This function MUST be called before any set/getUserConfig'''

        #self.currentUser = email.replace('@', '_').replace('.', '_')
        self.currentUser = user.lower()
        self.glob['lastLoggedAccount'] = user


        if user != '':

            _mkdir('User config dir', paths.CONFIG_DIR, self.currentUser)

            if _mkfile('Config file created: ', paths.CONFIG_DIR, \
               self.currentUser, 'config'):
                self.user = ConfigDict(self, self.writeUserConfig, \
                    DEFAULT_USER_CONFIG)
                self.writeUserConfig()

            #_mkdir('', paths.CONFIG_DIR, self.currentUser, 'logs')
            #_mkdir('', paths.CONFIG_DIR, self.currentUser, 'cache')
            _mkdir('', paths.CONFIG_DIR, self.currentUser, 'avatars')
            #_mkdir('', paths.CONFIG_DIR, self.currentUser, 'custom_emoticons')
            self.readUserConfig()

        else:
            self.user = {}

    def getCurrentUser(self):
        return self.currentUser

    def readUserConfig(self):
        '''read the config file and create a dictionarie with key and value
        of all the key=value\n in the config file'''

        userConfigDict = DEFAULT_USER_CONFIG.copy()
        conf = None
        try:
            userConfigPath = os.path.join(paths.CONFIG_DIR, self.currentUser, 'config')
            conf = open(userConfigPath, 'r')
            string = conf.read()

            for i in string.splitlines():
                if i != '':
                    try:
                        delim = i.find('=')
                        key = i[:delim]
                        value = i[delim+1:]
                        if key in DEFAULT_USER_CONFIG:
                            userConfigDict[ key ] = value
                        else:
                            #emesenelib.common.debug(key + ' is not a valid config key, ignored')
                            print "%s is not a valid config key, ignored" % key
                    except Exception, e:
                        #emesenelib.common.debug(key + ' config value is incorrect')
                        print "%s config value is incorrect" % key

            conf.close()
        except:
            if conf:
                conf.close()

        self.user = ConfigDict(self, self.writeUserConfig, DEFAULT_USER_CONFIG, userConfigDict)

    def writeUserConfig(self):
        '''write the config to the file, overwrite current config file'''

        try:
            userConfigPath = os.path.join(paths.CONFIG_DIR, self.currentUser, 'config')
            conf = open(userConfigPath, 'w')

            for k, v in self.user:
                if type(v) == bool:
                    conf.write(k + '=' + str(int(v)) + '\n')
                else:
                    conf.write(k + '=' + str(v) + '\n')

            conf.close()
        except Exception, e:
            #emesenelib.common.debug('exception writing config:\n')
            #emesenelib.common.debug(e)
            print "exception writint config:"
            print e
    # -- Theme Listing --#
    def __getAllThemes(self):
        self.themesTheme = ['default']
        self.themesSound = ['default']
        self.themesNot = ['default']
        self.themesEmot = ['default']

        themesHome = {}
        for th in os.listdir(paths.THEME_HOME_PATH):
            themesHome.update({th: os.path.join(paths.THEME_HOME_PATH, th) })
        themesSystem = {}
        for th in os.listdir(paths.THEME_SYSTEM_WIDE_PATH):
            themesSystem.update({th: os.path.join(paths.THEME_SYSTEM_WIDE_PATH, th) })

        self.themes = themesSystem.copy()
        self.themes.update(themesHome)

        # Make list for loop
        looplist = [ (self.themesTheme, THEME_THEME_FILES),
                     (self.themesSound, THEME_SOUND_FILES),
                     (self.themesNot, THEME_NOT_FILES),
                     (self.themesEmot, THEME_EMOT_FILES) ]

        for th, thpath in self.themes.items():
            if th != 'default':
                for themeType, themeFiles in looplist:
                    if not th in themeType:
                        for f in themeFiles:
                            if not f in os.listdir(thpath):
                                break
                        else:
                            themeType.append(th)
                            #Try with SystemWide folder
                            if not th in themeType and thpath != themeSystem['th']:
                                for f in themeFiles:
                                    if not f in os.listdir(themeSystem['th']):
                                        break
                                else:
                                    themeType.append(th)
    # -- Theme Install --#
    def installTheme(self, themeName, filePath):
        themeName = themeName.lower()
        try:
            theme_path = os.path.join(THEME_SYSTEM_WIDE_PATH, themeName)
            shutil.copytree(filePath,theme_path)
        except:
            theme_path = os.path.join(THEME_HOME_PATH, themeName)
            shutil.copytree(filePath,theme_path)
        return themeName

    # -- Theme Return -- #
    def pathFile(self, arc):
        sep = arc.find("-")
        themeType = arc[:sep]
        archive = arc[sep + 1:]
        theme = self.glob[themeType] if (themeType=='theme') else \
            self.user['theme' + themeType]
        return themePathFile(theme, archive)

    def profileAvatarLoad(self, user=None, op=True):
        if user == None:
            avatarPath = self.pathFile('theme-logo.png')
            userE = False
        else:
            user = user.lower()
            Path = os.path.join(paths.CONFIG_DIR, user)
            if os.path.isdir(Path):
                for arch in os.listdir(Path):
                    lastdot = arch.rfind('.') if (arch.rfind('.') != -1) else len(arch)
                    ext = arch[lastdot:]
                    name = arch[:lastdot]
                    if str(name) == str('avatar'):
                        avatarPath = os.path.join(Path, arch)
                        userE = True
                        break
                else:
                    avatarPath = self.pathFile('theme-logo.png')
                    userE = False
            else:
                avatarPath = self.pathFile('theme-logo.png')
                userE = False
        if op:
            avatarFile = open(avatarPath, 'r')
            avatarImg = avatarFile.read()
            avatarFile.close()
        else:
            avatarImg = avatarPath            
        return userE, avatarImg
    
    def profileAvatarSave(self, avatar, avatarimg):
        print "Saving profile avatar"
        lastdot = avatar.rfind('.') if (avatar.rfind('.') != -1) else len(arch)
        avatarfileName = 'avatar%s' % (avatar[lastdot:])        
        avatarPath = os.path.join(paths.CONFIG_DIR, self.currentUser, avatarfileName)
        try:
            avatarFile = open(avatarPath, 'wb')
            avatarFile.write(avatarimg)
            avatarFile.close()
            return True, avatarPath
        except:
            return False, None

    def avatarLoad(self, avatar, op=True):
        avatarPath = os.path.join(paths.CONFIG_DIR, self.currentUser, 'avatars', avatar)
        if os.path.isfile(avatarPath):
            if op:
                avatarFile = open(avatarPath, 'r')
                avatarImg = avatarFile.read()
                avatarFile.close()
            else:
                avatarImg = avatarPath            
            return True, avatarImg
        else:
            return False, avatarPath
    
    def avatarSave(self, avatar, avatarimg):
        print "Saving avatar"
        avatarPath = os.path.join(paths.CONFIG_DIR, self.currentUser, 'avatars', avatar)
        try:
            avatarFile = open(avatarPath, 'wb')
            avatarFile.write(avatarimg)
            avatarFile.close()
            return True, avatarPath
        except:
            return False, None

class ConfigDict(dict):
    '''A dictionary that handles type conversion, fallbacks to default, config
    file writing, etc'''

    def __init__(self, config, writeFunc, defaults, store=None):
        self.config = config
        self.writeFunc = writeFunc
        self.defaults = defaults

        if store == None:
            store = defaults.copy()

        self.store = {}
        for key, value in store.iteritems():
            if type(value) == bool:
                self.store[key] = str(int(value))
            else:
                self.store[key] = str(value)

    def __repr__(self):
        #return '<ConfigDict based on ' + repr(store) + '>'
        return '<ConfigDict based on ' + repr(self.store) + '>'

    def getDefault(self, name):
        if name in self.defaults:
            return self.defaults[name]
        else:
            return ''

    def __getitem__(self, name):
        '''returns a item from self.store. if it is not available, return that
        item from defaults
        also does some type conversion and bool checks'''

        if name in self.store:
            newType = type(self.getDefault(name))
            if newType == bool:
                if str(self.store[name]).lower() in ('true', 'false'):
                    # workaround for some buggy configs..
                    boolValue = (str(self.store[name]).lower() == 'true')
                    self.store[name] = str(int(boolValue))
                    return boolValue
                else:
                    try:
                        # >>> int('0') == True
                        return bool(int(self.store[name]))
                    except ValueError:
                        return self.getDefault(name)
            else:
                try:
                    return newType(self.store[name])
                except ValueError:
                    return self.getDefault(name)
        else:
            #emesenelib.common.debug('Config value was not found: ' + str(name))
            print 'Config value was not found: %s' % str(name)
            return self.getDefault(name)

    def __setitem__(self, name, value):
        '''sets a config key "name" to the string "value", emits
        callbacks and writes config'''

        if type(value) == bool:
            value = str(int(value))
        else:
            value = str(value)

        oldValue = None
        if name in self.store:
            oldValue = self.store[name]

        self.store[name] = value

        #self.config.emit('change::' + name, value, oldValue)
        self.writeFunc() # TODO: config transactions?

    def __iter__(self):
        '''for key, value in configDict'''
        return self.store.iteritems()

class UserList(dict):
    '''A list that handles saves users and passwords'''

    def __init__(self, config, writeFunc, store=None):
        self.config = config
        self.writeFunc = writeFunc

        if store == None:
            store = {}

        self.store = {}
        for key, value in store.iteritems():
            if type(value) == bool:
                self.store[key] = str(int(value))
            else:
                self.store[key] = str(value)

    def __repr__(self):
        #return '<UserList based on ' + repr(store) + '>'
        return '<UserList for Okeykoclient Users/Pass>'

    #def getDefault(self, name):
    #    if name in self.defaults:
    #        return self.defaults[name]
    #    else:
    #        return ''

    def __getitem__(self, name):
    #    '''if nick is given returns password or false
    #       if number is given returns nick'''

        if name in self.store:
            return self.store[name]
    #        newType = type(self.getDefault(name))
    #        if newType == bool:
    #            if str(self.store[name]).lower() in ('true', 'false'):
    #                # workaround for some buggy configs..
    #                boolValue = (str(self.store[name]).lower() == 'true')
    #                self.store[name] = str(int(boolValue))
    #                return boolValue
    #            else:
    #                try:
    #                    # >>> int('0') == True
    #                    return bool(int(self.store[name]))
    #                except ValueError:
    #                    return self.getDefault(name)
    #        else:
    #            try:
    #                return newType(self.store[name])
    #            except ValueError:
    #                return self.getDefault(name)
    #    else:
    #        #emesenelib.common.debug('Config value was not found: ' + str(name))
    #        print 'Config value was not found: %s' % str(name)
    #        return self.getDefault(name)

    def __setitem__(self, name, value):
        '''sets a config key "name" to the string "value", emits
        callbacks and writes config'''

        if type(value) == bool:
            value = str(int(value))
        else:
            value = str(value)

        oldValue = None
        if name in self.store:
            oldValue = self.store[name]

        self.store[name] = value

        #self.config.emit('change::' + name, value, oldValue)
        self.writeFunc() # TODO: config transactions?

    def __contains__(self, name):
        if name in self.store:
            return True
        else:
            return False   

    def __iter__(self):
        '''for key, value in configDict'''
        return self.store.iteritems()





def themePathFile(theme, arc):
    arcPathH = os.path.join(paths.THEME_HOME_PATH, theme ,arc)
    arcPathS = os.path.join(paths.THEME_SYSTEM_WIDE_PATH, theme, arc)
    arcPathD = os.path.join(paths.DEFAULT_THEME_PATH, arc)
    if os.path.isfile(arcPathH):
        arcPath = arcPathH
    elif os.path.isfile(arcPathS):
        arcPath = arcPathS
    elif os.path.isfile(arcPathD):
        arcPath = arcPathD
    else:
        arcPath = False
        print "Error in themePathFile: %s %s" % (theme, arc)
    return arcPath

def get_childs(path):
    '''Gets the childs of the specified path'''
    result = []
    for root, dirs, files in os.walk(path):
        if root == path:
            for dir in dirs:
                if not dir.startswith('.'):
                    result.append(dir)
    return result

def _mkbase(check, make, message, *components):
    '''base function for _mkdir and _mkfile'''
    path = os.path.join(*components)
    if not check(path):
        make(path)
        if message:
        #    emesenelib.common.debug(message + ' created: ' + path)
            print "%s created: %s" % (message, path)
        return True
    return False

def _mkdir(message, *components):
    '''makes a directory and prints a message'''
    return _mkbase(os.path.isdir, os.mkdir, message, *components)

def _mkfile(message, *components):
    '''checks if the file exists and prints a message'''
    return _mkbase(os.path.isfile, lambda x: None, message, *components)
