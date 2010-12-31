import gtk

NAME = 'Okeyko Client'
VERSION = 'beta 0'
COPYRIGHT = 'Nicolas Cisco'
COMMENTS = 'Un cliente para la red de Okeyko'
LICENSE = 'Esta por verse (?). Se cree que Gpl. Archivos sacados de emesene o de' \
          'otros lados tiene su licencia propia. Revisar cada archivo para saber'\
          'bajo que licencia se encuentran.'
WEBSITE = 'http://www.okeyko.com'
WEBSITE_LABEL = 'Pagina de Okeyko'
AUTHORS = ('Nicolas Cisco', 'Agradecimientos a Emesene community & developers y a la comunidad de PyAr')

class AboutOkeyko(gtk.AboutDialog):
    ''' About Dialog for Okeykoclient'''
    def __init__(self, Config):
        gtk.AboutDialog.__init__(self)
        logo = gtk.gdk.pixbuf_new_from_file(Config.pathFile('theme-logo.png'))
        self.set_logo(logo)
        self.set_version(VERSION)
        self.set_copyright(COPYRIGHT)
        self.set_comments(COMMENTS)
        self.set_license(LICENSE)
        self.set_website(WEBSITE)
        self.set_website_label(WEBSITE_LABEL)
        self.set_authors(AUTHORS)

