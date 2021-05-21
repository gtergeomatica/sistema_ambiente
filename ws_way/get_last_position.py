#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Gter copyleft 2021
# Author: Roberto Marzocchi
# Script che interroga i WS di WAY srl per ottenere le posizioni dei mezzi






import os, sys, re  # ,shutil,glob
import numpy as np
import getopt  # per gestire gli input

#import pymssql

import psycopg2

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from credenziali import db, port, user, pwd, host


import requests

import logging

path=os.path.realpath(__file__).replace('get_last_position.py', '')
#tmpfolder=tempfile.gettempdir() # get the current temporary directory
logfile='{}/log/get_last_position.log'.format(path)
#if os.path.exists(logfile):
#    os.remove(logfile)

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', # overwrite or append
    filename=logfile,
    #level=logging.WARNING)
    level=logging.DEBUG)

import token_api as t

import xml.etree.ElementTree as et

from xml.etree.ElementTree import parse


def GetVehicleLastEvent(token):
    
    ''' Ottengo XML con la lista delle ultime posizioni dei veicoli di SistemaAmbiente
    unico input è il token che scade dopo un'ora di inattività'''

    url = t.url
    headers = {'Content-Type': 'text/xml'} # set what your server accepts
    body1="""
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:mob="Mobility.FleetManagementServices">
    <soap:Header/>
    <soap:Body>
    <mob:GetVehicleLastEvent>
    <mob:Input>
    <mob:TokenID>{}</mob:TokenID>
    <!-- <mob:Vehicle></mob:Vehicle>
        <mob:UpdateAfterDate></mob:UpdateAfterDate> :-->
    </mob:Input>
    </mob:GetVehicleLastEvent>
    </soap:Body>
    </soap:Envelope>""".format(token)
    r = requests.post(url, data=body1.encode(encoding='utf-8'), headers=headers)
    logging.debug("Info recieved...")
    logging.debug(r.content)
    ret= r.status_code
    if ret == 200: 
        logging.debug("Vehicle Last position obtained")
    logging.debug(r.content)
    root = et.fromstring(r.content)
    logging.debug(root)
    n_Vehicle=len(root[0][0][0][5].tag)
    i=0

    result_list = []
    for v in root[0][0][0][5]:
        #itero sui veicoli
        vdict = {}

        for c in v:
            #itero sui tag di ogni veicolo

            key = c.tag.split('}')[-1].strip().lower()
            if c.text != None:           
                value = c.text.strip().lower()
            else:
                value = None
            vdict[key] = value
        result_list.append(vdict)


    # la funzione restituisce una lista di dizionari
    # ogni dizionario corrisponde a un veicolo
    return  result_list





def GetVehicleHistoryEvents(token):

    ''' Ottengo XML con lalista dei veicoli di SistemaAmbiente
    unico input è il token che scade dopo un'ora di inattività'''


    

def main():
    # recupero il token 
    logging.debug('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)
    r= requests.get('{}/GetToken'.format(t.url), params={'serverName':t.servername, 'userName':t.username, 'password':t.password})
    logging.debug(r.status_code)
    logging.debug(r.url)
    root = et.fromstring(r.content)
    token=root.text
    print(token)
    
    
    logging.debug('GO!')
    try:
        risposta=GetVehicleLastEvent(token)
    except:
        logging.error('Richiesta GetVehicleLastEvent fallita ')
        logging.exception('')
        os._exit(1)


       # carico i mezzi sul DB PostgreSQL
    logging.info('Connessione al db')
    conn = psycopg2.connect(dbname=db,
                        port=port,
                        user=user,
                        password=pwd,
                        host=host)

    curr = conn.cursor()
    conn.autocommit = True
    
    n_mezzi= len(risposta) #326
    column_list = [i for i in risposta[0]]
    
    print(column_list)
    


    #create table query
    create_table_query = ''' CREATE TABLE IF NOT EXISTS ws_way.t_last_position (
                            id SERIAL PRIMARY KEY,
                            id_mezzo varchar,
                            nome varchar,
                            targa varchar,
                            brand varchar,
                            modello varchar)  '''

    
    try:
	    curr.execute(create_table_query)
	    conn.commit()
	    logging.info(''' Creata tabella dei mezzi''')
    except Exception as e:
	    logging.error(e)                            
    
    #insert table query
    #organizzo i dati per l'insert
    
    records_list_template = ','.join(['%s'] *n_mezzi )
    a = np.array([['ND' if i is None else i for i in risposta[0]],
                 ['ND' if i is None else i for i in risposta[1]],
                 ['ND' if i is None else i for i in risposta[2]],
                ['ND' if i is None else i for i in risposta[3]],
                ['ND' if i is None else i for i in risposta[4]]])    
    
    b = np.transpose(a)
    c = b.tolist()
    d = [tuple(i) for i in c]

    
    insert_query = '''INSERT INTO ws_way.t_mezzi (id_mezzo, nome,targa, brand, modello) values {}'''.format(records_list_template)

    #con la funzione mogrify metto in successione la query scritta prima con l'array
    query_insert2=curr.mogrify(insert_query, d).decode('utf8')

    # lancio la query dentro un try per segnalare eventuali errori
    try:
	    curr.execute(query_insert2)
	    conn.commit()
	    logging.info('''INSERT MEZZI CONCLUSO''')
    except Exception as e:
	    logging.error(e)



    logging.debug('*'*20 +'ESCO NORMALMENTE' + '*'*20 )

if __name__ == "__main__":
    main()