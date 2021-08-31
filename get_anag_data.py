#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Script per la sincronizzazione giornaliera
dei dati delle anagrafiche contenute nella banca dati Garbage


il file viene normalmente generato a mezzanotte (12:00 AM)



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

from credenziali import *

# recupero il percorso allo script python 
spath=os.path.dirname(os.path.realpath(__file__)) 

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='w', # overwrite or append 
    filename='{}/log/get_anag.log'.format(spath),
    level=logging.INFO)


logging.info('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)



#session = FTP(ftp_host, ftp_user, ftp_pwd)
filename='{}/log/anag_data.csv'.format(spath) #, datetime.now().strftime("%Y%m%d_%H%M%S"))
try:
    with FTP(ftp_host, ftp_user, ftp_pwd) as ftp:
        #modtime = ftp.sendcmd('MDTM ' + anag_filename)
        #modtime2 = datetime.strptime(modtime[4:], "%Y%m%d%H%M%S").strftime("%Y%m%d_%H%M%S") #.strftime("%d %B %Y %H:%M:%S")
        logging.info('{}'.format(ftp.dir()))
        #filename='{}/log/anag_data_{}.csv'.format(spath, modtime2) 
        with open(filename, 'wb') as downloaded_file:
            ftp.retrbinary('RETR %s' % anag_filename, downloaded_file.write)
except:
    logging.error('Trasferimento non riuscito')
    logging.exception('')
    os._exit(1)
    
'''

Index(['CodiceUtenza', 'CodVia', 'Toponimo', 'Denominazione', 'datafine',
       'NumeroCivico', 'Lettera', 'Localita', 'TipoUtenza', 'Descrizione',
       'MQLocali', 'NumComponenti', 'cond', 'CodiceContribuente',
       'Denominazione1', 'Denominazione2'],
      dtype='object')
'''

#df = pd.read_csv(filename, sep=';', encoding='iso8859')
#df.head().to_csv('{}/log/test.csv'.format(spath), sep=';')


table_create_sql = ''' CREATE TABLE IF NOT EXISTS anagrafiche.anag_garbage (
                     id serial primary key,
                    'CodiceUtenza' varchar ,
                    'CodVia' varchar,
                    'Toponimo' varchar,
                    'Denominazione' varchar,
                    'datafine' timestamp without time zone,
                    'NumeroCivico' varchar,
                    'Lettera' varchar,
                    'Localita' varchar,
                    'TipoUtenza'varchar,
                    'Descrizione'varchar,
                    'MQLocali' integer, 
                    'NumComponenti' integer,
                    'cond' boolean,
                    'CodiceContribuente' varchar,
                    'Denominazione1' varchar,
                    'Denominazione2' varchar
                    )
                    '''

truncate_sql = '''TRUNCATE TABLE anagrafiche.anag_garbage'''

sql = ''' COPY anagrafiche.anag_garbage
          FROM {} 
          DELIMITER ';' CSV;
      '''.format(filename)



sql_list = [ table_create_sql, sql,  truncate_sql ]

logging.info('Connessione al db')
conn = psycopg2.connect(dbname=db,
                        port=port,
                        user=user,
                        password=pwd,
                        host=host)

cur = conn.cursor()
conn.autocommit = True


for sql in sql_list:
    logging.info(sql)
    try:
        cur.execute(sql)
    except:
        logging.error('Sql command fail')
        logging.exception('')
        os._exit(1)


logging.info('*'*20 + 'FINE ESECUZIONE' + '*'*20)  