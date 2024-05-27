from data.repository import Repo
from data.models import *
from typing import List
import bcrypt

class KategorijaService:
    repo : Repo
    def __init__(self) :
        self.repo= Repo()
    
    def vrni_opis(self, id):
        return self.repo.vrni_opis(id)
    
    def vrni_id(self, opis):
        return self.repo.vrni_id(opis)
    
    def vrni_vse_kategorije(self):
        return self.repo.vrni_vse_kategorije()
    
    