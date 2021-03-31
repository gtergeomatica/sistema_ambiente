#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Script per il refresh giornaliero della
vista materializzata percorsi.mv_contatori_utenze
del db - sis_ambiente

'''
import os
import sys
import shutil
import re
import glob
import getopt
import datetime
import psycopg2
import logging

from credenziali import *

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='def.log',
    level=logging.INFO)


logging.info('*'*20 + 'NUOVA ESECUZIONE' + '*'*20)
logging.info('COnnessione al db')
conn = psycopg2.connect(dbname=db,
                        port=port,
                        user=user,
                        password=pwd,
                        host=host)

curr = conn.cursor()
conn.autocommit = True



sql_list = ['''REINDEX INDEX percorsi.t_giri_geom_idx;''',
            #--DROP  INDEX IF EXISTS percorsi.t_giri_geom_idx;
            #--CREATE INDEX ON percorsi.t_giri USING gist (geom);
            '''VACUUM ANALYZE percorsi.t_giri;''',
        
            '''REINDEX INDEX civici.t_civici_geom_idx ;''',
            #--DROP  INDEX IF EXISTS t_civici_geom_idx;
            #--CREATE INDEX ON civici.t_civici USING gist (geom);
            '''VACUUM ANALYZE civici.t_civici;''',
        
            #-- index on mv is necessary to refresh view CONCURRENTLY
            '''REINDEX INDEX percorsi.mv_contatori_utenze_id_idx;''',
            #--DROP  INDEX IF EXISTS percorsi.mv_contatori_utenze_id_idx;
            #--CREATE UNIQUE INDEX ON percorsi.mv_contatori_utenze (id);
            '''VACUUM ANALYZE percorsi.mv_contatori_utenze; ''',

           '''REFRESH MATERIALIZED VIEW CONCURRENTLY percorsi.mv_contatori_utenze;''']

for sql in sql_list:
    logging.info(sql)
    try:
        curr.execute(sql)
    except:
        logging.error('Sql command fail')
        logging.exception('')
        os._exit(1)

logging.info('*'*20 + 'FINE ESECUZIONE' + '*'*20)  