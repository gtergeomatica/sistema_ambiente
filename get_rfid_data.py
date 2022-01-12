#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Script per la sincronizzazione giornaliera
dei dati dei tag rfid dei cestini


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
    #filename='{}/log/get_rfid.log'.format(spath),
    level=logging.INFO)

logging.info('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)

filename='{}/log/rfid_data.csv'.format(spath) #, datetime.now().strftime("%Y%m%d_%H%M%S"))

try:
    with FTP(ftp_host_g, ftp_user_g_01, ftp_pwd_g_01) as ftp:
        logging.info('{}'.format(ftp.dir()))
        #with open(filename, 'wb') as downloaded_file:
            #ftp.retrbinary('RETR %s' % anag_filename, downloaded_file.write)
except:
    logging.error('Trasferimento non riuscito')
    logging.exception('')
    os._exit(1)




logging.info('*'*20 + 'FINE ESECUZIONE' + '*'*20)  