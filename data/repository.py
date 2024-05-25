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
            INSERT INTO uporabniki
            (uporabnisko_ime, geslo, email, kredibilnost, telefon, kraj_bivanja, sporocila)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,(u.uporabnisko_ime, u.geslo, u.email, u.kredibilnost, u.telefon, u.kraj_bivanja, u.sporocila,))
        self.conn.commit()

    def poslji_sporocilo(self, u, sp):
        self.cur.execute("""
            UPDATE uporabniki
            SET sporocila=(sporocila || %s)
            WHERE uporabnisko_ime=%s
            """,(sp,u.uporabnisko_ime,))
        self.conn.commit()

    def dobi_oglase_uporabnika(self, u):
        self.cur.execute("""
            SELECT * FROM oglasi
            WHERE prodajalec=%s
            """,(u.uporabnisko_ime,))
        oglasi = [oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi