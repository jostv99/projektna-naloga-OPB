import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import auth as auth

from .models import Uporabnik, Kategorija, Oglas
from typing import List

class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ###################################################### OGLASI 
    
    def dobi_oglas(self,id):
        self.cur.execute("""
            SELECT * FROM oglasi WHERE id=%s
            """,(id,))
        o = Oglas.from_dict(self.cur.fetchone())
        return o
    
    def isci_oglase(self, opis):
        if opis == None:
            opis = '%'
        else:
            opis = '%' + opis + '%'
        self.cur.execute("""
            SELECT * FROM oglasi
            WHERE LOWER(naslov) LIKE LOWER(%s) OR LOWER(opis) LIKE LOWER(%s)
            ORDER BY naslov
            """,(opis ,opis,))
        oglasi = [Oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi        
    
    def dobi_nakljucne_oglase(self, num):
        self.cur.execute("""SELECT * FROM oglasi 
                         ORDER BY RANDOM() LIMIT %s
                         """, (num,))
        oglasi = [Oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi
    
    def dobi_zadnje_oglase(self, num):
        self.cur.execute("""SELECT * FROM oglasi
                         ORDER BY id DESC LIMIT %s
                         """, (num,))
        oglasi = [Oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi
        
    def dobi_oglase_uporabnika(self, u):
        self.cur.execute("""
            SELECT * FROM oglasi
            WHERE prodajalec=%s
            """,(u.uporabnisko_ime,))
        oglasi = [Oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi
    
    def naredi_oglas(self, o):
        self.cur.execute("SELECT setval('oglasi_id_seq', max(id)) FROM oglasi")
        self.cur.execute("""
            INSERT INTO oglasi
            (id, prodajalec, kategorija, opis, naslov, cena, slika)
            VALUES (DEFAULT, %s, %s, %s, %s, %s, %s)
            """,(o.prodajalec.uporabnisko_ime, o.kategorija, o.opis, o.naslov, o.cena, o.slika,))
        self.conn.commit()  
    
    def izbrisi_oglas(self, id):
        self.cur.execute("""
            DELETE FROM oglasi
            WHERE id=%s            
            """,(id,))
        self.conn.commit()
        
    def oglas_by_cat(self, cat):
        id = self.vrni_id(cat)
        self.cur.execute("""
            SELECT * FROM oglasi WHERE kategorija=%s
        """,(id,))
        oglasi = [Oglas.from_dict(t) for t in self.cur.fetchall()]
        return oglasi
    
    ###################################################### UPORABNIKI

    def dobi_uporabnika(self,username):
        self.cur.execute("""
            SELECT * FROM uporabniki WHERE uporabnisko_ime=%s
            """,(username,))
        u = Uporabnik.from_dict(self.cur.fetchone())
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

    def dobi_sporocila(self, u):
        self.cur.execute("""
            SELECT sporocila FROM uporabniki
            WHERE uporabnisko_ime=%s             
            """,(u.uporabnisko_ime,))
        s = self.cur.fetchone()
        return s
    
    def preberi_sporocilo(self, s, u):
        self.cur.execute("""
            SELECT sporocila FROM uporabniki WHERE uporabnisko_ime=%s             
        """,(u.uporabnisko_ime,))
        st = self.cur.fetchone()
        st = st[0]
        st = razgradi(st)
        for sporocilo in st:
            if sporocilo == s:
                sporocilo[3] = 'True'
        st = str(st)
        st = "{" + st[1:-1] + "}"
        st = st.replace('"\'',"")
        st = st.replace('\'"','')
        st = st.replace("'","")
        self.cur.execute("""
        UPDATE uporabniki SET sporocila = %s WHERE uporabnisko_ime=%s
        """,(st,u.uporabnisko_ime,))
        self.conn.commit()
    
    ###################################################### KATEGORIJE
    
    def vrni_opis(self,id):
        self.cur.execute("""
           SELECT opis FROM kategorije WHERE id=%s
           """,(id,))
        opis = Kategorija.from_dict(self.cur.fetchone())
        return opis[1]     
    
    def vrni_id(self,opis):
        self.cur.execute("""
           SELECT id FROM kategorije WHERE opis=%s
           """,(opis,))
        k = Kategorija.from_dict(self.cur.fetchone())
        print(id)
        return k.id
    
    def vrni_vse_kategorije(self):
        self.cur.execute("""
           SELECT * FROM kategorije
           ORDER BY opis
           """)
        kat = [Kategorija.from_dict(t) for t in self.cur.fetchall()]
        return kat   
        
        
        
##################### POMOZNE

def razgradi(seznam):
    print(seznam)
    chunk_size = 4
    result = []
    for i in range(0, len(seznam), chunk_size):
        chunk = seznam[i:i + chunk_size]
        chunk[0] = chunk[0].strip('[]')
        chunk[3] = chunk[3].strip('[]')
        result.append(chunk)
    return result
