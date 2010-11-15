import os
import imp
try:
     import cPickle as pickle
except ImportError:
     import pickle

import paths

class Main:
    ''' Manages everything related to configuration'''
    def __init__(self):
        self.CONFIG_DIR = None
        self.CONFIG_DIR_BOL = None
        self.CONFIG_DIR_GLOBAL = paths.CONFIG_DIR_GLOBAL
        self.USER = None
        self.USER_CONF_DIR = None
        self.THEMES_DIR = None
        self.THEME_PATH = None
        self.THEME_NAME = None
        self.THEME_PATH_EMOT = None
        self.THEME_NAME_EMOT = None
        self.THEME_PATH_SOUND = None
        self.THEME_NAME_SOUND = None
        self.THEME_PATH_NOT = None
        self.THEME_NAME_NOT = None

        self.EMOT = {} #User Emot Config
        self.SOUND = {} #User Sound Config
        self.NOT = {} #User Notification Config

        self.MainDict = {}
        self.EmotDict = {}
        self.SoundDict = {}
        self.NotDict = {}


        if os.path.isdir(paths.CONFIG_DIR):
            self.CONFIG_DIR = paths.CONFIG_DIR
            self.CONFIG_DIR_BOL = False    
        elif os.path.isdir(paths.CONFIG_DIR_GLOBAL):
            self.CONFIG_DIR = paths.CONFIG_DIR_GLOBAL
            self.CONFIG_DIR_BOL = True
        else:
            print "No existe directorio de configuracion... Cerrando"
            exit()

        if os.path.isdir(paths.THEME_HOME_PATH):
            self.THEMES_DIR = paths.THEME_HOME_PATH
        elif os.path.isdir(paths.THEME_SYSTEM_WIDE_PATH):
            self.THEMES_DIR = paths.THEME_SYSTEM_WIDE_PATH
        else:
            print "No existe directorio de themes... Cerrando"
            exit()

        if os.path.isdir(paths. DEFAULT_THEME_PATH_HOME):
            self.THEME_PATH = paths.DEFAULT_THEME_PATH_HOME
        elif os.path.isdir(paths.THEME_SYSTEM_WIDE_PATH):
            self.THEME_PATH = paths.DEFAULT_THEME_PATH
        else:
            print "No existe directorio de themes default... Cerrando"
            exit()
        self.THEME_PATH = self.THEME_PATH + "default"
        self.THEME_NAME = "default"
        self.THEME_PATH_EMOT = self.THEME_PATH + "default"
        self.THEME_NAME_EMOT = "default"
        self.THEME_PATH_SOUND = self.THEME_PATH + "default"
        self.THEME_NAME_SOUND = "default"
        self.THEME_PATH_NOT = self.THEME_PATH + "default"
        self.THEME_NAME_NOT = "default"
        self.loadConfig()

    def conectado(self, user):
        '''It has to be called after conecting
            Configures things acording to the user'''
        self.USER = user
        if not self.CONFIG_DIR_BOL:
            if not os.path.isdir(self.CONFIG_DIR + user):
                os.mkdir(self.CONFIG_DIR + user)
                self.USER_CONF_DIR = self.CONFIG_DIR + user
            else:
                self.USER_CONF_DIR = self.CONFIG_DIR + user
                self.loadConfig(user)            
        return

    def loadConfig(self, user=None):
        '''Loads the configuration '''
        confDir = self.USER_CONF_DIR if (user != None)\
                                        else self.CONFIG_DIR_GLOBAL
        configFile = file(confDir + "config.dat")
        config = pickle.load(configFile)
        configFile.close()
        if self.checkConfig(config):
            self.THEME_NAME = config[0]
            self.THEME_PATH = self.THEMES_DIR + self.THEME_NAME + paths.DIR_SEP
            self.THEME_PATH_EMOT = self.THEMES_DIR + self.THEME_NAME_EMOT + paths.DIR_SEP
            self.THEME_NAME_EMOT = config[1]
            self.THEME_PATH_SOUND = self.THEMES_DIR + self.THEME_NAME_SOUND + paths.DIR_SEP
            self.THEME_NAME_SOUND = config[2]
            self.THEME_PATH_NOT = self.THEMES_DIR + self.THEME_NAME_NOT + paths.DIR_SEP
            self.THEME_NAME_NOT = config[3]
            self.loadThemes()
            self.EMOT = config[4]
            self.SOUND = config[5]
            self.setThemeDict(self.SoundDict, self.SOUND)
            self.NOT = config[6]
            self.setThemeDict(self.NotDict, self.NOT)
        return

    def loadThemes(self):
        '''Loads Themes'''
        TMfile = open(self.THEME_PATH + "__init__.py", "r")
        ThemeMain = imp.load_source( self.THEME_NAME, self.THEME_PATH + "__init__.py", TMfile)
        TMfile.close()
        TSfile = open(self.THEME_PATH_SOUND + "__init__.py", "r")
        ThemeSound = imp.load_source( self.THEME_NAME_SOUND, self.THEME_PATH_SOUND + "__init__.py", TSfile)
        TSfile.close()
        TEfile = open(self.THEME_PATH_EMOT + "__init__.py", "r")
        ThemeEmot = imp.load_source( self.THEME_NAME_EMOT, self.THEME_PATH_EMOT + "__init__.py", TEfile)
        TEfile.close()
        TNfile = open(self.THEME_PATH_NOT + "__init__.py", "r")
        ThemeNot = imp.load_source( self.THEME_NAME_NOT, self.THEME_PATH_NOT + "__init__.py", TNfile)
        TNfile.close()

        #exec("import " + self.THEME_NAME + " as ThemeMain")
        self.setThemeDict(self.MainDict, ThemeMain.MainDict, self.THEME_PATH)
        #exec("import " + self.THEME_NAME_SOUND + " as ThemeSound")
        self.setThemeDict(self.SoundDict, ThemeSound.SoundDict, self.THEME_PATH_SOUND)
        #exec("import " + self.THEME_NAME_EMOT + " as ThemeEmot")
        self.setThemeDict(self.EmotDict, ThemeEmot.EmotDict, self.THEME_PATH_EMOT)
        #exec("import " + self.THEME_NAME_NOT + " as ThemeNot")
        self.setThemeDict(self.NotDict, ThemeNot.NotDict, self.THEME_PATH_NOT)

        del ThemeMain, ThemeSound, ThemeEmot, ThemeNot
        

    def setThemeDict(self, globalDict, themeDict, path=None):
        for name, value in themeDict.items():
            if path != None:
                try:
                    value = value.replace('[PATH]', path)
                except Exception as ins:
                    pass
            globalDict[name] = value
        return globalDict
        

    def checkConfig(self, config):
        '''Checks that the loaded configuration is valid '''
        return True

    def saveConfig(self):
        '''Saves configuration'''
        config = [ self.THEME_NAME,\
                    self.THEME_NAME_EMOT,\
                    self.THEME_NAME_SOUND,\
                    self.THEME_NAME_NOT,\
                    self.EMOT,\
                    self.SOUND,\
                    self.NOT ]
        if os.path.isdir(self.USER_CONF_DIR):
            configFile = file(self.USER_CONF_DIR + "config.dat", "w")
            pickle.dump(config, configFile)
            configFile.close()

    def set_theme(self, theme, tipo="all"):
        '''Sets the theme
            Tipo:
                 all - Sets all themes to the specified one
                 main - Only main theme
                 emot - Only emoticons
                 sound - Only sound
                 not - Only Notifications
        '''
        if os.path.isdir(paths.THEME_HOME_PATH + theme):
            path = paths.THEME_HOME_PATH + theme
        elif os.path.isdir(paths.THEME_SYSTEM_WIDE_PATH + theme):
            path = paths.THEME_SYSTEM_WIDE_PATH + theme
        else:
            return False
        if (tipo == "all") | (tipo == "main"):
            self.THEME_PATH = path
            self.THEME_NAME = theme
        if (tipo == "all") | (tipo == "emot"):
            self.THEME_PATH_EMOT = path
            self.THEME_NAME_EMOT = theme
        if (tipo == "all") | (tipo == "sound"):
            self.THEME_PATH_SOUND = path
            self.THEME_NAME_SOUND = theme
        if (tipo == "all") | (tipo == "not"):
            self.THEME_PATH_NOT = path
            self.THEME_NAME_NOT = theme
        return True

    def getNotConfig(self, arg):
        '''args:
         corner, scroll, offset, string, height = 128,
         width = 200, pixmap = None, closePixmap = None,
         userPixbuf = None, font = None, color = None'''
        try:
            return self.NotDict[arg]
        except:
            return False

def get_childs(path):
    '''Gets the childs of the specified path'''
    result = []
    for root, dirs, files in os.walk(path):
        if root == path:
            for dir in dirs:
                if not dir.startswith('.'):
                    result.append(dir)
    return result
