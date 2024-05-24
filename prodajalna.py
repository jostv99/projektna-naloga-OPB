
from bottleext import get, post, run, request, template, redirect, static_file, url

import os, psycopg2, psycopg2.extensions, psycopg2.extras, hashlib

import auth as auth


SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


secret = 'neka skrivnost 123'

## dodaj v bazo: sporocila,


def password_hash(s):
    h = hashlib.sha512()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
def index():
    cur.execute("SELECT * FROM oglasi ORDER BY RANDOM() LIMIT 10") #pocasno ampak uredu za zdaj
    return template('osnovna.html', oglasi=cur)

@get('/login')
def login_get():
    return template('login.html', napaka=None, username=None)

@post('/login')
def login_post():
    username = request.forms.username
    password = password_hash(request.forms.password)
    #dopolni

@get('/register')
def register_get():
    return template('register.html', napaka=None, username=None)

@get('/register')
def register_post():
    return None
    #dopolni

@get('/ad/<x:int>')
def oglas(x):
    cur.execute("SELECT * FROM oglasi WHERE id=%s",[x])
    #cur=(id, prodajalec, kategorija, opis, naslov, cena, slika)
    for i in cur:
        [id, prodajalec, kategorija, opis, naslov, cena, slika] = i
    return template('oglas.html',sporocilo='',prejemnik='',napaka=None,id=id,prodajalec=prodajalec,kategorija=kategorija,opis=opis,naslov=naslov,cena=cena,slika=slika)

@post('/ad/<x:int>')
def oglas_post(x):
    cur.execute("SELECT * FROM oglasi WHERE id=%s",[x])
    #cur=(id, prodajalec, kategorija, opis, naslov, cena, slika)
    for i in cur:
        [id, prodajalec, kategorija, opis, naslov, cena, slika] = i
    sporocilo = request.forms.sporocilo
    prejemnik = request.form.prodajalec
    sporocilo = '!new!' + sporocilo
    print(sporocilo)
    try:
        cur.execute("UPDATE uporabniki SET sporocila= (sporocila || %s) WHERE id=%s", [sporocilo,prejemnik])
        conn.commit()
    except Exception as ex:
        print("napaka")
        conn.rollback()
        return template('oglas.html',sporocilo='',prejemnik='',napaka='Zgodila se je napak',id=id,prodajalec=prodajalec,kategorija=kategorija,opis=opis,naslov=naslov,cena=cena,slika=slika)

@get('/user/<x:int>')
def user(x):
    cur.execute("SELECT * FROM uporabniki WHERE id=%s",[x])
    for i in cur:
        [id, ime, priimek, email, kredibilnost, uporabnisko_ime, telefon, geslo, kraj_bivanja,sporocila] = i
    return template('profil.html',id=id,ime=ime,priimek=priimek,email=email,kredibilnost=kredibilnost,telefon=telefon,kraj_bivanja=kraj_bivanja)


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)