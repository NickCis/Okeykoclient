import re
import urllib2
import cookielib
import htmlentitydefs
import MultipartPostHandler
from urllib import urlencode
from pyquery import PyQuery as pq

class urldownload:
    def __init__(self, cookies=None):
        self.cookies = cookielib.CookieJar()
        if cookies != None and type(cookies) == type(self.cookies):
            self.cookies = cookies        
        self.proxy = None
        self.auth = None
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies),
                                           MultipartPostHandler.MultipartPostHandler)
    def open(self, url, post=None, get=None ):
        if get:            
            url = "url?%s" % urlencode(get)
        return self.opener.open(url, post, 30)

    def setProxy(self, proxy, auth=None):
        '''proxy, auth
           ip:port, (user,pass)
           xxx.xxx.xxx.xxx:xx'''
        print proxy, auth        
        if proxy == "%s:%s" % (None, None):
            self = urldownload(self.cookies)
            return
        self.proxy = proxy
        self.opener.add_handler(urllib2.ProxyHandler({'http': proxy}))
        if auth:
            self.auth = auth
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
            proxy_auth_handler.add_password(None, proxy, auth[0], auth[1])
            self.opener.add_handler(proxy_auth_handler)

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
   @param text The HTML (or XML) source text.
   @return The plain text, as a Unicode string, if necessary.
   from Fredrik Lundh
   2008-01-03: input only unicode characters string.
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print "Value Error"
            pass
      else:
         # named entity
         # reescape the reserved characters.
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               #print text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
         except KeyError:
            print "keyerror"
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)

def removeListInList(lsts, x):
    for lst in lsts:
        try:
            lst.index(x)
            lsts.remove(lst)
        except:
            pass


class okeyko:
    def __init__(self):
        self.__download = urldownload()
        self.__conectado = False
        self.__usuario = None
        self.__contra = None
        self.__agenda_lista = None
        self.__inbox = False
        self.__outbox = False
        self.__outboxPag = False
        self.__outboxBor = False
        self.__favbox = False
        self.__favPag = False
        self.__favBor = False
        self.__avatar = False
        self.__avatarLink = None
        self.__estado = False
        self.__captcha = None
        self.__envio = False
        self.__pensamientos = None
        self.__conectado_result = None
        

    def login(self, usuario, contra):
        self.__usuario = usuario if (usuario[:1] != "@") else usuario[1:]
        self.__contra = contra
        self.connect()
        if self.__conectado:
           self.get_all()
        return

    def connect(self):
        if (self.__usuario == None) | (self.__contra == None): 
            self.__conectado = False
            self.__conectado_result = "Usuario o Pass no seteadas"
            return
        url = "http://www.okeyko.com/v2/validar_usuario.php"
        params =  {'usuario': self.__usuario, 'clave': self.__contra}
        pag = self.pagina(url, post=params)
        if pag.find("Password o Usuario incorrecto") != -1: #Ok2.0
            self.__conectado = False
            self.__conectado_result = pq(pag).text() #Ok2.0
            return
        self.__conectado = True if (pag.find("exitosamente")) else False #Ok2.0
        self.__conectado_result = pq(pag).text() #Ok2.0
        print self.__conectado_result
        return

    def conectado(self, down=True):
        if down:
            if self.pagina("http://www.okeyko.com/v2/index.php").find(
                                "|| Hola") == -1:
                self.__conectado = False
                self.connect()
        return self.__conectado, self.__conectado_result
        
    def get_all(self):
        ''' Obtiene: inbox, outbox, avatar, estado'''
        if self.__conectado != True: return
        url = "http://www.okeyko.com/v2/boceto.php"
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        avt = pag("img[title='Usuario']").attr('src')
        self.__avatarLink = avt[avt.rfind('/')+1:]
        self.__avatar = self.avatar(self.__avatarLink,'g')
        try:
            self.__estado = pag("b[style='color:#FFF;']").text()
            self.__estado = self.__estado.encode('iso-8859-1')
        except:
            self.__estado = ""
        self.__inbox = self.__getInbox(pag)
        self.__outboxPag = 1
        self.__outbox = self.__getOutbox(pag)
        self.__favPag = 1
        self.__favbox = self.__getFavs(pag)
        self.__pensamientos = self.__getPensamientos(pag)
        self.getCaptcha()
        self.agenda_lista()

    def getCaptcha(self):
        url = 'http://www.okeyko.com/v2/CaptchaSecurityImages.php?width=100&height=40&characters=5'
        self.__captcha = self.pagina(url)

    def captcha(self):
        return self.__captcha

    def getMoreInbox(self):
        lastOId = self.__inbox[len(self.__inbox) - 1][3]
        params = {'lastmsg': str(lastOId)}
        url = "http://www.okeyko.com/v2/0ajax_more.php"
        #pag = BS(unescape(unicode(self.pagina(url,params), 'latin-1')))
        #pag = BS(unicode(self.pagina(url, post=params), 'latin-1'))
        pag = pq(unicode(self.pagina(url, post=params), 'latin-1'))
        Ins = self.__getInbox(pag)
        for i in Ins:
            self.__inbox.append(i)
        return Ins

    def getMoreOutbox(self):
        if self.__conectado != True: return
        if self.__outboxBor == False:
            self.__outboxPag = self.__outboxPag + 1
        else:
            self.__outboxBor = False
        url = "http://www.okeyko.com/v2/boceto.php?paginae=%s" % self.__outboxPag
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        #pag = BS(unicode(self.pagina(url), 'latin-1'))
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        Outs = self.__getOutbox(pag)
        lastOutId = int(self.__outbox[-1][3])
        ret = []
        for o in Outs:
            if lastOutId > int(o[3]):
                self.__outbox.append(o)
                ret.append(o)
        if len(ret) == 0:
            ret = self.getMoreOutbox()
        elif len(ret) < 5:
            lastRetId = ret[-1][3]
            for o in self.getMoreOutbox():
                if lastRetId > int(o[3]):
                    ret.append(o)
        return ret

    def getMoreFavs(self):
        if self.__conectado != True: return
        if self.__favBor == False:
            self.__favPag = self.__favPag + 1
        else:
            self.__favBor = False
        url = "http://www.okeyko.com/v2/boceto.php?pagina=%s" % self.__favPag
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        #pag = BS(unicode(self.pagina(url), 'latin-1'))
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        Favs = self.__getFavs(pag)
        lastFavId = int(self.__favbox[-1][3])
        ret = []
        for f in Favs:
            if lastFavId > int(f[3]):
                self.__favbox.append(f)
                ret.append(f)
        if len(ret) == 0:
            ret = self.getMoreFavs()
        elif len(ret) < 5:
            lastRetId = ret[-1][3]
            for f in self.getMoreFavs():
                if lastRetId > int(f[3]):
                    ret.append(f)
        return ret
            
    def __getInbox(self, pqHtml):
        menInbox = []
        li = pqHtml("li:eq(4)")

        while str(li) != '':
            de = li('a:eq(1)').text()
            hora = li("td[align='right']:first").text()
            mensaje = li.text()
            mensaje = mensaje[mensaje.find('</h2>')+5:mensaje.find('Leido desde')].strip()
            if mensaje.find('Agregar a Chat (IMok) -->') != -1:
                mensaje = mensaje[mensaje.find('Agregar a Chat (IMok) -->')+26:]
            Oik = li('label').attr('for')
            avatar = li('img:first').attr('src')
            avatar = avatar[avatar.rfind('/')+1:]
            leido = li("div[style=' font-size:11px; color:#666;']").text()
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            favHref = li("img[src='images/iconos_mensajes/favoritos2.png']").parent().attr('href')
            fav = favHref[favHref.rfind('&')+1:]
            menInbox.append([de, hora, mensaje, Oik, avatar, leido, fav])
            li = li.next()
        return menInbox

    def __getOutbox(self, pqHtml):
        menOutbox = []
        outs = pqHtml("#tab2 div.conten_mensaje")
        osum = 0
        out = outs.eq(osum)
        while str(out) != '':
            mensaje = out("div#cuerpo_mensaje").text()
            ph = out("div#mensaje_head").text()
            para = ph[ph.rfind('@'):ph.find('|')-1]
            hora = ph[ph.find('|')+1:ph.rfind('|')]
            Oid = out("div#herramientas input").attr('value')
            avatar = self.__avatarLink #TODO: Get avatar
            leido = out("div#herramientas").text()
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            menOutbox.append([para, hora, mensaje, Oid, avatar, leido]) 
            osum += 1
            out = outs.eq(osum)
        return menOutbox   

    def __getFavs(self, pqHtml):
        menFav = []
        favsTab = pqHtml('div#tab3')
        if favsTab.text().find('No tiene mensajes') != -1:
            return False
        favDs = favsTab("div.conten_mensaje")
        favsum = 0
        favD = favDs.eq(favsum)
        while str(favD) != '':
            mensaje = favD("div#cuerpo_mensaje").text()
            ph = favD("div#mensaje_head").text()
            para = ph[ph.find('">')+2:ph.find('|')]
            hora = ph[ph.find('|')+1:ph.rfind('|')]
            Oid = favD("div#herramientas input").attr('value')
            avatarSrc = favD('img:first').attr('src')
            avatar = avatarSrc[avatarSrc.rfind('/')+1:]
            leido = favD("div#herramientas").text()
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            favHref = favD("img[src='images/iconos_mensajes/favoritos2.png']").parent().attr('href')
            fav = favHref[favHref.rfind('&')+1:]
            menFav.append([para, hora, mensaje, Oid, avatar, leido, fav])
            favsum += 1
            favD = favDs.eq(favsum)
        return menFav

    def __getPensamientos(self, pqHtml):
        pensamientos = []
        pens = pqHtml("div#tab4 table")
        pen = pens.eq(0)
        penSum = 0        
        while str(pen) != '':
            trs = pen('tr td')        
            de = trs.eq(1).text()[4:]
            mensaje = trs.eq(2).text()
            try: # Corregir Codificacion
                mensaje = mensaje.encode('iso-8859-1')
            except:
                print "Exception in __getPensamientos while codification correction"
            hora = trs.eq(3).text()
            Oid = 'a'
            avatar = pen('img:first').attr('src')
            avatar = avatar[avatar.rfind('/')+1:]
            pensamientos.append([de, hora, mensaje, Oid, avatar])
            penSum += 1
            pen = pens.eq(penSum)
        return pensamientos

    def userinfo(self):
        if self.__conectado != True: return
        return self.__usuario, self.__avatar, self.__estado

    def avatarinfo(self):
        if self.__conectado != True: return
        return self.__avatarLink, self.__avatar

    def getUser(self):
        if self.__conectado != True: return
        return self.__usuario

    def inbox(self):
        ''' Devuelve los mensajes de inbox en una lista
        Formato: [de, hora, mensaje, Oik, avatar, leido, fav]'''
        if self.__conectado != True: return
        if self.__inbox == False: return
        return [list(a) for a in self.__inbox]
        
    def inboxNew(self, minId=0):
        inboxNew = []
        url = "http://www.okeyko.com/v2/nuevos.php"
        pag = self.pagina(url).strip()
        if pag == "</form >":
            return False
        #pag = BS(unicode(pag, 'latin-1'))
        pag = pq(unicode(pag, 'latin-1'))
        tables = pag('table')
        tablesN = len(tables) / 3

        for i in range(0, tablesN):
            table = tables.eq(i * 3)
            de = table('a:eq(1)').text()
            de = de[de.find(">")+1:]
            hora = table("td[align='right']:first").text()
            Oik = table.find("div[style='display:none; padding:5px; "
                + "margin-left:30px;margin-right:30px;background-color:"
                + "#F2F2F2']").attr('id').replace('_','')
            avatar = table('img:first').attr('src')
            avatar = avatar[avatar.rfind('/')+1:]
            leido = table("div[style=' font-size:11px; color:#666;']").text()
            leido = 0 #TODO: Arreglar leido
            fav = 0 #TODO: Get Favorito
            #Se borra todo y se deja solo el texto del mensaje
            while table.children().eq(0).children().eq(2).children().children().eq(0).remove():
                pass
            mensaje = table.children().eq(0).children().eq(2).children().text()
            if int(Oik) <= int(minId): #TODO: arreglar esto. Es feo.
                break
            else:
                inboxNew.append([de, hora, mensaje, Oik, avatar, leido, fav])
        if len(inboxNew) < 1:
            return False
        elif len(inboxNew[0]) > 4:
            if int(inboxNew[0][3]) <= int(minId):
                return False
        return inboxNew

    def outbox(self):
        ''' Devuelve los mensajes de outbox en una lista
        Formato: [para, hora, mensaje, Oid, leido]'''
        if self.__conectado != True: return
        if self.__outbox == False: return
        return [list(a) for a in self.__outbox]

    def outboxNew(self, pag=None):
        '''Devuelve si hay, mensajes enviados nuevos'''
        if self.__conectado != True: return
        if self.__envio == False:
            return False
        else:
            self.__envio = False
        if pag == None:
            url = "http://www.okeyko.com/v2/boceto.php"
            #pag = BS(unicode(self.pagina(url), 'latin-1'))
            pag = pq(unicode(self.pagina(url), 'latin-1'))
        Outs = self.__getOutbox(pag)
        firstOutId = int(self.__outbox[0][3])
        ret = []
        for o in Outs:
            if firstOutId < int(o[3]):
                ret.append(o)
        if len(ret) != 0:
            ret.reverse()
            for r in ret:
                self.__outbox.insert(0, r)
            ret.reverse()
            return ret
        else:
            return False        

    def favbox(self):
        ''' Devuelve los mensajes de favoritos en una lista
        Formato: [de, hora, mensaje, Oik, avatar, leido, fav] devuelve false si no hay ninguno'''
        if self.__conectado != True: return
        if self.__favbox == False: return
        return [list(a) for a in self.__favbox]

    def getReFavs(self):
        ''' Vuelve a descargar favs y devuelve los mensajes de favoritos en una lista
        Formato: [de, hora, mensaje, Oik, avatar, leido, fav] devuelve false si no hay ninguno'''
        if self.__conectado != True: return
        url = "http://www.okeyko.com/v2/boceto.php"
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        #pag = BS(unicode(self.pagina(url), 'latin-1'))
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        self.__favPag = 1
        self.__favbox = self.__getFavs(pag)
        return self.favbox()
    
    def pensamientos(self):
        ''' Devuelve los pensamientos en una lista
        Formato: [de, hora, mensaje, Oid?, avatar]'''
        if self.__conectado != True: return
        if self.__pensamientos == False: return
        return [list(a) for a in self.__pensamientos]

    def getRePen(self):
        ''' Vuelve a descargar pensamientos y devuelve los mensajes de favoritos en una lista
        Formato: [de, hora, mensaje, Oik, avatar] devuelve false si no hay ninguno'''
        if self.__conectado != True: return
        url = "http://www.okeyko.com/v2/boceto.php"
        #pag = BS(unicode(self.pagina(url), 'latin-1'))
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        self.__pensamientos = self.__getPensamientos(pag)
        return self.pensamientos()

    def pensamientosNew(self, pag=None):
        '''Devuelve si hay, pensamientos nuevos'''
        if self.__conectado != True: return
        if pag == None:
            url = "http://www.okeyko.com/v2/boceto.php"
            #pag = BS(unicode(self.pagina(url), 'latin-1'))
            pag = pq(unicode(self.pagina(url), 'latin-1'))
        Pens = self.__getPensamientos(pag)
        firstPenDate = self.__pensamientos[0][1]
        ret = []
        for p in Pens:
            if firstPenDate == p[1]:
                break
            else:
                ret.append(p)
        if len(ret) != 0:
            ret.reverse()
            for r in ret:
                self.__pensamientos.insert(0, r)
            ret.reverse()
            return ret
        else:
            return False

    def newOutPen(self):
        '''Binding para outboxNew y pensamientosNew para hacer una sola desgarga
           de la pagina. Devuelve: [outbouxNew] [pensamientosNew]'''
        url = "http://www.okeyko.com/v2/boceto.php"
        #pag = BS(unicode(self.pagina(url), 'latin-1'))
        pag = pq(unicode(self.pagina(url), 'latin-1'))
        return self.outboxNew(pag), self.pensamientosNew(pag)

    def set_leido(self, ok_id):
        ok_id = int(ok_id) + 1
        params = {'lastmsg': str(ok_id)}
        #url = "/nv02/0ajax_more.php"
        url = "http://www.okeyko.com/v2/0ajax_more.php"
        self.pagina(url,params)
        return

    def setFav(self, favId):
        url = 'http://www.okeyko.com/v2/fav-add.php?%s' % favId
        self.pagina(url)
        return

    def setNoFav(self, favId):
        url = 'http://www.okeyko.com/v2/fav-no.php?%s' % favId
        self.pagina(url)
        removeListInList(self.__favbox, favId)
        self.__favBor = True
        return

    def enviar_mensaje(self, para, men):
        #http://www.okeyko.com/nv02/ajax.php para= mensaje=
        if self.__conectado != True: return

        if type(para) == tuple or type(para) == list:
            if len(para) > 4:
                self.enviar_mensaje(para[:4])
                self.enviar_mensaje(para[4:])
                return True, "FIXME: mando True, por mandar xD"
            para = ','.join(para)
        para = para.replace("@","")
        #men = unicode( men, "utf-8").encode("iso-8859-1")
        #men = unicode( men, "utf-8")
        if len(men) > 250:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: mas de 250 caracteres \n" + para
            return False, "Mensaje con mas de 250 caracteres"
        url = "http://www.okeyko.com/v2/ajax.php"
        params =  {'para': para, 'mensaje': men}
        resp = self.pagina(url, params)
        if resp.find("<b>Warning</b>:") > 0:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: \n" + resp
            return  False, "warning"
        elif resp.find("Nombre de usuario:") > 0:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: Nombre de usuario incorrecto \n" + resp
            return  False, "Usuario inexistente o campos obligatorios vacios"
        elif resp.find("no salio") > 0:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: no salio \n" + resp
            return  False, "Mensaje no salio"
        else:
            print "============ Mensaje enviado con exito =========="
            self.__envio = True
            return True, "Mensaje enviado exitosamente"

    def enviarSms(self,para,men,captcha):
        #http://www.okeyko.com/nv02/SMS.php para= mensaje=
        if self.__conectado != True: return
        #men = unicode( men, "utf-8").encode("iso-8859-1")
        #men = unicode( men, "utf-8")
        if len(men) > 70:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: mas de 250 caracteres \n" + para
            return False, "SMS con mas de 70 caracteres"
        url = "http://www.okeyko.com/v2/SMS.php"
        cel = para[0]
        cel2 = para[1]
        params =  {'cel': cel, 'cel2': cel2, 'mensaje': men,
                   'security_code': captcha, 'Enviar':'Enviar' }
        resp = self.pagina(url, params)
        self.getCaptcha()
        if resp.find("seguridad incorrecto") > 0:
            print "============= Error Sms CAPTCHA ========== \n okeyko.enviar: \n" + resp
            return  False, "Error Captcha"
        else:
            print "============ Mensaje enviado con exito =========="
            return True, "Mensaje enviado exitosamente"         

    def estadoSet(self, estado):
        #http://www.okeyko.com/nv02/estadoajax.php estado
        if self.__conectado != True: return        
        if len(estado) > 250:
            print "============= Error estado ========== \n okeyko.estadoSet: mas de 250 caracteres \n" + para
            return False, "Mensaje con mas de 250 caracteres"
        if estado == "":
            estado = "Pensando en......"   
        try:
            #estado = unicode(estado, "utf-8").encode("iso-8859-1")
            #estado = estado.encode("iso-8859-1")
            #estado = unicode(estado, 'iso-8859-1')
            #estado = unicode(estado, 'iso-8859-1').encode('utf-8')
            estado = unicode(estado, 'iso-8859-1').encode('iso-8859-1')
        except:
            print "Exception in estadoSet while correcting Encoding"
        url = "http://www.okeyko.com/v2/estadoajax.php"
        params = {'estado': estado}
        resp = self.pagina(url, params)
        print "============ Estado cambiado =========="
        return True, "Estado cambiado"

    def agenda_lista(self, oname=False, redown=False):
        if self.__conectado != True: return
        if (self.__agenda_lista == None) | ( redown != False):
            url = "http://www.okeyko.com/v2/agenda/listado.php"
            resp = self.pagina(url).replace(" bgcolor='#DFDFDF'", "")
            agdict =  {"{usuario}":"(.*?)", "{nombre}":"(.*?)","{id}":"(.*?)"}
            template = """<tr><td><div align='center'><a href='../oky_agenda.php?agenda=@{usuario}'>@{bla}</a></div></td><td><div align='center'>{nombre}</div></td> <td><div align='center'><a href='eliminar.php?ok_id={id}'><img src='../images/iconos_mensajes/eliminar2.png' border='0' title='Eliminar'/></a><a href='black.php?ok_id={bla}<img src='../images/iconos_mensajes/bloqueo.png'  /></a>"""
            self.__agenda_lista = self.getInfo(resp, template, agdict, False)        
        if oname == True:
            ret = []
            for name in self.__agenda_lista:
                ret.append(name[0])
            return ret
        return self.__agenda_lista

    def agendaAdd(self, nom, desc):
        url = "http://www.okeyko.com/v2/agenda/index.php"
        params =  {'nombre_agenda': nom, 'descripcion_agenda': desc,
                   'action': 'checkdata', 'Submit': 'Agendar' }
        pag = self.pagina(url, params)
        self.agenda_lista(redown=True)
        if pag.find('Ojo Ojo!!') != -1:
            return False
        return True

    def agendaDel(self, agId):
        #http://www.okeyko.com/nv02/agenda/eliminar.php?ok_id=
        url = "http://www.okeyko.com/v2/agenda/eliminar.php?ok_id=%s" % agId
        self.pagina(url)
        removeListInList(self.__agenda_lista, agId)

    def agendaBlock(self, agId):
        #http://www.okeyko.com/nv02/agenda/black.php?ok_id=
        url = "http://www.okeyko.com/v2/agenda/black.php?ok_id=%s" % agId
        self.pagina(url)

    def inbox_bor(self, menid):
        elimina = {'Submit': 'Eliminar Seleccion'}
        if (type(menid) == tuple) | (type(menid) == list):
            for a in range(0, len(menid)):
                elimina.update({'elimina[%s]' % a : menid[a]})
        #if (type(menid) == tuple) | (type(menid) == list):
        #    menid = "&elimina[]=".join(menid)
        #elimina = "?Submit=Eliminar+Seleccion&elimina[]=%s" % menid
        url = "http://www.okeyko.com/v2/eliminar_sms.php"
        self.pagina(url, elimina)
        removeListInList(self.__inbox, menid)
        return
        
    def outbox_bor(self, menid):
        elimina = {'Submit': 'Eliminar Seleccion'}
        if (type(menid) == tuple) | (type(menid) == list):
            for a in range(0, len(menid)):
                elimina.update({'elimina[%s]' % a : menid[a]})
        #if (type(menid) == tuple) | (type(menid) == list):
        #    menid = "&elimina[]=".join(menid)
        #elimina = "?Submit=Eliminar+Seleccion&eliminae[]=%s" % menid
        url = "http://www.okeyko.com/v2/eliminar_sms_enviados.php"
        self.pagina(url, elimina)
        removeListInList(self.__outbox, menid)
        self.__outboxBor = True
        return

    def getInfo(self, html, template, tdict=False, openf=True):
        if openf:
            template = open(template)
            tem = "%s" % template.read()
            template.close()
        else:
            tem = template
        tem = tem.replace("\\", "\\\\")
        remdict = {"(":"\(", ")":"\)", "[":"\[", "]":"\]", ".":"\.", "^":"\^", \
                    "$":"\$", "*":"\*", "+":"\+", "?":"\?", "|":"\|" }
        for rem in remdict.iteritems():            
            tem = tem.replace(rem[0], rem[1])
        if tdict == False:
            tdict =  {"{avatar}":"(.*?)", "{emisor}":"(.*?)","{fecha}":"(.*?)", \
                    "{hora}":"(.*?)", "{mensaje}":"(.*?)", "{leido}":"(.*?)", \
                    "{fav}":"(.*?)", "{id}":"(.*?)" }
        for rem in tdict.iteritems():            
            tem = tem.replace(rem[0], rem[1])
        expdict = { "{bla}":".*?", "{espn}":"\\b?"}
        for rem in expdict.iteritems():            
            tem = tem.replace(rem[0], rem[1])
        mensajes = re.findall(tem, html, re.DOTALL)
        return mensajes
        
    def avatar(self,link,size='g'):
        if (size != 'g') & (size != 'm'): size = 'g'
        link = "http://www.okeyko.com/upload/imagenes/galeria/%s/%s" % (size, link)
        pag = self.pagina(link)
        return pag

    def changeAvatar(self, path):
        url = "http://www.okeyko.com/v2/upload_img/upload.php"
        params = {'Submit': "       Upload        ", 'file': open(path,'rb')}
        resp = self.pagina(url, post=params)
        return resp

    def pagina(self, link, post=None, get=None):
        #if self.__conectado != True: return
        resp = self.__download.open(link, post, get)
        ret = resp.read()
        resp.close()
        return ret

    def setProxy(self, host, port, user=None, passw=None):
        self.__download.setProxy("%s:%s" % (host, port), (user, passw))

    def disconnect(self):
        self.__download = urldownload()
        self.__conectado = False
        self.__usuario = None
        self.__contra = None
        self.__agenda_lista = None
        self.__inbox = False
        self.__outbox = False
        self.__outboxPag = False
        self.__outboxBor = False
        self.__favbox = False
        self.__favPag = False
        self.__favBor = False
        self.__avatar = False
        self.__avatarLink = None
        self.__estado = False
        self.__captcha = None
        self.__envio = False
        self.__pensamientos = None
             

if __name__ == "__main__":
    import getpass
    print "Bienvenidos a Okeyko"
    a = 1
    while a == 1:
        print "Conectarse a Okeyko"
        user = raw_input("Usuario: ")
        contra = getpass.getpass("Password: ")
        okemain = okeyko(user, contra)
        if okemain.conectado():
            a = 2
    while True: 
        print """Okeyko Via Consola
            1- Ver bandeja de entrada
            2- Enviar Mensaje
            3- Agenda
            4- Salir"""
        try:
            resp = raw_input("Que desea hacer? ")
            resp = int(resp)
        except:
            print "No insertaste numero"
        if resp == 1:
            mensajes = okemain.bandeja()
            mensajes.reverse()
            for mensaje in mensajes:
                print "==========================================="
                print "De:", mensaje[0] 
                print "Hora:", mensaje[1]
                print "----Mensaje-----"
                print mensaje[2]        
            print "==========================================="
        if resp == 2:
            para = raw_input("Para: @")
            men = raw_input("Mensaje:")
            result, rta = okemain.enviar_mensaje(para, men)
            if result != True:
                print rta
            print rta
        if resp == 3:
            agendas = okemain.agenda_lista()
            for agenda in agendas:
                print "----------------"
                print "Okeyko:", agenda[0], "Desc:", agenda[1]
            print "----------------"
        if resp == 4:
            print "Saliendo"
            break
