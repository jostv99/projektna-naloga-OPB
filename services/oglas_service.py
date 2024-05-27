from data.repository import Repo
from data.models import *
from typing import List
import bcrypt

class OglasService:
    repo : Repo

    def __init__(self) -> None:
        self.repo = Repo()


    def obstaja_oglas(self, id):
        try:
            o = self.repo.dobi_oglas(id)
            return True
        except:
            return False

    def dobi_oglas(self, id):
        return self.repo.dobi_oglas(id)

    def dobi_nakljucne_oglase(self, num):
        return self.repo.dobi_nakljucne_oglase(num)
    
    def naredi_oglas(self, prodajalec,naslov, opis, cena, kategorija,slika):
        
        o = Oglas(
            id = 0,
            prodajalec = prodajalec,
            kategorija = kategorija,
            opis = opis,                        
            naslov = naslov,
            cena = float(cena),
            slika = slika            
        )
        
        self.repo.naredi_oglas(o)
        return o
        