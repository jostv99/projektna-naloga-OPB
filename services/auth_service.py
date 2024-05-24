from data.repository import Repo
from data.models import *
from typing import List
import bcrypt

class AuthService:
    repo : Repo
    def __init__(self) :
        self.repo= Repo()

    def obstaja_uporabnik(self, uporabnik):
        try:
            user = self.repo.dobi_uporabnika(uporabnik)
            return True
        except:
            return False
        
    def prijavi_uporabnika(self, u, geslo):
        user = self.repo.dobi_uporabnika(u)
        geslo_bytes = geslo.encode('utf-8')
        succ = bcrypt.checkpw(geslo_bytes, user.geslo.encode('utf-8'))
        if succ:
            return user
        return False

    def dodaj_uporabnika(self, ime, priimek, email, uporabnisko_ime, telefon, geslo, kraj_bivanja):
        bytes = geslo.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(bytes, salt)

        u = uporabnik(
                ime = ime,
                priimek = priimek,
                email = email,
                kredibilnost = 0,
                uporabnisko_ime = uporabnisko_ime,
                telefon = telefon,
                geslo = password_hash.decode(),
                kraj_bivanja = kraj_bivanja,
                sporocila = ''

        )

        self.repo.dodaj_uporabnika(u)
        return u