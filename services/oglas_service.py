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
        
    def izbrisi_oglas(self, id):
        return self.repo.izbrisi_oglas(id)
    
    def isci_oglase(self, opis):
        return self.repo.isci_oglase(opis)
    
    def oglas_by_cat(self, cat):
        return self.repo.oglas_by_cat(cat)
    
    def dobi_zadnje_oglase(self, n):
        return self.repo.dobi_zadnje_oglase(n)
    
    def posodobi_oglas(self, ad, naslov, opis, cena, kategorija, filename):
        return self.repo.posodobi_oglas(ad, naslov, opis, cena, kategorija, filename)