import re
import httplib, urllib
import htmlentitydefs
from BeautifulSoup import BeautifulSoup
#from xml.etree import ElementTree as ET

def download(dom, url, params=None, ref=False, cookie=None, ctype=False, clength=False):

    headers = {
                "User-Agent": "Mozilla/5.0 (X11; U; Linux i686; es-AR; rv:1.9.1.9) Gecko/20100401 Ubuntu/9.10 (karmic) Firefox/3.5.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ar,es;q=0.8,en-us;q=0.5,en;q=0.3",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Keep-Alive": "300",
                "Proxy-Connection": "keep-alive"
                }
    if ref:
        headers["Referer"] = "http://www.okeyko.com/default.php"
        #headers["Referer"] = "http://www.okeyko.com/iphone/index.php"
    if cookie:
        headers["Cookie"] = cookie
    if ctype:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if clength:
        headers["Content-Length"] = len(params)
    
    conn = httplib.HTTPConnection(dom, 80)
    if params:
        conn.request("POST", url, params, headers)
    else:
        conn.request("GET", url, params, headers)
    resp = conn.getresponse()
    return resp

def search_between(ini, end, html):
    try:
        html = html[html.find(ini) + len(ini):]
        html = html[:html.find(end)]
        return html
    except:
        return None

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

def BS(html):
    return BeautifulSoup(unescape(html), convertEntities=BeautifulSoup.HTML_ENTITIES)

def removeListInList(lsts, x):
    for lst in lsts:
        try:
            lst.index(x)
            lsts.remove(lst)
        except:
            pass


class okeyko:
    def __init__(self):
        self.__dom = "www.okeyko.com"
        self.__conectado = False
        self.__cookie = None
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
        self.__estado = False
        self.__captcha = None
        self.__envio = False
        self.__pensamientos = None
        

    def login(self, usuario, contra):
        self.__usuario = usuario if (usuario[:1] != "@") else usuario[1:]
        self.__contra = contra
        self.set_cookie()
        if self.__conectado:
           self.get_all()
        return

    def set_cookie(self):
        if (self.__usuario == None) | (self.__contra == None): 
            self.__conectado = False
            self.__conectado_result = "Usuario o Pass no seteadas"
            return
        #url = "/nv02/validar_usuario.php" #Cambios para okeyko2.0
        url = "/v2/validar_usuario.php" #Cambios para okeyko2.0
        params =  urllib.urlencode({'usuario': self.__usuario, 'clave': self.__contra}) #Ok2.0
        #params =  {'usuario': self.__usuario, 'clave': self.__contra} #Ok2.0
        resp = download(self.__dom, url, params, True, None, True, True)
        self.__cookie = resp.getheader("set-cookie")
        pag = resp.read()
        resp.close()
        if pag.find("Password o Usuario incorrecto") != -1: #Ok2.0
            self.__conectado = False
            self.__conectado_result = BS(pag).text #Ok2.0
            return
        self.__conectado = True if (pag.find("exitosamente")) else False #Ok2.0
        self.__conectado_result = BS(pag).text #Ok2.0
        print self.__conectado_result
        return

    def conectado(self):
        #if self.pagina("/nv02/index.php").find("|| Hola") == -1:
        if self.pagina("/v2/index.php").find("|| Hola") == -1:
            self.__conectado = False
            self.set_cookie()
        return self.__conectado, self.__conectado_result
        
    def get_all(self):
        ''' Obtiene: inbox, outbox, avatar, estado'''
        if self.__conectado != True: return
        #url = "/nv02/boceto.php"
        url = "/v2/boceto.php"
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        pag = BS(unicode(self.pagina(url), 'latin-1'))
        avt = pag.find('img',{'title':'Usuario', 'class':'reflect rheight20'})['src']
        self.__avatarLink = avt[avt.rfind('/')+1:]
        self.__avatar = self.avatar(self.__avatarLink,'m')
        try:
            self.__estado = pag.find('b',{'style':'color:#FFF;'}).text
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
        #url = '/nv02/CaptchaSecurityImages.php?width=100&height=40&characters=5'
        url = '/v2/CaptchaSecurityImages.php?width=100&height=40&characters=5'
        self.__captcha = self.pagina(url)

    def captcha(self):
        return self.__captcha

    def getMoreInbox(self):
        lastOId = self.__inbox[len(self.__inbox) - 1][3]
        params = urllib.urlencode({'lastmsg': str(lastOId)})
        #url = "/nv02/0ajax_more.php"
        url = "/v2/0ajax_more.php"
        #pag = BS(unescape(unicode(self.pagina(url,params), 'latin-1')))
        pag = BS(unicode(self.pagina(url,params), 'latin-1'))
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
        #url = "/nv02/boceto_enviados.php?paginae=%s" % self.__outboxPag
        #url = "/nv02/boceto.php?paginae=%s" % self.__outboxPag
        url = "/v2/boceto.php?paginae=%s" % self.__outboxPag
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        pag = BS(unicode(self.pagina(url), 'latin-1'))
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
        #url = "/nv02/boceto.php?pagina=%s" % self.__favPag
        url = "/v2/boceto.php?pagina=%s" % self.__favPag
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        pag = BS(unicode(self.pagina(url), 'latin-1'))
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
            
    def __getInbox(self, BShtml):
        lis = BShtml.findAll('li')
        menInbox = []
        for i in range(0, len(lis) - 4 ):
            li = lis[i + 4]
            de = li.findAll('a')[1].string
            hora = li.find('td',{'align':'right'}).text
            mensaje = li.findAll('br')[5].next
            Oik = li.label['for']
            avatar = li.img['src'][li.img['src'].rfind('/')+1:]
            leido = li.findAll('div',{'style': ' font-size:11px; color:#666;' \
                    })[0].contents[0]
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            favImg = li.find('img', {'src': 'images/iconos_mensajes/favoritos2.png'})
            favHref = favImg.parent['href']
            #fav = favHref[favHref.rfind('=')+1:]
            fav = favHref[favHref.rfind('&')+1:]
            menInbox.append([de, hora, mensaje, Oik, avatar, leido, fav])
        return menInbox

    def __getOutbox(self, BShtml):
        outTab = BShtml.find('div',{'id':'tab2'})
        outs = outTab.findAll('div',{'class':'conten_mensaje'})
        menOutbox = []
        for out in outs:
            mensaje = out.find('div', {'id':'cuerpo_mensaje'}).text
            ph = out.find('div',{'id':'mensaje_head'}).text
            para = ph[ph.find('">')+2:ph.find('|')]
            hora = ph[ph.find('|')+1:ph.rfind('|')]
            Oid = out.find('div',{'id':'herramientas'}).input['value']
            avatar = self.__avatarLink #TODO: Get avatar
            leido = out.find('div',{'id':'herramientas'}).text
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            menOutbox.append([para, hora, mensaje, Oid, avatar, leido]) 
        return menOutbox   

    def __getFavs(self, BShtml):
        favsTab = BShtml.find('div',{'id':'tab3'})
        if favsTab.text.find('No tiene mensajes') != -1:
            return False
        favs = favsTab.findAll('div',{'class':'conten_mensaje'})
        menFav = []
        for fav in favs:
            mensaje = fav.find('div', {'id':'cuerpo_mensaje'}).text
            ph = fav.find('div',{'id':'mensaje_head'}).text
            para = ph[ph.find('">')+2:ph.find('|')]
            hora = ph[ph.find('|')+1:ph.rfind('|')]
            Oid = fav.find('div',{'id':'herramientas'}).input['value']
            avatarSrc = fav.find('img')['src']
            avatar = avatarSrc[avatarSrc.rfind('/')+1:]
            leido = fav.find('div',{'id':'herramientas'}).text
            if leido.find('MOVIL') != -1:
                leido = 1
            elif leido.find('PC') != -1:
                leido = 2
            else:
                leido = 0
            favImg = fav.find('img', {'src': 'images/iconos_mensajes/favoritos2.png'})
            favHref = favImg.parent['href']
            #fav = favHref[favHref.rfind('=')+1:]
            fav = favHref[favHref.rfind('&')+1:]
            menFav.append([para, hora, mensaje, Oid, avatar, leido, fav]) 
        return menFav

    def __getPensamientos(self, BShtml):
        penTab = BShtml.find('div',{'id':'tab4'})
        pens = penTab.findAll('table')
        pensamientos = []
        for pen in pens:
            de = pen.findAll('td')[1].text[4:]
            trs = pen.findAll('tr')
            mensaje = trs[1].text
            hora = trs[2].text
            Oid = 'a'
            avatar = pen.find('img')['src']
            avatar = avatar[avatar.rfind('/')+1:]
            pensamientos.append([de, hora, mensaje, Oid, avatar]) 
        return pensamientos

    def userinfo(self):
        if self.__conectado != True: return
        return self.__usuario, self.__avatar, self.__estado

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
        #url = "/nv02/nuevos.php"
        url = "/v2/nuevos.php"
        pag = self.pagina(url).strip()
        #print pag
        if pag == "</form >":
            return False
        #pag = BS(unescape(unicode(pag, 'latin-1')))
        pag = BS(unicode(pag, 'latin-1'))
        tables = pag.findAll('table')
        tablesN = len(tables) / 3
        inboxNew = []
        for i in range(0, tablesN):
            table = tables[i * 3]
            de = table.findAll('a')[1].text
            de = de[de.find(">")+1:]
            hora = table.find('td',{'align':'right'}).text
            mensaje = table.findAll('br')[6].next.string.strip()
            Oik = table.find('div',{'style':'display:none; padding:5px; '
                + 'margin-left:30px;margin-right:30px;background-color:'
                + '#F2F2F2'})['id'].replace('_','')
            avatar = table.img['src']
            avatar = avatar[avatar.rfind('/')+1:]
            leido = table.find('div', \
                {'style':' font-size:11px; color:#666;'}).text
            leido = 0 #TODO: Arreglar leido
            fav = 0 #TODO: Get Favorito
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
            url = "/v2/boceto.php"
            pag = BS(unicode(self.pagina(url), 'latin-1'))
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
        #url = "/nv02/boceto.php"
        url = "/v2/boceto.php"
        #pag = BS(unescape(unicode(self.pagina(url), 'latin-1')))
        pag = BS(unicode(self.pagina(url), 'latin-1'))
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
        url = "/v2/boceto.php"
        pag = BS(unicode(self.pagina(url), 'latin-1'))
        self.__pensamientos = self.__getPensamientos(pag)
        return self.pensamientos()

    def pensamientosNew(self, pag=None):
        '''Devuelve si hay, pensamientos nuevos'''
        if self.__conectado != True: return
        if pag == None:
            url = "/v2/boceto.php"
            pag = BS(unicode(self.pagina(url), 'latin-1'))
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
        url = "/v2/boceto.php"
        pag = BS(unicode(self.pagina(url), 'latin-1'))
        return self.outboxNew(pag), self.pensamientosNew(pag)

    def set_leido(self, ok_id):
        ok_id = int(ok_id) + 1
        params = urllib.urlencode({'lastmsg': str(ok_id)})
        #url = "/nv02/0ajax_more.php"
        url = "/v2/0ajax_more.php"
        self.pagina(url,params)
        return

    def setFav(self, favId):
        #url = '/nv02/fav-add.php?%s' % favId
        url = '/v2/fav-add.php?%s' % favId
        self.pagina(url)
        return

    def setNoFav(self, favId):
        #url = '/nv02/fav-no.php?%s' % favId
        url = '/v2/fav-no.php?%s' % favId
        self.pagina(url)
        removeListInList(self.__favbox, favId)
        self.__favBor = True
        return

    def enviar_mensaje(self, para, men):
        #http://www.okeyko.com/nv02/ajax.php para= mensaje=
        if self.__conectado != True: return
        para = para.replace("@","")
        #men = unicode( men, "utf-8").encode("iso-8859-1")
        #men = unicode( men, "utf-8")
        if len(men) > 250:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: mas de 250 caracteres \n" + para
            return False, "Mensaje con mas de 250 caracteres"
        #url = "/nv02/ajax.php"
        url = "/v2/ajax.php"
        params =  urllib.urlencode({'para': para, 'mensaje': men}) 
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
        #url = "/nv02/SMS.php"
        url = "/v2/SMS.php"
        cel = para[0]
        cel2 = para[1]
        params =  urllib.urlencode({'cel': cel, 'cel2': cel2, 'mensaje': men,
                                    'security_code': captcha, 'Enviar':'Enviar'}) 
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
        try:
           estado = estado.encode("iso-8859-1")
        except:
           pass
        #url = "/nv02/estadoajax.php"
        url = "/v2/estadoajax.php"
        params =  urllib.urlencode({'estado': estado}) 
        resp = self.pagina(url, params)
        print "============ Estado cambiado =========="
        return True, "Estado cambiado"

    def agenda_lista(self, oname=False, redown=False):
        if self.__conectado != True: return
        if (self.__agenda_lista == None) | ( redown != False):
            #url = "/nv02/agenda/listado.php"
            url = "/v2/agenda/listado.php"
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
        #url = "/nv02/agenda/index.php"
        url = "/v2/agenda/index.php"
        params =  urllib.urlencode({'nombre_agenda': nom,
                                    'descripcion_agenda': desc,
                                    'action': 'checkdata',
                                    'Submit': 'Agendar'})
        pag = self.pagina(url, params)
        self.agenda_lista(redown=True)
        if pag.find('Ojo Ojo!!') != -1:
            return False
        return True

    def agendaDel(self, agId):
        #http://www.okeyko.com/nv02/agenda/eliminar.php?ok_id=
        #url = "/nv02/agenda/eliminar.php?ok_id=%s" % agId
        url = "/v2/agenda/eliminar.php?ok_id=%s" % agId
        self.pagina(url)
        removeListInList(self.__agenda_lista, agId)

    def agendaBlock(self, agId):
        #http://www.okeyko.com/nv02/agenda/black.php?ok_id=
        #url = "/nv02/agenda/black.php?ok_id=%s" % agId
        url = "/v2/agenda/black.php?ok_id=%s" % agId
        self.pagina(url)

    def inbox_bor(self, menid):
        if (type(menid) == tuple) | (type(menid) == list):
            menid = "&elimina[]=".join(menid)
        elimina = "?Submit=Eliminar+Seleccion&elimina[]=%s" % menid
        #url = "/nv02/eliminar_sms.php"
        url = "/v2/eliminar_sms.php"
        self.pagina(url, elimina)
        removeListInList(self.__inbox, menid)
        return
        
    def outbox_bor(self, menid):
        if (type(menid) == tuple) | (type(menid) == list):
            menid = "&elimina[]=".join(menid)
        elimina = "?Submit=Eliminar+Seleccion&eliminae[]=%s" % menid
        #url = "/nv02/eliminar_sms_enviados.php"
        url = "/v2/eliminar_sms_enviados.php"
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
        link = "/upload/imagenes/galeria/%s/%s" % (size, link)
        pag = self.pagina(link)
        return pag

    def pagina(self,link,post=None):
        #if self.__conectado != True: return
        clength = False if (post == None) else True
        link = "/%s" % link if ( link[0] != "/" ) else link
        #resp = download(self.__dom, link, post, False, self.__cookie)
        resp = download(self.__dom, link, post, True, self.__cookie, True, clength)
        ret = resp.read()
        resp.close()
        return ret

    def disconnect(self):
        self.__conectado = False
        self.__cookie = None
        self.__usuario = None
        self.__contra = None
        self.__agenda_lista = None
        self.__inbox = False
        self.__outbox = False
        self.__outboxPag = False
        self.__avatar = False
        self.__estado = False
             

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
