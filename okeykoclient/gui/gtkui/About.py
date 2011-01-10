import gtk

NAME = 'Okeyko Client'
VERSION = 'beta 0'
COPYRIGHT = 'Nicolas Cisco'
COMMENTS = 'Un cliente para la red de Okeyko'
LICENSE = 'Esta por verse (?). Se cree que Gpl. Archivos sacados de emesene o de' \
          'otros lados tiene su licencia propia. Revisar cada archivo para saber'\
          'bajo que licencia se encuentran.'
WEBSITE = 'http://okeykoclient.sourceforge.net'
WEBSITE_LABEL = 'Pagina de Okeyko'
AUTHORS = ('Nicolas Cisco', 'Agradecimientos a Emesene community & developers y a la comunidad de PyAr')
TRANSLATORS = ""

def Link(*args):
    print args

class AboutOkeyko(gtk.AboutDialog):
    ''' About Dialog for Okeykoclient'''
    def __init__(self, Config):
        gtk.AboutDialog.__init__(self)
        gtk.about_dialog_set_url_hook(Link)
        self.set_name(NAME)
        logo = gtk.gdk.pixbuf_new_from_file(Config.pathFile('theme-logo.png'))
        self.set_logo(logo)
        self.set_icon(logo)
        self.set_version(VERSION)
        self.set_copyright(COPYRIGHT)
        self.set_comments(COMMENTS)
        self.set_license(LICENSE)
        self.set_website(WEBSITE)
        #self.set_website_label(WEBSITE_LABEL)
        self.set_authors(AUTHORS)
        
        self.connect('response', lambda *x: self.destroy() if (x[1] == -6) else x)
        
        #self.set_translator_credits(TRANSLATORS)
