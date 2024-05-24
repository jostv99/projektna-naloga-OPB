from functools import wraps
from presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

import os, psycopg2, psycopg2.extensions, psycopg2.extras, hashlib
from services.auth_service import AuthService
from services.oglas_service import OglasService

import auth as auth

#popravi bazo, da je up_ime enolicno

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

authS = AuthService()
oglasiS = OglasService()


def cookie_required(f):
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("login.html",uporabnik=None, rola=None, napaka="Potrebna je prijava!")
        
    return decorated



@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
@cookie_required
def index():
    oglasi = oglasiS.dobi_nakljucne_oglase(10)
    return template('index.html', oglasi=oglasi)

@post('/login')
def login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not authS.obstaja_uporabnik(username):
        return template("login.html", napaka="Uporabnik s tem imenom ne obstaja")

    prijava = authS.prijavi_uporabnika(username, password)
    if prijava:
        response.set_cookie("uporabnik", username)
        redirect(url('/'))
        
    else:
        return template("login.html", uporabnik=None, napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#authS.dodaj_uporabnika('admin','admin','admin','admin','admin','admin','admin')
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)