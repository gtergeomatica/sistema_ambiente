#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime, timedelta
import dateutil.parser
import json
from typing_extensions import runtime
import requests
import psycopg2
import logging
from sqlalchemy import create_engine, text
from credenziali import *
import pandas as pd


def initLogger():
    """
    define log file as simple as possibile
    """

    spath = os.path.dirname(os.path.realpath(__file__))

    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        filemode="a",  # overwrite or append
        filename=f"{spath}/log/get_rfid_ws_tellum.log",
        level=logging.INFO,
    )
    logging.info("*" * 20 + "NUOVA ESECUZIONE" + "*" * 20)


def initDbConnection():
    """
    set up for the connection
    """
    try: 
        logging.info("Connessione al db")
        conn = psycopg2.connect(dbname=db, port=port, user=user, password=pwd, host=host)

        cur = conn.cursor()
        conn.autocommit = True

        return cur, conn

    except:
        logging.error("Connessione al DB non riuscita")
        logging.exception("")
        os._exit(1)


def executeSqlQuery(cur):
    """
    it executes the queries, only one right now
    """
    tableCreateSql = """ CREATE TABLE IF NOT EXISTS cestini.bracciali (
                     id serial primary key,
                    "cod_cestino" varchar ,
                    "cod_bracciale" varchar,
                    "x" DOUBLE PRECISION,
                    "y" DOUBLE PRECISION,
                    "data" varchar,
                    "orario" varchar,
                    "indirizzo" varchar
                    )
                    """
    sqlQueryList = [tableCreateSql]

    for idx, s in enumerate(sqlQueryList):
        try:
            cur.execute(s)
            logging.info(f"esecuzione query nr {idx+1} di sqlQuery")
        except:
            logging.error("Sql command fail on executeSqlQuery function")
            logging.exception("")
            os._exit(1)


def quitConncetion(cur, conn):
    """
    close connection with db
    """

    if (cur is not None) or (conn is not None):
        cur.close()
        conn.close()
        logging.info(f"chiusura connessioni al db")


# headers usato di default nelle chiamate
headersDeafuult = {
    'Cookie': 'ARRAffinity=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3; ARRAffinitySameSite=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3'
    }


def requestHandling(type ,url, payloadT={}, headersT = headersDeafuult):
    """
    Per non scrivere troppo scrivo una funzione che fa le chiamate e restiuisce la risposta via testo,
    se per ragioni di performance non andasse bene faccio un altra maniera
    """
    
    try:
        response = requests.request(type, url, headers=headersT, data=payloadT)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error(errh)
        logging.exception("")
    except requests.exceptions.ConnectionError as errc:
        logging.error(errc)
        logging.exception("")
    except requests.exceptions.Timeout as errt:
        logging.error(errt)
        logging.exception("")
    except requests.exceptions.RequestException as err:
        logging.error(err)
        logging.exception("")


def getToken():
    """
    get token from api 4.1.1 di SATfinderService_Interfacciamento.pdf
    """
    url = f"{root}/authentication?username={usernameTellus}&password={passwordTellus}"

    responseFull = requestHandling("GET", url)
    token = responseFull['token']

    return token


def getFleetId(token):
    """ 
    get fleet or groups 4.1.2 di SATfinderService_Interfacciamento.pdf
    """
    url = f"{root}/groups?token={token}"
    responseFull = requestHandling("GET", url)
    
    return responseFull[0]['fleets'][0]['id']


def getDispositivi(id, token):
    """
    Richiesta Elenco Dispositivi disponibili 4.2.1, ritorna lista di liste con [id, description]
    """
    url = f"{root}/devices?token={token}"
    
    payload = json.dumps([id])
    headers= {
    'Content-Type': 'application/json',
    'Cookie': 'ARRAffinity=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3; ARRAffinitySameSite=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3'
    }

    responseFull = requestHandling("POST", url,  payload, headers)

    #salviamo lista dispositivi ottenuti dalla chiamata con lista di lista [[idX, descriptionX],[idY, descriptionY], ..]
    listaIdDispositivi = [ [el["id"], el["description"] ] for el in responseFull ]
    
    return listaIdDispositivi


def sendDataToDb(dictionary, cur):
    """
    send data to DB in the table cestini.bracciali create temporary table and upload DataFrame 
    and merge temp_table into main_table (cestini.bracciali) to upsert
    """
    
    for k in dictionary:
        # connString = 'postgres://{}:{}@{}/{}'.format(user, pwd, host, db )
        connString = f"postgres://{user}:{pwd}@{host}/{db}"
        engine = create_engine(connString)
        connection = engine.connect()
        
        try:
            # step 1 - create temporary table 
            connection.execute(
                text('''CREATE TEMPORARY TABLE temp_table (
                        --id serial primary key,
                        "cod_cestino" varchar ,
                        "cod_bracciale" varchar,
                        "x" DOUBLE PRECISION,
                        "y" DOUBLE PRECISION,
                        "data" varchar,
                        "orario" varchar,
                        "indirizzo" varchar);'''
                )
            )

            # step 2 - upload DataFrame
            # df.to_sql('bracciali', con=connection, schema='cestini', if_exists='append', index=False)
            dictionary[k].to_sql(
                "temp_table",
                con=connection,
                #schema="cestini",
                if_exists="append",
                index=False,
            )

            # step 3 - merge temp_table into cestini.bracciali

            connection.execute(
                text('''INSERT INTO cestini.bracciali (cod_cestino,
                                                cod_bracciale,
                                                x,
                                                y,
                                                data,
                                                orario,
                                                indirizzo) 
                        SELECT * FROM temp_table
                        ON CONFLICT ON CONSTRAINT bracciali_unique
                        DO NOTHING; '''
                )
            )

            logging.info(f"dati inseriti per {k}")

        except:
            logging.error("Sql command fail")
            logging.exception("")
            os._exit(1)


def getEventoInteressante(token, listaDispo):
    """
    4.2.3 Informazioni di dettaglio sul dispositivo
    Nello specifico, per ogni dispositivo restituito nella chiamata 4.2.1, otterrete l’elenco di eventi 
    presenti nell’arco temporale richiesto, tra questi l’evento 296 è quello che riguarda le letture.
    Richiamerà una funzione per scrivere direttamente nel DB
    """
    #per ogni deviceId contenuto in listaDispo[][0] e per la data e ora che ti interessano

    #momento esatto in cui gira lo script non che limite superiore della finestra temporale considerata
    dateEnd = datetime.now().replace(microsecond=0)

    #limite inferiore (tempo inizio) finestra temporale considerata, i.e 45 minuti --> se lo script gira ogni 30 min ci sono 15 min di overlap
    #margine di sicurezza
    dateStart = (dateEnd - timedelta(minutes = 35)).isoformat()
    
    logging.info(f"Script sta girando alle ore {dateEnd}, interroga i seguenti dispositivi {listaDispo} in finestra temporale a partire da {dateStart}")
    
    dicts = {}

    for dispositivo in listaDispo:

        url = f"{root}/devicedata?token={token}&deviceId={dispositivo[0]}&dateStart={dateStart}&dateEnd={dateEnd.isoformat()}"
        responseFull = requestHandling("GET", url)

        #empty list to be populated
        listToDf = []

        #della lista di eventi preventi cerchi il 296
        for evento in responseFull["events"]:
            
            if (evento['idEvent'] != 296) or (evento['idEvent'] is None):
                continue
            
            if evento['info'][0:4] != "SALC":
                continue

            #if evento['idEvent'] == 296:
            try:
                # parse della data e creazioni di due variabile che andranno a popolare la lista e in seguito andranno inserite nel DB
                timeStampCompleto = dateutil.parser.isoparse(evento['dateTime'])
                data = timeStampCompleto.strftime('%d/%m/%Y')
                orario = timeStampCompleto.strftime('%H:%M:%S')

                #lista da inserire nella tabella temp_table e poi in cestini.bracciali
                listTosend = [ 
                                evento['info'].split(";")[0], 
                                dispositivo[1], 
                                evento['xcoord'],
                                evento['ycoord'],
                                data,
                                orario,
                                evento['address'] if ("address" in evento) else None
                            ]
                
                listToDf.append(listTosend)

            except:
                logging.error(f"Impossibile scrivere la lista da inserire nel DB per {dispositivo} contiene{evento}")

        # creo Df
        dfToSend = pd.DataFrame(listToDf, columns = ["cod_cestino", "cod_bracciale", "x", "y", "data", "orario","indirizzo"]) 
        
        # popolo dict in cui chiave è id dispositivo e valore è il df
        dicts[dispositivo[0]] = dfToSend
        
    return dicts


def main():

    initLogger()

    #connect to DB and set uo
    cur, conn = initDbConnection()
    executeSqlQuery(cur)

    #interaction with TELLUS api
    tokenTellus = getToken()
    fleetId = getFleetId(tokenTellus)
    listaIdDispositivi = getDispositivi(fleetId, tokenTellus)
    dictToSend = getEventoInteressante(tokenTellus, listaIdDispositivi)

    sendDataToDb(dictToSend, cur)
    
    #quit connection with DB
    quitConncetion(cur, conn)

    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    main()