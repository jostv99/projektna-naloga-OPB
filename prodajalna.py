from functools import wraps
from presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

import os, psycopg2, psycopg2.extensions, psycopg2.extras, hashlib
from services.auth_service import AuthService
from services.oglas_service import OglasService
from services.kategorija_service import KategorijaService
import auth as auth
import re

#popravi bazo da so def sporocila {} in ne NULL, da sporocila shranijo od koga so prisla.....
#dodaj viewed za najbolj ogledane oglase?
#dodaj da je ogled svojega profila drugacen--urejanje, dodajanje info, oglasov, branje sporocil...
#css, urejanje html, lepsi izgled...
#spremeni bazo, da vzame vec slik, kot sporocila...array


SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

authS = AuthService()
oglasS = OglasService()
katS = KategorijaService() 

dirname = os.path.dirname(__file__)

def cookie_required(f):
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik",secret=auth.skrivnost)
        if cookie:
            return f(*args, **kwargs)
        return template("login.html",uporabnik=None,napaka="Potrebna je prijava!")
        
    return decorated



@get('/presentation/static/images/<filename:path>')
def static_images(filename):
    return static_file(filename, root='presentation/static/images')

@get('/presentation/static/<filename:path>')
def static(filename):
    return static_file(filename, root='presentation/static')

@get('/')
@cookie_required
def index():
    oglasi = oglasS.dobi_nakljucne_oglase(10)
    zadnji_oglasi = oglasS.dobi_zadnje_oglase(10)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik:
        trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
        return template('index.html', oglasi=oglasi,zadnji_oglasi=zadnji_oglasi,uporabnik=trenutni_uporabnik)
    else:
        return template('index.html', oglasi=oglasi,zadnji_oglasi=zadnji_oglasi,uporabnik=None)
@get('/login')
def login():
    return template("login.html",uporabnik=None,napaka=None)

@post('/login')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not authS.obstaja_uporabnik(username):
        return template("login.html",uporabnik=None,napaka="Uporabnik s tem imenom ne obstaja")

    prijava = authS.prijavi_uporabnika(username, password)
    if prijava:
        response.set_cookie("uporabnik", username,secret=auth.skrivnost)
        redirect(url('/'))
        
    else:
        return template("login.html",uporabnik=None,napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")


@get('/logout')
def logout():
    response.delete_cookie("uporabnik")
    
    return template('login.html', uporabnik=None,napaka=None)


@get('/register')
def register():
    return template("register.html", napaka=None, uporabnik=None)

@post('/register')
def register_post():
    username = request.forms.get('username')
    password = request.forms.get('password')  
    email = request.forms.get('email')
    
    if password ==  '' or username == '' or email == '':
        return template("register.html", uporabnik=None,napaka="Prosimo vnesite podatke v vsa polja!")
    
    if authS.obstaja_uporabnik(username):
        return template("register.html", uporabnik=None, napaka="To uporabniško ime je že zasedeno, prosim izberite drugo.")

    #se pregledas ksne pogoje...

    uporabnik = authS.dodaj_uporabnika(username,password,email,'','')
    #popravi da samo vpise geslo, ki ni hash,
    return template("login.html", uporabnik=uporabnik, napaka=None)

@get('/ad/<x:int>')
def oglas(x):
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik:
        trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik) 
    if oglasS.obstaja_oglas(x):
        oglas = oglasS.dobi_oglas(x)
        print(oglas.slika)
        return template("oglas.html", oglas=oglas,uporabnik=trenutni_uporabnik,napaka=None)
    else:
        return template("oglas.html",oglas=None,uporabnik=trenutni_uporabnik,napaka=None)

@post('/ad/<x:int>')
@cookie_required
def oglas_post(x):
    oglas = oglasS.dobi_oglas(x)
    sporocilo = request.forms.get('sporocilo')
    prodajalec = authS.dobi_uporabnika(oglas.prodajalec)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)  
    if sporocilo == "":
        return template("oglas.html",oglas=oglas,uporabnik=trenutni_uporabnik,napaka="Sporočilo mora imeti vsebino.")      
    sporocilo = '{'+'['+trenutni_uporabnik.uporabnisko_ime+','+str(oglas.id)+','+sporocilo+','+'False'+']'+'}'
    authS.poslji_sporocilo(prodajalec,sporocilo)
    return template("oglas.html",oglas=oglas,uporabnik=trenutni_uporabnik,napaka="Sporočilo uspešno poslano!")

@get('/user/<username>')
@cookie_required
def user(username):
    if not authS.obstaja_uporabnik(username):
        return template("profil.html",uporabnik=None,t_uporabnik=None,oglasi=None,napaka=None)
    uporabnik = authS.dobi_uporabnika(username)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    if uporabnik.uporabnisko_ime == trenutni_uporabnik:
        return template("lasten_profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka=None)  
    trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)  
    return template("profil.html",uporabnik=trenutni_uporabnik,t_uporabnik=uporabnik,oglasi=oglasi,napaka=None)

@get('/user/<username>/new_ad')
@cookie_required
def new_ad(username):
    uporabnik = authS.dobi_uporabnika(username)
    kategorije = katS.vrni_vse_kategorije()
    return template("nov_oglas", uporabnik=uporabnik, kategorije=kategorije,napaka=None)

@post('/user/<username>/new_ad')
@cookie_required
def new_ad_post(username): #dodaj kaksen error...
    uporabnik = authS.dobi_uporabnika(username)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    naslov = request.forms.get('naslov')
    opis = request.forms.get('opis')
    cena = request.forms.get('cena')
    if naslov == "":
        kategorije = katS.vrni_vse_kategorije()
        return template("nov_oglas", uporabnik=uporabnik, kategorije=kategorije, napaka="Oglas potrebuje naslov!")
    elif opis == "":
        kategorije = katS.vrni_vse_kategorije()
        return template("nov_oglas", uporabnik=uporabnik, kategorije=kategorije, napaka="Oglas potrebuje opis!")
    elif cena == "":
        kategorije = katS.vrni_vse_kategorije()
        return template("nov_oglas", uporabnik=uporabnik, kategorije=kategorije, napaka="Oglas potrebuje ceno!")
    kategorija = request.forms.get('kategorija')
    slika = request.files['slika']
    filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", slika.filename)
    slika.save(os.path.join(dirname,'presentation','static','images'),filename)
    oglasS.naredi_oglas(uporabnik,naslov,opis,cena,kategorija,filename)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    return template("lasten_profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka="Oglas uspešno narejen!")  

@get('/user/<username>/remove_ad_<id>') #pogoj na sliko ne dela? nalozi lahko katerokoli datoteko
@cookie_required
def remove_ad(username, id):
    oglasS.izbrisi_oglas(id)
    uporabnik = authS.dobi_uporabnika(username)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    slika = request.files['slika']
    filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", slika.filename)
    os.remove(os.path.join(dirname,'presentation','static','images'),filename)
    return template("lasten_profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka="Oglas uspešno izbrisan!")  

@get('/user/<username>/messages')
@cookie_required
def messages(username):
    uporabnik = authS.dobi_uporabnika(username)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if not uporabnik.uporabnisko_ime == trenutni_uporabnik:
        return template("napaka.html")
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    sporocila = authS.dobi_sporocila(uporabnik)
    sporocila = sporocila[0]
    sporocila = razgradi(sporocila)
    nova = []
    ogledana = []
    for sporocilo in sporocila:
        print("for sporocila")
        print(sporocilo)
        if sporocilo[3] == 'False':
            nova.append(sporocilo)
        else:
            ogledana.append(sporocilo)
    print(sporocila)
    print(nova)
    print(ogledana)
    return template("sporocila.html", uporabnik=uporabnik,sporocila=sporocila,nova=nova,ogledana=ogledana,oglasi=oglasi)

@get('/user/<username>/reply/<sporocilo>')
@cookie_required
def message_reply(username, sporocilo):
    uporabnik = authS.dobi_uporabnika(username)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if not uporabnik.uporabnisko_ime == trenutni_uporabnik:
        return template("napaka.html")
    sporocilo = seznam_iz_str(sporocilo)
    print("get od sporocil:")
    print(sporocilo)
    if sporocilo[3] == 'False':
        authS.preberi_sporocilo(sporocilo,uporabnik)
    return template("message_reply.html", uporabnik=uporabnik,sporocilo=sporocilo,napaka=None)

@post('/user/<username>/reply/<sporocilo>')
@cookie_required
def message_reply(username,sporocilo):
    uporabnik = authS.dobi_uporabnika(username)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if not uporabnik.uporabnisko_ime == trenutni_uporabnik:
        return template("napaka.html")
    sporocilo = seznam_iz_str(sporocilo)   
    msg = request.forms.get("msg")
    if msg == "":
        return template("message_reply.html",uporabnik=uporabnik,sporocilo=sporocilo,napaka="Sporočilo mora imeti vsebino!")
    msg = '{'+'['+uporabnik.uporabnisko_ime+','+sporocilo[1]+','+msg+','+'False'+']'+'}'
    towho = authS.dobi_uporabnika(sporocilo[0])
    authS.poslji_sporocilo(towho,msg)
    return template("message_reply.html",uporabnik=uporabnik,sporocilo=sporocilo,napaka="Sporočilo uspešno poslano!")
    
    

@post('/search')
@cookie_required
def search_post():
    item = request.forms.get("search")
    oglasi = oglasS.isci_oglase(item)
    uporabnik=None
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik is not None:
        uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
    if item == "":
        return template("search.html",oglasi=None,uporabnik=None,iskanje=None, napaka="V iskalno polje vnesite vsaj en znak!")
    return template("search.html",oglasi=oglasi,uporabnik=uporabnik,iskanje=item,napaka=None)

@get('/search/<item>')
@cookie_required
def search(item):
    item = item[7:]
    oglasi = oglasS.isci_oglase(item)
    uporabnik=None
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik is not None:
        uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
    return template("search.html",oglasi=oglasi,uporabnik=uporabnik,iskanje=item,napaka=None)

@get('/user/<username>/edit')
@cookie_required
def uredi_profil(username):
    uporabnik = authS.dobi_uporabnika(username) 
    return template("uredi_profil.html", uporabnik=uporabnik)
    
@post('/user/<username>/edit')
@cookie_required
def uredi_profil_post(username):
    uporabnik = authS.dobi_uporabnika(username)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    up_ime = request.forms.get('up_ime')
    geslo = request.forms.get('geslo')
    telefon = request.forms.get('telefon')
    email = request.forms.get('email')
    
    return template("lasten_profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka="Podatki uspošno posodobljeni!")

@get('/search_cat')
@cookie_required
def search_cat():
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik is not None:
        uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
    cat = katS.vrni_vse_kategorije()
    return template("search_cat.html", cat=cat, oglasi=None,uporabnik=uporabnik,napaka=None)

@get('/search_cat/<cat>')
@cookie_required
def search_catf(cat):
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik is not None:
        uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
    oglasi = oglasS.oglas_by_cat(cat)
    print("oglasi:")
    print(cat)
    print(oglasi)
    return template("search_catf.html", cat=None, oglasi=oglasi,uporabnik=uporabnik,napaka=None)
    
    


############################################## POMOZNO

def razgradi(seznam):
    print(seznam)
    chunk_size = 4
    result = []
    for i in range(0, len(seznam), chunk_size):
        chunk = seznam[i:i + chunk_size]
        chunk[0] = chunk[0].strip('[]')
        chunk[3] = chunk[3].strip('[]')
        result.append(chunk)
    return result

def seznam_iz_str(str):
    ls = str.strip('[]').replace(", ",",").replace("'", '').split(',')
    return ls






conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#authS.dodaj_uporabnika('admin','admin','admin','admin','admin')
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)