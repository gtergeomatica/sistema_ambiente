#!/usr/bin/env python

import requests
import json
import os
#from conn import *
import logging
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='log/download_OSM.log',   #mancano permessi
    level=logging.INFO)

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)


#definizione file di output
outdir = os.path.dirname(os.path.realpath(__file__))
osm_file = os.path.join(outdir,'dati_osm_lucca.osm')
logging.info(osm_file)


#query sul database OSM per estrazione del tag highway 
overpass_url = "http://overpass-api.de/api/interpreter"

#e="10.646374350606367" n="43.969977647278014" s="43.74798936510469" w="10.288957076844582
# order is s, w, n, e
overpass_query_old = """
[timeout:900][maxsize:1073741824][out:xml];
(node["highway"="*"](43.74798936510469, 10.288957076844582, 43.969977647278014,10.646374350606367);
way["highway"="*"](43.74798936510469, 10.288957076844582, 43.969977647278014,10.646374350606367);
rel["highway"="*"](43.74798936510469, 10.288957076844582, 43.969977647278014,10.646374350606367);
);
(._;>;);
out meta;
"""
overpass_query ='''
<osm-script output="xml" timeout="25">
    <union>
        <query type="node">
            <has-kv k="highway"/>
            <bbox-query e="10.646374350606367" n="43.969977647278014" s="43.74798936510469" w="10.288957076844582"/>
        </query>
        <query type="way">
            <has-kv k="highway"/>
            <bbox-query e="10.646374350606367" n="43.969977647278014" s="43.74798936510469" w="10.288957076844582"/>
        </query>
        <query type="relation">
            <has-kv k="highway"/>
            <bbox-query e="10.646374350606367" n="43.969977647278014" s="43.74798936510469" w="10.288957076844582"/>
        </query>
    </union>
    <union>
        <item/>
        <recurse type="down"/>
    </union>
    <print mode="body"/>
</osm-script>
'''


logging.info('Lancio query')
response = requests.get(overpass_url, params={'data': overpass_query})
                        
if response.ok:
    logging.info('Query eseguita con successo!')
else:
    logging.error('Query fallita!')
    logging.error(response)
    os._exit(1)

                        
logging.info('Recupero dati')
try:                      
    data = response.text
except:
    logging.error('Recupero dati fallito')
    os._exit(1)

    
#scrive il risultato della query su un file data.osm
logging.info('Scrivo file .osm')
with open(osm_file, "w") as file:
    file.write(data)
file.close()
'''
logging.info('osm 2 pgrouting')
#Import in Postgres del file data.osm
p = """osm2pgrouting -f {0} -h {1} -U {2} -d {3} -p {4} -W {5}  --schema {6} --conf={7}""".format(osm_file,
                                                                                                  host,
                                                                                                  user,
                                                                                                  dbname,
                                                                                                  port,
                                                                                                  password,
                                                                                                  schema,
                                                                                                  conf)
 #"""osm2pgrouting -f data.osm -h localhost -U postgres -d city_routing -p 5432 -W postgresnpwd  --schema network --conf=/usr/share/osm2pgrouting/mapconfig_rail.xml"""
  
os.system(p)
'''


logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 