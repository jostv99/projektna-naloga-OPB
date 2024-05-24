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
        
    def prijavi_uporabnika(self, uporabnik, geslo):
        user = self.repo.dobi_uporabnika(uporabnik)
        geslo_bytes = geslo.encode('utf-8')
        succ = bcrypt.checkpw(geslo_bytes, user.password_hash.encode('utf-8'))
        if succ:
            self.repo.posodobi_uporabnika(user)
            return uporabnik(username=user.username)
        return False

    def dodaj_uporabnika(self, uporabnik, geslo):
        bytes = geslo.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(bytes, salt)


        return uporabnik()