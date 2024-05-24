import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import auth as auth

from models import uporabnik, kategorija, oglas
from typing import List

class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_oglas(self,id):
        self.cur.execute("""
            SELECT * FROM oglasi WHERE id=%s
            """,(id,))
        
    def dobi_uporabnika(self,id):
        self.cur.execute("""
            SELECt * FROM uporabniki WHERE id=%s
            """,(id,))
        
    def dodaj_uporabnika(self, ime, priimek, email, uporabnisko_ime, telefon, geslo, kraj_bivanja):
        self.cur.execute("""
            INSERT INTO uporabniki
            (id, ime, priimek, email, kredibilnost, uporabnisko_ime, telefon, geslo, kraj_bivanja, sporocila)
            VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, NULL)
            """,(ime, priimek, email, uporabnisko_ime, telefon, geslo, kraj_bivanja,))