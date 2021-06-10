#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Gter copyleft 2021
# Author: Roberto Marzocchi - Rossella Ambrosino
# Script che interroga i WS di WAY srl per ottenere le posizioni dei mezzi
# lo script è a crontab (vedi file con credeziali)







import os, sys, re  # ,shutil,glob
import numpy as np
import getopt  # per gestire gli input
import psycopg2
import requests
import token_api as t
import xml.etree.ElementTree as et
from xml.etree.ElementTree import parse

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from credenziali import db, port, user, pwd, host

import logging
path=os.path.realpath(__file__).replace('get_vehicle_list.py', '')
#tmpfolder=tempfile.gettempdir() # get the current temporary directory
logfile='{}/log/get_vehicle_list.log'.format(path)
#if os.path.exists(logfile):
#    os.remove(logfile)

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', # overwrite or append
    filename=logfile,
    level=logging.INFO)
    #level=logging.DEBUG)




def GetVehicleList(token):
    
    ''' Ottengo XML con la lista delle ultime posizioni dei veicoli di SistemaAmbiente
    unico input è il token che scade dopo un'ora di inattività'''

    url = t.url
    headers = {'Content-Type': 'text/xml'} # set what your server accepts
    body1="""
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:mob="Mobility.FleetManagementServices">
        <soap:Header/>
        <soap:Body>
        <mob:GetVehicleList>
        <mob:Input>
        <mob:TokenID>{0}</mob:TokenID>
        <!-- <mob:Vehicle></mob:Vehicle>
        <mob:UpdateAfterDate></mob:UpdateAfterDate> :-->
        </mob:Input>
        </mob:GetVehicleList>
        </soap:Body>
        </soap:Envelope>""".format(token)

    r = requests.post(url, data=body1.encode(encoding='utf-8'), headers=headers)
    logging.debug("Info recieved...")
    #logging.debug(r.content)
    ret= r.status_code
    if ret == 200: 
        logging.debug("Vehicle Last position obtained")
    
    root = et.fromstring(r.content)

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
    logging.info('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)
    r= requests.get('{}/GetToken'.format(t.url), params={'serverName':t.servername,
                                                         'userName':t.username, 
                                                         'password':t.password})
    logging.debug(r.status_code)
    logging.debug(r.url)
    root = et.fromstring(r.content)
    token=root.text
    logging.debug(token)
    
    
    logging.debug('GO!')
    try:
        risposta=GetVehicleList(token)
    except:
        logging.error('Richiesta GetVehicleList fallita ')
        logging.exception('')
        os._exit(1)


    # carico la risposta sul DB PostgreSQL
    logging.info('Connessione al db')
    try:
        conn = psycopg2.connect(dbname=db,
                        port=port,
                        user=user,
                        password=pwd,
                        host=host)
    except:
        logging.error('connessione al db fallita ')
        logging.exception('')
        os._exit(1)   
    
    
    curr = conn.cursor()
    conn.autocommit = True
    

    
    #create table query
    create_table_query =  '''CREATE TABLE IF NOT EXISTS ws_way.t_mezzi (
                            id_row SERIAL PRIMARY KEY,
                            date_ins timestamp DEFAULT NOW(),
                            id varchar,
                            customid varchar,
                            fleetname varchar,
                            idfleet varchar, 
                            name varchar UNIQUE,
                            plate varchar, 
                            chassisnumber varchar,
                            brand varchar,
                            model varchar , 
                            symbol varchar,
                            note varchar, 
                            driverid varchar,
                            drivercustomid varchar,
                            driverfullname varchar,
                            missionname varchar,
                            idmission varchar,
                            trucKname varchar,
                            trailername varchar,
                            sealcode varchar ,
                            barcode numeric ,
                            appversion varchar,
                            activationcode varchar,
                            codehw varchar,
                            owner varchar)  '''

    
    try:
	    curr.execute(create_table_query)
	    conn.commit()
	    logging.debug(''' Verificata presenza tabella lista veicoli''')
    except Exception as e:
	    logging.error(e)
                         
    
    #insert table query
    #organizzo i dati per l'insert
    n_mezzi= len(risposta) #326
    column_list = [i for i in risposta[0]]
    #column_type = {i: type(i) for i in risposta[0]} 
    #inutile: in lettura del ws tutti i valori sono stringhe

     
    records_list_template = ', '.join(['%s'] *n_mezzi )
    column_list_template = ', '.join(column_list )

    #scrivo le liste di valori da inserire secondo l'ordine definito in column_lisr
    rowstoinsert = [tuple([i[c] for c in column_list ]) for i in risposta]

    #in caso di id già presente non viene effettuato nessun insert
    insert_query = '''INSERT INTO ws_way.t_mezzi ({})
                   values {} 
                   ON CONFLICT (name) DO UPDATE
                   SET customid = EXCLUDED.customid ,
                            id = EXCLUDED.id,
                            fleetname = EXCLUDED.fleetname ,
                            idfleet = EXCLUDED.idfleet , 
                            plate = EXCLUDED.plate , 
                            chassisnumber = EXCLUDED.chassisnumber ,
                            brand = EXCLUDED.brand ,
                            model = EXCLUDED.model  , 
                            symbol = EXCLUDED.symbol ,
                            note = EXCLUDED.note , 
                            driverid = EXCLUDED.driverid ,
                            drivercustomid = EXCLUDED.drivercustomid ,
                            driverfullname = EXCLUDED.driverfullname,
                            missionname = EXCLUDED.missionname,
                            idmission = EXCLUDED.idmission,
                            trucKname = EXCLUDED.trucKname,
                            trailername = EXCLUDED.trailername,
                            sealcode = EXCLUDED.sealcode,
                            barcode = EXCLUDED.barcode ,
                            appversion = EXCLUDED.appversion,
                            activationcode = EXCLUDED.activationcode,
                            codehw = EXCLUDED.codehw,
                            owner = EXCLUDED.owner 
                    ;'''.format(column_list_template,
                                records_list_template)

    logging.debug(insert_query)
    #con la funzione mogrify metto in successione la query scritta prima con l'array
    query_insert2=curr.mogrify(insert_query, rowstoinsert ).decode('utf8')
    
    # lancio la query dentro un try per segnalare eventuali errori
    try:
	    curr.execute(query_insert2)
	    conn.commit()
	    logging.info('''Insert concluso con successo''')
    except Exception as e:
        logging.error('Insert fallito {}'.format(insert_query))
        logging.error(e)
        os._exit(1)


    logging.info('*'*20 +'ESCO NORMALMENTE' + '*'*20 )

if __name__ == "__main__":
    main()