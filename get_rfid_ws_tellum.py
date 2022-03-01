import logging
import os
from datetime import datetime, timedelta
import json
import token
import requests
import psycopg2
import logging
import pandas as pd
import pathlib
from io import BytesIO
from sqlalchemy import create_engine, text
from credenziali import *
from subprocess import *
import shlex
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

headersDeafuult = {
    'Cookie': 'ARRAffinity=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3; ARRAffinitySameSite=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3'
    }

def requestHandling(type ,url, payloadT={}, headersT = headersDeafuult):
    """
    Per non scrivere troppo (ctr c/ctrl v) scrivo una funzione che fa le chiamate e restiuisce la risposta via testo,
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
    url = f"https://www.satfinder.it/services/extern/authentication?username={usernameTellus}&password={passwordTellus}"

    responseFull = requestHandling("GET", url)
    token = responseFull['token']

    return token


def getFleetId(token):
    """ 
    get fleet or groups 4.1.2 di SATfinderService_Interfacciamento.pdf
    """
    url = f"https://www.satfinder.it/services/extern/groups?token={token}"
    responseFull = requestHandling("GET", url)
    
    return responseFull[0]['fleets'][0]['id']


def getDispositivi(id, token):
    """
    Richiesta Elenco Dispositivi disponibili 4.2.1
    """
    url = f"https://www.satfinder.it/services/extern/devices?token={token}"
    
    payload = json.dumps([id])
    headers= {
    'Content-Type': 'application/json',
    'Cookie': 'ARRAffinity=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3; ARRAffinitySameSite=922e9738a217d969207539a314a23be570278def2f467b4687460ebde8af52e3'
    }

    responseFull = requestHandling("POST", url,  payload, headers)

    #salviamo lista dispositivi ottenuti dalla chiamata
    listaIdDispositivi = [ el["id"] for el in responseFull ]
    
    return listaIdDispositivi

def getEventoInteressante(token, listaDispo):
    """
    4.2.3 Informazioni di dettaglio sul dispositivo
    Nello specifico, per ogni dispositivo restituito nella chiamata 4.2.1, otterrete l’elenco di eventi 
    presenti nell’arco temporale richiesto, tra questi l’evento 296 è quello che riguarda le letture.
    """
    url = f"https://www.satfinder.it/services/extern/devicedata?token={token}&deviceId=7572&dateStart=2022-02-28T00:00:00&dateEnd=2022-02-28T23:00:00"

    responseFull = requestHandling("GET", url)
    print( responseFull["events"][4])

def main():

    initLogger()
    tokenTellus = getToken()
    fleetId = getFleetId(tokenTellus)
    listaIdDispositivi = getDispositivi(fleetId, tokenTellus)
    
    getEventoInteressante(tokenTellus, listaIdDispositivi)
    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    
    main()