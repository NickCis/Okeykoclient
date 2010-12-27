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

import paths


DEFAULT_GLOBAL_CONFIG = {
    'mainWindowGeometry': '205x550+0+0',
    'theme': 'default',
    'rememberMe': True,
    'rememberMyPassword': False,
    'lastLoggedAccount': 'Nadie'
}


DEFAULT_USER_CONFIG = {
    'menWindowGeometry': '205x150+0+0',
    'themeEmot': 'default',
    'themeSound': 'default',
    'themeNot': 'default',
    'notColor': '#000000',
    'notCorner': '1',
    'notFont': 'sans',
    'notScroll': '1',
    'notOffset': '1',
    'notHeight': 128,
    'notWidth': 200
}



class Main:
    ''' Manages everything related to configuration and themes'''
    def __init__(self):
        '''Constructor : this will create needed files for global configuration'''
        
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

    def readGlobalConfig(self):
        '''read the config file and create a dictionarie with key and value
        of all the key=value\n in the config file'''

        globalConfigDict = DEFAULT_GLOBAL_CONFIG.copy()
        conf = None
        try:
            conf = open(paths.CONFIG_DIR + '/config', 'r')
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
            conf = open(paths.CONFIG_DIR + '/config', 'w')

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
            conf = open(paths.CONFIG_DIR + '/users.dat', 'w')
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
            conf = open(paths.CONFIG_DIR + '/users.dat', 'r')
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
    # -- USER LIST -- #
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
            conf = open(paths.CONFIG_DIR + '/' + self.currentUser + '/config', 'r')
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
            conf = open(paths.CONFIG_DIR + '/' + self.currentUser + '/config', 'w')

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
            
    # -- Theme Return -- #
    def pathFile(self, arc):
        sep = arc.find("-")
        themeType = arc[:sep]
        archive = arc[sep + 1:]
        theme = self.glob[themeType] if (themeType=='theme') else \
            self.user['theme' + themeType]
        return themePathFile(theme, archive)

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
        return '<ConfigDict based on ' + repr(store) + '>'

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
        arcPath = archPathD
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
