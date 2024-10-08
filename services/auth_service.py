from data.repository import Repo
from data.models import *
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
        
    def dobi_uporabnika(self, u):
        return self.repo.dobi_uporabnika(u)
        
    def prijavi_uporabnika(self, u, geslo):
        user = self.repo.dobi_uporabnika(u)
        geslo_bytes = geslo.encode('utf-8')
        succ = bcrypt.checkpw(geslo_bytes, user.geslo.encode('utf-8'))
        if succ:
            return user
        return False

    def dodaj_uporabnika(self, uporabnisko_ime, geslo, email, telefon, kraj_bivanja):
        bytes = geslo.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(bytes, salt)  

        u = Uporabnik(
                uporabnisko_ime = uporabnisko_ime,
                geslo = password_hash.decode(),                
                email = email,
                kredibilnost = 0,
                telefon = telefon,
                kraj_bivanja = kraj_bivanja,
                sporocila = '{}'

        )

        self.repo.dodaj_uporabnika(u)
        return u
    
    def posodobi_uporabnika(self, uporabnisko_ime, novo_uporabnisko_ime, novo_geslo, email, telefon, kraj_bivanja, kredibilnost, sporocila):
        bytes = novo_geslo.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(bytes, salt)
        print(password_hash.decode())
        
        self.repo.posodobi_uporabnika(uporabnisko_ime, novo_uporabnisko_ime, password_hash.decode(), email, telefon, kraj_bivanja, kredibilnost, sporocila)
        
    def poslji_sporocilo(self, u, sporocilo):
        self.repo.poslji_sporocilo(u,sporocilo)

    def dobi_oglase_uporabnika(self, u):
        return self.repo.dobi_oglase_uporabnika(u)
    
    def dobi_sporocila(self, u):
        return self.repo.dobi_sporocila(u)
    
    def preberi_sporocilo(self, s, u):
        return self.repo.preberi_sporocilo(s, u)
    
    def preveri_telefon(self, t):
        return self.repo.preveri_telefon(t)
    
    def preveri_email(self, e):
        return self.repo.preveri_email(e)
    
    def izbrisi_uporabnika(self, username):
        return self.repo.izbrisi_uporabnika(username)