import re
import httplib, urllib
#from xml.etree import ElementTree as ET
#import htmlentitydefs

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

def changeEntities(str):
    str = str.encode( "utf-8" )
    lst = htmlentitydefs.name2codepoint
    for find, replace in lst.iteritems():
        find = "&%s;" % (find)
        replace = unichr(int(replace))
        #replace = "&%s;" % (replace)
        str = str.replace(find, replace)
    return str

def toEntities(str):
    print "pre %s" % (str)
    #lst = htmlentitydefs.codepoint2name
    #for find, replace in lst.iteritems():
        #replace = "&#%s;" % (find)
        #replace = "&%s;" % (replace)
        #find = unichr(int(find))
        #str = str.replace(find, replace)
    #str = unicode(str, "iso-8859-1")
    #str = unicode(str, "utf-8")
    #print "pos %s" % (str)
    return str

class okeyko:
    def __init__(self):
        self.__dom = "www.okeyko.com"
        self.__conectado = False
        self.__cookie = None
        self.__usuario = None
        self.__contra = None

    def login(self, usuario, contra):
        self.__usuario = usuario if (usuario[:1] != "@") else usuario[1:]
        self.__contra = contra
        self.set_cookie()
        return

    def set_cookie(self):
        if (self.__usuario == None) | (self.__contra == None): 
            self.__conectado = False
            self.__conectado_result = "Usuario o Pass no seteadas"
            return
        url = "/nv02/validar_usuario.php" #Cambios para okeyko2.0
        params =  urllib.urlencode({'usuario': self.__usuario, 'clave': self.__contra}) #Ok2.0
        #params =  {'usuario': self.__usuario, 'clave': self.__contra} #Ok2.0
        resp = download(self.__dom, url, params, True, None, True, True)
        self.__cookie = resp.getheader("set-cookie")
        pag = resp.read()
        resp.close()
        if pag.find("Password o Usuario incorrecto") != -1: #Ok2.0
            self.__conectado = False
            self.__conectado_result = pag #Ok2.0
            print self.__conectado_result
            #return
        self.__conectado = True if (pag.find("Has iniciado sesion exitosamente")) else False #Ok2.0
        self.__conectado_result = pag #Ok2.0
        print self.__conectado_result
        return

    def conectado(self):
        if self.pagina("/busca_filtrado.php") == "no esta logeado": self.set_cookie()
        return self.__conectado, self.__conectado_result

    def bandeja(self):
        if self.__conectado != True: return
        url = "/nv02/0ajax_more.php"
        params = urllib.urlencode({'lastmsg': '9999999999999'})
        pag = self.pagina(url, params)
        mensajes = self.getInfo(pag,"libokeykoTre")
        #print ET.XML(pag)
        #for sub in resp:
        #    de = sub[0].text if ( sub[0].text != None ) else ""
        #    hora = "%s // %s" % (sub[1].text,sub[2].text) if ( sub[1].text != None ) | ( sub[2].text != None ) else ""
        #    mensaje = sub[3].text if ( sub[3].text != None ) else ""
        #    okid = sub[4].text if ( sub[4].text != None ) else ""
        #    avatar = sub[5].text if ( sub[5].text != None ) else "perfil.png"
        #    leido = sub[6].text if ( sub[6].text != None ) else ""
        #    fav = sub[7].text if ( sub[6].text != None ) else ""
        #    enviado = sub[8].text if ( sub[6].text != None ) else ""
        #    mensajes.append([de,hora,mensaje,okid,avatar,leido,fav,enviado])
        menord = []
        for men in mensajes:
            leido = "1" if (men[6] == "Leido desde la PC ") else "2"
            menord.append((men[1],men[2]+men[3],men[4],men[6],men[0],leido,None,None))
        mensajes = menord
        return mensajes

    def bandeja_nuevos(self, minid= None):
        pass
        #http://www.okeyko.com/nv02/nuevos.php
        url = "/nv02/nuevos.php"
        pag = self.pagina(url)
        print pag
        return
        #if resp.text == None: return False
        #for sub in resp:
        #    de = sub[0].text if ( sub[0].text != None ) else ""
        #    hora = "%s // %s" % (sub[1].text,sub[2].text) if ( sub[1].text != None ) | ( sub[2].text != None ) else ""
        #    mensaje = sub[3].text if ( sub[3].text != None ) else ""
        #    okid = sub[4].text if ( sub[4].text != None ) else ""
        #    avatar = sub[5].text if ( sub[5].text != None ) else "perfil.png"
        #    leido = sub[6].text if ( sub[6].text != None ) else ""
        #    fav = sub[7].text if ( sub[6].text != None ) else ""
        #    enviado = sub[8].text if ( sub[6].text != None ) else ""
        #    mensajes.append([de,hora,mensaje,okid,avatar,leido,fav,enviado])
        #try:
        #    asd = mensajes[0][3]
        #except:
        #    mensajes = False
        #return mensajes

    def set_leido(self, ok_id):
        url = "/cleinte/api.php?tipo=set_leido&ok_id=%s" % (ok_id)
        self.pagina(url)
        return

    def salida(self):
        return [["","","","","",""]]
        if self.__conectado != True: return
        url = "/cleinte/api.php?tipo=outbox"
        mensajes = []
        resp = ET.XML(self.pagina(url))
        for sub in resp:
            para = sub[0].text if ( sub[0].text != None ) else ""
            hora = "%s // %s" % (sub[1].text,sub[2].text) if ( sub[1].text != None ) | ( sub[2].text != None ) else ""
            mensaje = sub[3].text if ( sub[3].text != None ) else ""
            okid = sub[4].text if ( sub[4].text != None ) else ""
            avatar = sub[5].text if ( sub[5].text != None ) else "perfil.png"
            leido = sub[6].text if ( sub[6].text != None ) else ""
            mensajes.append([para,hora,mensaje,okid,avatar,leido])
        return mensajes

    def enviar_mensaje(self, para, men):
        #http://www.okeyko.com/nv02/ajax.php para= mensaje=
        if self.__conectado != True: return
        para = para.replace("@","")
        men = unicode( men, "utf-8").encode("iso-8859-1")
        if len(men) > 250:
            print "============= Error enviando mensaje ========== \n okeyko.enviar: mas de 250 caracteres \n" + para
            return False, "Mensaje con mas de 250 caracteres"
        url = "/nv02/ajax.php"
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
            return True, "Mensaje enviado exitosamente"        

    def agenda_lista(self):
        if self.__conectado != True: return
        url = "/agenda/listado.php"
        respa = download(self.__dom, url, None, False, self.__cookie)
        resp = respa.read()
        respa.close()
        agenda = []
        while resp.find("'> Bloquear</a>") > 0:
            okeyko = search_between("<a href='../okey.php?agenda=", "'>", resp).strip()
            desc = search_between("</a></div></td><td><div align='center'>", "</div></td> <td><div align='center'><a href='eliminar.php?ok_id=", resp)
            try: okid = int(search_between("eliminar_sms.php?ok_id=", "</div></td> <td><div align='center'><a href='eliminar.php", resp))
            except: okid = search_between("<a href='eliminar.php?ok_id=", "'>Eliminar</a", resp)
            agenda = agenda + [[okeyko,desc,okid]]
            resp = resp[resp.find("'> Bloquear</a>")+len("'> Bloquear</a>"):]
        return agenda

    def borrar_rev(self, menid):
        if (type(menid) == tuple) | (type(menid) == list):
            menid = "&elimina[]=".join(menid)
        elimina = "?Submit=Eliminar+Seleccion&elimina[]=%s" % menid
        url = "/nv02/eliminar_sms.php"
        print self.pagina(url, elimina)
        return
        
    def borrar_env(self, menid):
        if (type(menid) == tuple) | (type(menid) == list):
            menid = "&elimina[]=".join(menid)
        elimina = "?Submit=Eliminar+Seleccion&eliminae[]=%s" % menid
        url = "/nv02/eliminar_sms_enviados.php"
        print self.pagina(url, elimina)
        return

    def getInfo(self, html, template, tdict=False):
        template = open(template)
        tem = "%s" % template.read()
        template.close()
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
        repl = ""
        for a in range(1, len(tdict)+1):
            repl = "%s{||}\g<%s>"% (repl, a)
        mensajes = re.findall(tem, html, re.DOTALL)
        #mensajes = []        
        #for mensaje in re.findall(tem, html): #TODO: Finish
        #for mensaje in re.findall("<li>(.*?)</li>",html, re.DOTALL): #TODO: Finish
        #    premen = re.sub(tem, repl, mensaje)
        #    premen = premen.split("{||}")
        #    mensajes.append(premen)
        return mensajes

    def pagina(self,link,post=None):
        if self.__conectado != True: return
        clength = False if (post == None) else True
        link = "/%s" % link if ( link[0] != "/" ) else link
        #resp = download(self.__dom, link, post, False, self.__cookie)
        resp = download(self.__dom, link, post, True, self.__cookie, True, clength)
        ret = resp.read()
        resp.close()
        return ret        

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
