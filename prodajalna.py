from functools import wraps
from presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

import os, psycopg2, psycopg2.extensions, psycopg2.extras, hashlib
from services.auth_service import AuthService
from services.oglas_service import OglasService
from services.kategorija_service import KategorijaService
import auth as auth

#popravi bazo da so def sporocila {} in ne NULL 
#dodaj viewed za najbolj ogledane oglase?
#dodaj da je ogled svojega profila drugacen--urejanje, dodajanje info, oglasov, branje sporocil...
#css, urejanje html, lepsi izgled...

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

authS = AuthService()
oglasS = OglasService()
katS = KategorijaService() 

def cookie_required(f):
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik",secret=auth.skrivnost)
        if cookie:
            return f(*args, **kwargs)
        return template("login.html",uporabnik=None,napaka="Potrebna je prijava!")
        
    return decorated



@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
@cookie_required
def index():
    oglasi = oglasS.dobi_nakljucne_oglase(10)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    if trenutni_uporabnik:
        trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik)
        return template('index.html', oglasi=oglasi,uporabnik=trenutni_uporabnik)
    else:
        return template('index.html', oglasi=oglasi,uporabnik=None)
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
    return template("register.html", napaka=None)

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
        return template("oglas.html", oglas=oglas,uporabnik=trenutni_uporabnik,napaka=None)
    else:
        return template("oglas.html",oglas=None,uporabnik=trenutni_uporabnik,napaka=None)

@post('/ad/<x:int>')
@cookie_required
def oglas_post(x):
    oglas = oglasS.dobi_oglas(x)
    sporocilo = request.forms.get('sporocilo')
    sporocilo = '{'+sporocilo+'}'
    prodajalec = authS.dobi_uporabnika(oglas.prodajalec)
    authS.poslji_sporocilo(prodajalec,sporocilo)
    trenutni_uporabnik = request.get_cookie("uporabnik",secret=auth.skrivnost)
    trenutni_uporabnik = authS.dobi_uporabnika(trenutni_uporabnik    )
    if sporocilo == '{}': #nekaj ne dela ker ne pokaze napake. Prvo prejeto sporocilo ni string (v bazi)?
        return template("oglas.html",oglas=oglas,uporabnik=trenutni_uporabnik,napaka="Sporočilo mora imeti vsebino.")
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
    kategorija = request.forms.get('kategorija')
    slika = request.forms.get('slika')
    oglas = oglasS.naredi_oglas(uporabnik,naslov,opis,cena,kategorija,slika)
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    return template("lasten_profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka="Oglas uspešno narejen!")  






conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#authS.dodaj_uporabnika('admin','admin','admin','admin','admin')
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)