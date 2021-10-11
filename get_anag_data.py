#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Script per la sincronizzazione giornaliera
dei dati delle anagrafiche2 contenute nella banca dati Garbage


il file  di Garbage viene normalmente generato a mezzanotte (12:00 AM)



'''
from ftplib import FTP
import os
import sys
import shutil
import re
import glob
import getopt
from datetime import datetime
import psycopg2
import logging
import pandas as pd
from sqlalchemy import create_engine
from credenziali import *

# recupero il percorso allo script python 
spath=os.path.dirname(os.path.realpath(__file__)) 

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='w', # overwrite or append 
    filename='{}/log/get_anag.log'.format(spath),
    level=logging.INFO)


logging.info('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)

filename='{}/log/anag_data.csv'.format(spath) #, datetime.now().strftime("%Y%m%d_%H%M%S"))
try:
    with FTP(ftp_host, ftp_user, ftp_pwd) as ftp:
        #logging.info('{}'.format(ftp.dir()))
        with open(filename, 'wb') as downloaded_file:
            ftp.retrbinary('RETR %s' % anag_filename, downloaded_file.write)
except:
    logging.error('Trasferimento non riuscito')
    logging.exception('')
    os._exit(1)
    


table_create_sql = ''' CREATE TABLE IF NOT EXISTS anagrafiche2.anag_garbage (
                     --id serial primary key,
                    "CodiceUtenza" varchar primary key,
                    "CodVia" varchar,
                    "Toponimo" varchar,
                    "Denominazione" varchar,
                    "datafine" timestamp without time zone,
                    "NumeroCivico" varchar,
                    "Lettera" varchar,
                    "Localita" varchar,
                    "TipoUtenza" varchar,
                    "RESIDENTE" varchar,
                    "Descrizione" varchar,
                    "MQLocali" integer, 
                    "NumComponenti" integer,
                    "cond" boolean,
                    "CodiceContribuente" varchar,
                    "Denominazione1" varchar,
                    "Denominazione2" varchar,
                    "ServizioPannoloni" boolean
                    )
                    '''

truncate_sql = '''TRUNCATE TABLE anagrafiche2.anag_garbage'''

"""
 sql = '''COPY anagrafiche2.anag_garbage
          FROM STDIN
          DELIMITER ';' 
          CSV HEADER
          QUOTE "'"
          ENCODING 'LATIN1'; 
      ''' 
"""


sql_list = [ table_create_sql,  truncate_sql ]

logging.info('Connessione al db')
conn = psycopg2.connect(dbname=db,
                        port=port,
                        user=user,
                        password=pwd,
                        host=host)

cur = conn.cursor()
conn.autocommit = True



for s in sql_list:

    logging.info(s)

    if s.startswith('COPY'):

        try:
            cur.copy_expert(s, open(filename, "r", encoding="latin_1"))
        except:
            logging.error('Sql COPY command fail')
            logging.exception('')
            os._exit(1)           

    else:

        try:
            cur.execute(s)
        except:
            logging.error('Sql command fail')
            logging.exception('')
            os._exit(1)


conn_string = 'postgres://{}:{}@{}/{}'.format(user, pwd, host, db )
engine = create_engine(conn_string)
connection = engine.connect()

df = pd.read_csv(filename, sep=';', encoding='iso8859', 
                 dtype={'cond' : bool, 'ServizioPannoloni':bool,
                       'CodVia': str,  'NumeroCivico':str},
                 true_values=['SI'], false_values=['NO'])
#df.head().to_csv('{}/log/anag_garbage_sample.csv'.format(spath), sep=';')

try:
    df.to_sql('anag_garbage', con=connection, schema='anagrafiche2', if_exists='append', index=False)
except:
    logging.error('Sql command fail')
    logging.exception('')
    os._exit(1)


logging.info('*'*20 + 'FINE ESECUZIONE' + '*'*20)  