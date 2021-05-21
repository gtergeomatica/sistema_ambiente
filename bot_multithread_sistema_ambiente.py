#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GTER copyleft 2021
# Roberto Marzocchi
# Lorenzo Benvenuto
# Rossella Ambrosino 
# 

# Componente lato server del BOT telegram per Sistema Ambiente SPA
#  


import os.path
from os import path
import asyncio

import sys, time
# da togliere
import random

import emoji
import telepot
#import url_shortener #, short_url

#python 3
from telepot.aio.loop import MessageLoop
#from telepot.aio.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open, per_callback_query_origin
#python2 
#from telepot.loop import MessageLoop
#questo per i tastini
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
#from telepot.delegate import pave_event_space, per_chat_id, create_open


from pprint import pprint
import time
import datetime
import json

import logging
import tempfile

path=os.path.realpath(__file__).replace('bot_multithread_sistema_ambiente.py','')
#tmpfolder=tempfile.gettempdir() # get the current temporary directory
logfile='{}/log/bot_telegram_sistema_ambiente.log'.format(path)
#if os.path.exists(logfile):
#    os.remove(logfile)

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', # overwrite or append
    filename=logfile,
    level=logging.WARNING)
    #level=logging.DEBUG)




try:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
except:
    # For Python 3.0 and later
    from urllib.request import urlopen
    import urllib.parse

import psycopg2
import credenziali as p



# Il token è contenuto nel file vredenziali.py e non è aggiornato su GitHub per evitare utilizzi impropri
TOKEN=p.bot_token
link=p.link
note_link=p.note_link

check=0
testo_segnalazione=''
testo_segnalazione20=''
alllegato=''
chat_id=''
id_mira=''



def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")






def lista_percorsi(colore):
    #conn = psycopg2.connect(host=ip, dbname=db, user=user, password=pwd, port=port) 
    # ora mi connetto al DB
    conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    query='''select g.giro, m.descrizione from percorsi.v_giri g 
        left join deco.giri_mezzo m on m.id=g.mezzo  
        where zona='{}' order by length(giro), giro;'''.format(colore)
    try:
        cur.execute(query)
        stazioni=cur.fetchall()
    except Exception as e:
        logging.error(e)

    logging.debug(query)
    #logging.debug(stazioni)

    #messaggio= "\033[1m"+'CONTROLLO OPERATIVITA\' STAZIONI GNSS\n\n'+"\033[0m"
    messaggio= '{} Clicca sul bottone per visualizzare il giro su mappa'.format(emoji.emojize(" :backhand_index_pointing_down:)", use_aliases=True), emoji.emojize(" :world_map:)", use_aliases=True))
    inline_array = []
    for s in stazioni:
        logging.debug(s)
        testo_bottone='Giro {} - {}: {}\n'.format(s[0],emoji.emojize(" :truck:", use_aliases=True), s[1])   
        logging.debug(testo_bottone)
        cod='{}_{}'.format(colore,s[0])
        inline_array.append(InlineKeyboardButton(text=testo_bottone, callback_data=cod))

    logging.debug(inline_array)
    keyboard_elements = [[element] for element in inline_array]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_elements )
    # vidlist = ""
    # for row in mire:
    #         vidlist = vidlist+"[InlineKeyboardButton(text='"+str(row[1])+"', callback_data='"+str(row[0])+"')],"
    # vidlist = vidlist+"]"
    # print(vidlist)
    #keyboard = InlineKeyboardMarkup(inline_keyboard=[vidlist])
    
    conn.close()


    #logging.info(messaggio)
    logging.info(messaggio)
    return messaggio, keyboard

def lista_mezzi(str_targa=''): #targa completa o primi caratteri della targa 
    #conn = psycopg2.connect(host=ip, dbname=db, user=user, password=pwd, port=port) 
    # ora mi connetto al DB
    conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    query='''select nome, targa, brand, modello from ws_way.t_mezzi  
             where targa ilike '{}%' order by targa;'''.format(str_targa.strip())
    try:
        cur.execute(query)
        stazioni=cur.fetchall()
    except Exception as e:
        logging.error(e)

    logging.debug(query)
    #logging.debug(stazioni)

    #messaggio= "\033[1m"+'CONTROLLO OPERATIVITA\' STAZIONI GNSS\n\n'+"\033[0m"
    messaggio= '{0} Clicca sul bottone per scegliere il mezzo {1}'.format(emoji.emojize(" :backhand_index_pointing_down: ", use_aliases=True), emoji.emojize(" :truck: ", use_aliases=True))
    inline_array = []
    for s in stazioni:
        logging.debug(s)
        testo_bottone='Mezzo con targa {} - brand: {} - modello {}\n'.format(s[1], s[2], s[3])   
        logging.debug(testo_bottone)
        cod='sceltamezzo_{}_{}'.format(str_targa,s[1])
        inline_array.append(InlineKeyboardButton(text=testo_bottone, callback_data=cod))

    logging.debug(inline_array)
    keyboard_elements = [[element] for element in inline_array]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_elements )
    # vidlist = ""
    # for row in mire:
    #         vidlist = vidlist+"[InlineKeyboardButton(text='"+str(row[1])+"', callback_data='"+str(row[0])+"')],"
    # vidlist = vidlist+"]"
    # print(vidlist)
    #keyboard = InlineKeyboardMarkup(inline_keyboard=[vidlist])
    
    conn.close()
    
    if keyboard == []:
        messaggio = '{} Nessun mezzo corrispondente alla targa fornita. Ritenta!'.format(emoji.emojize(" :no_entry_sign: ", use_aliases=True))

    #logging.info(messaggio)
    logging.info(messaggio)
    return messaggio, keyboard

# questa classe usa il ChatHandler telepot.aio.helper.ChatHandler (ossia è in ascolto della chat del BOT)
class MessageCounter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0


    async def on_chat_message(self, msg):
        #contatore messaggi
        self._count += 1
        global check
        global testo_segnalazione
        global testo_segnalazione20
        #global allegato
        global chat_id
        global id_mira
        self._check1 = check

        logging.debug('Check1 nel on_chat_message = {}'.format(self._check1))
        content_type, chat_type, chat_id = telepot.glance(msg)
        #content_type, chat_type, chat_id = telepot.glance(msg) #get dei parametri della conversazione e del tipo di messaggio
        

        # qua recupero il messaggio scritto dall'utente
        try:
            command = msg['text'] #get del comando inviato
            logging.debug('Ho letto il seguente messaggio: {}'.format(command))
        except:
            logging.info("Non è arrivato nessun messaggio")
        
        # per ora le immagini non servono
        try:
             if content_type == 'photo':
                 await self.bot.download_file(msg['photo'][-1]['file_id'], '\tmp\file_bot.png')
                 allegato = '\tmp\file_bot.png'
                 logging.info("Immagine recuperata")
                 command="foto"
        except:
             logging.info("Non è arrivato nessuna immagine")

        try:
            nome = msg["from"]["first_name"]
        except:
            nome= ""
        try:
            cognome = msg["from"]["last_name"]
        except:
            cognome= ""
        is_bot = msg["from"]["is_bot"]
        if is_bot=='True':
            await self.sender.sendMessage("ERROR: questo Bot non risponde ad altri bot!")
        elif command == '/webgis':
            message = '''Gentile {1} {2} il link al webGIS di Sistema Ambiente è {3} {4}.'''.format(self._count,nome, cognome, link, note_link)
            await self.sender.sendMessage(message)
        elif command == '/lista_percorsi_blu':
            sent = '''{0} - Gentile {1} {2} ecco la lista dei percorsi della zona blu {3}:'''.format(self._count,nome, cognome, emoji.emojize(" :blue_circle:", use_aliases=True))
            logging.info(sent)
            await self.sender.sendMessage(sent)
            testo, bottoni = lista_percorsi('B') 
            await self.sender.sendMessage(sent, reply_markup=bottoni)
        elif command == '/lista_percorsi_rossa':
            sent = '''{0} - Gentile {1} {2} ecco la lista dei percorsi della zona rossa {3}:'''.format(self._count,nome, cognome, emoji.emojize(" :red_circle:", use_aliases=True))
            logging.info(sent)
            await self.sender.sendMessage(sent)
            testo, bottoni = lista_percorsi('G')
            await self.sender.sendMessage(testo, reply_markup=bottoni)
        elif command == '/lista_percorsi_gialla':
            sent = '''{0} - Gentile {1} {2} ecco la lista dei percorsi della zona gialla {3}:'''.format(self._count,nome, cognome, emoji.emojize(" :yellow_circle:", use_aliases=True))
            logging.info(sent)
            await self.sender.sendMessage(sent)
            testo, bottoni = lista_percorsi('G')
            await self.sender.sendMessage(testo, reply_markup=bottoni)

            
        # elif command == '/avvia_giro' or command.startswith('/avvia_giro'):
        #     sent = '{0} - Gentile {1} {2} stai per scegliere il mezzo per avviare un giro {3}:'.format(self._count,nome, cognome, emoji.emojize(" :white_check_mark:", use_aliases=True))
        #     logging.info(sent)
        #     await self.sender.sendMessage(sent)
        #     targa_str = ''.join(command.split()[-1].strip())
        #     logging.debug(targa_str)
        #     testo, bottoni = lista_mezzi(targa_str)
        #     await self.sender.sendMessage(testo, reply_markup=bottoni)
            
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[                           
                             [InlineKeyboardButton(text='Lista percorsi blu', callback_data='percorsi_blu')],
                             [InlineKeyboardButton(text='Lista percorsi rossi', callback_data='percorsi_rossi')],
                             [InlineKeyboardButton(text='Lista percorsi gialli', callback_data='percorsi_gialli')],
                             [InlineKeyboardButton(text='Link a webGIS', callback_data='sito')],
                             #[InlineKeyboardButton(text='Avvia giro', callback_data='sceltamezzo')],
                             #[InlineKeyboardButton(text='Time', callback_data='time')],
                         ])
                #bot.sendMessage(chat_id, 'Gentile {0} {1} questo è un bot configurato per alcune operazioni minimali, quanto hai scritto non è riconosciuto, invece di fotterti prova con i seguenti tasti:'.format(nome,cognome), reply_markup=keyboard)
            message = "Gentile {} {}, questo è un bot configurato per fornire i percorsi di raccolta di Sistema Ambiente SPA (Lucca).".format(nome, cognome)
                          #"\nIl comando che hai inserito non è riconosciuto dal sistema, " \
                          #"prova a usare i comandi definiti o ancora più semplicemente i seguenti tasti seguenti:".format(nome, cognome)
            await self.sender.sendMessage(message, reply_markup=keyboard)


# questa classe usa il CallbackQueryOriginHandler telepot.aio.helper.CallbackQueryOriginHandler 
# (ossia è in ascolto dei tasti schiacchiati dal BOT)
class Quizzer(telepot.aio.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        super(Quizzer, self).__init__(*args, **kwargs) # non sappiamo bene a cosa serva ma a qualcosa serve
        #self._score = {True: 0, False: 0}
        #self._answer = None
        #self._messaggio = ''
        self.step = 1
        global check
        logging.info("sono dentro la classe quizzer e check vale {}".format(check))
        
    
    async  def _webGIS(self):
        sent = "Gentile {0} {1} il link al webGIS di Sistema Ambiente è {2} {3}".format(self.nome, self.cognome, link, note_link)
        logging.debug(sent)
        logging.debug('Check = {}'.format(check))
        await self.editor.editMessageText(sent)       
    
   
        

    async def _percorsi(self, color):
        logging.debug('sono arrivato qua')
        logging.debug(color)
        if color=='B':
            em = 'blu'.format(emoji.emojize(" :blue_circle:", use_aliases=True))
        elif color=='G':
            em = 'giallo'.format(emoji.emojize(" :yellow_circle:", use_aliases=True))
        elif color=='R':
            em = 'rosso'.format(emoji.emojize(" :red_circle:", use_aliases=True))
        sent = '''Gentile {0} {1} ecco la lista dei percorsi della zona {2}:'''.format(self.nome, self.cognome, em)
        logging.info(sent)
        await self.editor.editMessageText(sent) 
        testo, bottoni = lista_percorsi(color)
        await self.editor.editMessageText(testo, reply_markup=bottoni)

    '''
    async def _mezzi(self, str_targa):
        logging.debug('sono arrivato qua')
        sent = ''Gentile {0} {1} ecco la lista dei mezzi corrispondeti {2}:''.format(self.nome, self.cognome)
        logging.info(sent)
        await self.editor.editMessageText(sent) 
        testo, bottoni = lista_mezzi(str_targa)
        await self.editor.editMessageText(testo, reply_markup=bottoni)
    '''


    # questa è la funzione che reindirizza i bottoni:
    async def on_callback_query(self, msg):
        global testo_segnalazione
        global testo_segnalazione20
        global check
        global id_mira
        logging.debug('Ok sono dentro la funzione on_callback_query')
        logging.debug(msg)
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        logging.debug(query_id)
        logging.debug(from_id)
        logging.debug(query_data)
        #content_type, chat_type, chat_id = telepot.glance(msg)
        #self.chat_id=from_id
        #parte copiata
        #
        # logging.info('Callback Query:', query_id, query_data)
        try:
            command = msg['text'] #get del comando inviato
        except:
            command="Nessun comando"
        try:
            self.nome = msg["from"]["first_name"]
        except:
            self.nome= ""
        try:
            self.cognome = msg["from"]["last_name"]
        except:
            self.cognome= ""
        is_bot = msg["from"]["is_bot"]
        if query_data == 'percorsi_blu':
            logging.info('Ho richiesto i percorsi blu')
            self._answer = await self._percorsi('B')  
        elif query_data == 'percorsi_rossi':
            logging.info('Ho richiesto i percorsi rossi')
            self._answer = await self._percorsi('R') 
        elif query_data == 'percorsi_gialli':
            logging.info('Ho richiesto i percorsi gialli')
            self._answer = await self._percorsi('G') 
        elif query_data == 'sito':
            check=1
            logging.info('ho effettivamente schiacciato il bottone sito')
            self._answer = await self._webGIS()
            
         #risponde al pulsante in cui si sceglie il mezzo   
        # elif query_data[0:12] == 'sceltamezzo':
        #     logging.debug(query_data)
        #     logging.info('ho effettivamente schiacciato il bottone avvia giro{}'.format(query_data))
        #     self._answer = await self._mezzi()
        
        # questo è il secondo gruppo di bottoni creato a partire dal primo tasto
        elif query_data[0:2] in ('B_', 'R_', 'G_'):
            logging.debug(query_data[0:2])
            logging.info('ho effettivamente schiacciato il bottone {}'.format(query_data))
            par_giro=query_data.split('_')
            col=par_giro[0]
            giro=par_giro[1]
            link_mappa="https://gishosting.gter.it/sa/map_sis_ambiente.php?c={}&g={}".format(col,giro)
            kml="https://gishosting.gter.it/sa/kml_sis_ambiente.php?c={}&g={}".format(col,giro)
            logging.info(link_mappa)





            #GOOGLE MAPS (è una parte commentata che non usiamo più ma che potrebbe venir 
            # bene per il discorso pannoloni dove i percorsi saranno ordinati)
            
            
            # # estraggo i vertici della linea
            # # query_vertici= '''SELECT st_y(geom2) as lat, st_x(geom2) as lon 
            # #     FROM (
            # #     SELECT st_transform((ST_DumpPoints(geom)).geom, 4326) AS geom2 
            # #     from percorsi.v_giri g 
            # #     where zona='{}' and giro='{}') foo;'''.format(col, giro)
            
            
            # # estraggo tutti i punti di partenza delle linestring che compongono il giro
            # query_vertici= '''SELECT st_y(st_startpoint(geom2)) as lat_start, st_x(st_startpoint(geom2)) as lon_start 
            #     FROM (
            #     SELECT st_transform((ST_Dump(geom)).geom, 4326) AS geom2 
            #         from percorsi.v_giri g 
            #     where zona='{}' and giro='{}'
            #     ) foo;'''.format(col, giro)


            # try:
            #     conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
            #     conn.set_session(autocommit=True)
            #     cur = conn.cursor()
            #     cur.execute(query_vertici)
            #     vertici=cur.fetchall()
            # except Exception as e:
            #     logging.error(e)

            # logging.debug(query_vertici)
            # #logging.debug(stazioni)


            # #messaggio= "\033[1m"+'CONTROLLO OPERATIVITA\' STAZIONI GNSS\n\n'+"\033[0m"
            
            # link_gmaps= 'https://www.google.com/maps/dir/?api=1&'
            # lat=[]
            # lon=[]
            # for v in vertici:
            #     #link_gmaps = '{}/{},{}'.format(link_gmaps,round(v[0],6),round(v[1],6)) 
            #     lat.append(v[0])
            #     lon.append(v[1])

            # n=len(lat)
            # link_gmaps='{}origin={},{}&destination={},{}&dir_action=navigate&travelmode=driving&waypoints='.format(link_gmaps,lat[0],lon[0],lat[n-1],lon[n-1])

            # i=1
            # while i < n-1:
            #     link_gmaps='{}|{},{}'.format(link_gmaps,lat[i],lon[i])
            #     i+=1
            # logging.debug(link_gmaps)
            # apiurl = "http://tinyurl.com/api-create.php?url="
            # tinyurl = urlopen(apiurl + link_gmaps).read()
            # link_gmaps2 = tinyurl.decode("utf-8")
            # #link_gmaps = tinyurl(link_gmaps)
            # logging.debug(link_gmaps2)
            # sent = "Clicca sul link {0} per visualizzare il giro su google maps.".format(link_gmaps)

            # fine GOOGLE MAPS



            # GISHOSTING
            url_gishosting='www.gishosting.gter.it/lizmap-web-client/lizmap/www/index.php/view/map/'
            repository = 'sisambiente3'
            project='percorsi_progetto_pubblico'
            layers='B0TTTTTTTF'
            epsg=3857
            crs='EPSG:{}'.format(epsg)
            #bbox=


            query_filtro='''select id, 
                replace(replace(replace(st_extent(st_transform(geom,{0}))::text,'BOX(',''),')',''),' ',',')
                from percorsi.mv_contatori_utenze mcu
                where zona ='{1}' and giro='{2}'
                group by id'''.format(epsg, col, giro)

            try:
                conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                cur.execute(query_filtro)
                filtro=cur.fetchall()
            except Exception as e:
                logging.error(e)


            
            for f in filtro:
                #url_gter ='''{}?repository={}&project={}&layers={}&bbox={}&crs={}&filter=mv_contatori_utenze:"id"+IN+(+{}+)'''.format(url_gishosting, repository, project,layers,f[1],crs,f[0])
                params={ 'repository' : repository,
                'project': project,
                'layers': layers,
                'bbox': f[1],
                'crs':crs,
                'filter': 'mv_contatori_utenze:"id"+IN+(+{}+)'.format(f[0])
                }

            url_gter2 = urllib.parse.urlencode(params)
            url_gter = '{}?{}'.format(url_gishosting, url_gter2)
            logging.debug(url_gter)    
            sent='Visualizza il percorso su mappa {0} {1} {0}'.format(emoji.emojize(" :world_map:)", use_aliases=True),url_gter)
            
            
            #link_mappa=short_url.encode_url(link_mappa)
            #kml=short_url.encode_url(kml)
            #sent = "Clicca sul link {0} per visualizzare il giro su google maps.\n Visualizza il KML {1} o scaricalo {2} ".format(link_gmaps, link_mappa, kml)
            
            logging.debug(sent)
            check+=1
            logging.debug('Check = {}'.format(check))
            await self.editor.editMessageText(sent)
            

            

    











# questo è il "main" del BOT che è in ascolto 
bot = telepot.aio.DelegatorBot(TOKEN, [
    #chat
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=120),
    # bottoni    
    pave_event_space()(
        per_callback_query_origin(), create_open, Quizzer, timeout=120),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
logging.info('Listening ...')

loop.run_forever()





