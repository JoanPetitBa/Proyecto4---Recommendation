import os, sqlite3

def connectar_BDD():
    ruta_bd = f"{os.getcwd()}/db/market_place.db"
    try:
        connexio = sqlite3.connect(ruta_bd)
        cursor = connexio.cursor()
    except Exception as e:
        print(e)
    return connexio, cursor

def guardar_tancar_BDD(connexio):
    try:
        connexio.commit()
        connexio.close()
        return True
    except Exception as e:
        print(e)
        return False

connexio, cursor = connectar_BDD()
query = str(input("> "))
while query != "q":
    if query == "cls":
        os.system("cls")
    else:
        try:
            cursor.execute(query)
            for line in cursor.fetchall():
                print(' | '.join(str(value) for value in line))
        except Exception as e:
            print(e)
    query = str(input("> "))
guardar_tancar_BDD(connexio)
