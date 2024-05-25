import auth

import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import csv


def ustvari_tabelo_uporabniki():
    cur.execute("""
        CREATE TABLE uporabniki (
            uporabnisko_ime TEXT PRIMARY KEY,
            geslo TEXT NOT NULL,                           
            email TEXT NOT NULL,                
            kredibilnost FLOAT(24) NOT NULL,
            telefon TEXT,
            kraj_bivanja TEXT,
            sporocila TEXT[]
        );
    """)
    conn.commit()
    print("Tabela z uporabniki uspešno narejena!")

def ustvari_tabelo_kategorije():
    cur.execute("""
        CREATE TABLE kategorije (
            id SERIAL PRIMARY KEY,
            opis TEXT
        )
    """)
    conn.commit()
    print("Tabela s kategorijami uspešno narejena!")

def ustvari_tabelo_oglasi():
    cur.execute("""
        CREATE TABLE oglasi (
            id SERIAL PRIMARY KEY,
            prodajalec TEXT REFERENCES uporabniki(uporabnisko_ime),
            kategorija INTEGER REFERENCES kategorije(id),
            opis TEXT,
            naslov TEXT NOT NULL,
            cena FLOAT(24) NOT NULL,
            slika TEXT
        )
    """)
    conn.commit()
    print("Tabela z oglasi uspešno narejena!")

def pobrisi_tabelo(ime_tabele):
    cur.execute(f"""
        DROP TABLE {ime_tabele};
    """)
    conn.commit()

def uvozi_podatke(podatki):
    with open(f"{podatki}.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd)

        if podatki == 'kategorije':
            for r in rd:
                r = [None if x in ('', '-') else x for x in r]
                cur.execute("""
                    INSERT INTO kategorije
                    (id, opis)
                    VALUES (%s, %s)
                    RETURNING id
                """, r)
            print("Kategorije uspešno naložene!")

        elif podatki == 'uporabniki':
            for r in rd:
                r = [None if x in ('', '-') else x for x in r]
                cur.execute("""
                    INSERT INTO uporabniki
                    (uporabnisko_ime, geslo, email, kredibilnost, telefon, kraj_bivanja, sporocila)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING uporabnisko_ime
                """, r)
            print("Podatki uporabnikov uspešno naloženi!")
            
        elif podatki == 'oglasi':
            for r in rd:
                r = [None if x in ('', '-') else x for x in r]
                cur.execute("""
                    INSERT INTO oglasi
                    (id, prodajalec, kategorija, opis, naslov, cena, slika)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, r)
            print("Oglasi uspešno naloženi!")

        else:
            print('Napačni podatki pri uvozu')



    conn.commit()





conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


pobrisi_tabelo('oglasi')
pobrisi_tabelo('uporabniki')
pobrisi_tabelo('kategorije')

ustvari_tabelo_uporabniki()
ustvari_tabelo_kategorije()
ustvari_tabelo_oglasi()
print("Tabele uspešno narejene.")

uvozi_podatke('uporabniki')
uvozi_podatke('kategorije')
uvozi_podatke('oglasi')
print("Podatki uspešno naloženi v tabele.")