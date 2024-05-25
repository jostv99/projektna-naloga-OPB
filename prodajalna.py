from functools import wraps
from presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

import os, psycopg2, psycopg2.extensions, psycopg2.extras, hashlib
from services.auth_service import AuthService
from services.oglas_service import OglasService

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


def cookie_required(f):
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
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
    return template('index.html', oglasi=oglasi)

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
        response.set_cookie("uporabnik", username)
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
        return template("register.html", napaka="Prosimo vnesite podatke v vsa polja!")
    
    if authS.obstaja_uporabnik(username):
        return template("register.html", napaka="To uporabniško ime je že zasedeno, prosim izberite drugo.")

    #se pregledas ksne pogoje...

    uporabnik = authS.dodaj_uporabnika(username,password,email,'','')
    #popravi da samo vpise geslo, ki ni hash,
    return template("login.html", uporabnik=uporabnik, napaka=None)

@get('/ad/<x:int>')
def oglas(x):
    if oglasS.obstaja_oglas(x):
        oglas = oglasS.dobi_oglas(x)
        return template("oglas.html", oglas=oglas,napaka=None)
    else:
        return template("oglas.html",oglas=None,napaka=None)

@post('/ad/<x:int>')
def oglas_post(x):
    oglas = oglasS.dobi_oglas(x)
    sporocilo = request.forms.get('sporocilo')
    sporocilo = '{'+sporocilo+'}'
    if sporocilo == None: #nekaj ne dela ker ne pokaze napake. Prvo prejeto sporocilo ni string?
        return template("oglas.html",oglas=oglas,napaka="Sporočilo mora imeti vsebino.")
    prodajalec = authS.dobi_uporabnika(oglas.prodajalec)
    authS.poslji_sporocilo(prodajalec,sporocilo)

    return template("oglas.html",oglas=oglas,napaka="Sporočilo uspešno poslano!")

@get('/user/<username>')
def user(username):
    if not authS.obstaja_uporabnik(username):
        return template("profil.html",uporabnik=None,oglasi=None,napaka=None)
    uporabnik = authS.dobi_uporabnika(username)
    trenutni_uporabnik = request.get_cookie("username")
    if uporabnik == trenutni_uporabnik:
        return template("profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka="Uredi svoj profil")
    oglasi = authS.dobi_oglase_uporabnika(uporabnik)
    return template("profil.html",uporabnik=uporabnik,oglasi=oglasi,napaka=None)




conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#authS.dodaj_uporabnika('admin','admin','admin','admin','admin')
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)