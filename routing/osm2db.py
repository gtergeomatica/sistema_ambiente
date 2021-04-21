import requests
import json
import os
from conn import *
import logging
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='log/download_OSM.log',   #mancano permessi
    level=logging.INFO)

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)

logging.info('osm 2 pgrouting')

p = """osm2pgrouting -f {0} -h {1} -U {2} -d {3} -p {4} -W {5}  --schema {6} --conf={7}""".format(osm_file,
                                                                                                  host,
                                                                                                  user,
                                                                                                  dbname,
                                                                                                  port,
                                                                                                  password,
                                                                                                  schema,
                                                                                                  conf)
try:  
    os.system(p)
except:
    loggin.error('Import fallito')
    logging.exception('')
    os._exit(1)


logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 