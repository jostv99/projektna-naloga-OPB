from data.repository import Repo
from data.models import *
from typing import List
import bcrypt

class OglasService:
    def __init__(self) -> None:
        self.repo = Repo()


    def dobi_oglas(self, id):
        return self.repo.dobi_oglas(id)

    def dobi_nakljucne_oglase(self, num):
        return self.repo.dobi_nakljucne_oglase(num)