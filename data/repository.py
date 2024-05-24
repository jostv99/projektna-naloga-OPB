import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import auth as auth

from .models import uporabnik, kategorija, oglas
from typing import List

class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_oglas(self,id):
        self.cur.execute("""
            SELECT * FROM oglasi WHERE id=%s
            """,(id,))
        o = oglas.from_dict(self.cur.fetchone())
        return o
    
    def dobi_nakljucne_oglase(self, num):
        self.cur.execute("""SELECT * FROM oglasi 
                         ORDER BY RANDOM() LIMIT %s
                         """, (num,))
        oglasi = [oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi

    def dobi_uporabnika(self,username):
        self.cur.execute("""
            SELECT * FROM uporabniki WHERE uporabnisko_ime=%s
            """,(username,))
        u = uporabnik.from_dict(self.cur.fetchone())
        return u
        
    def dodaj_uporabnika(self, u):
        self.cur.execute("""
            SELECT setval('uporabniki_id_seq', max(id)) FROM uporabniki;
            INSERT INTO uporabniki
            (ime, priimek, email, kredibilnost, uporabnisko_ime, telefon, geslo, kraj_bivanja, sporocila)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,(u.ime, u.priimek, u.email, u.kredibilnost, u.uporabnisko_ime, u.telefon, u.geslo, u.kraj_bivanja, u.sporocila,))
        self.conn.commit()
    
