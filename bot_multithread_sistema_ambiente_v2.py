#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

# GTER copyleft 2021
# Rossella Ambrosino 
# Lorenzo Benvenuto
# Roberta Fagandini

# Componente lato server del BOT telegram per Sistema Ambiente SPA

from dataclasses import dataclass
import logging
import os
from aiogram.types import reply_keyboard
from aiogram.types.inline_keyboard import InlineKeyboardButton
import aiogram.utils.markdown as md
from aiogram.types import callback_query, message, message_entity, update
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext, middlewares
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime, timedelta
from aiogram.dispatcher.filters import Text
import psycopg2
import emoji
import asyncio
#import conn
#import config
import credenziali as p
#from pprint import pprint
#import time
import json
from urllib.request import urlopen
from urllib.parse import urlencode


path=os.path.realpath(__file__).replace('bot_multithread_sistema_ambiente_v2.py','')
logfile='{}/log/bot_telegram_sisamb.log'.format(path)
logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', 
    filename=logfile,
    #level=logging.WARNING)
    level=logging.DEBUG)

#****************** credenziali ****************************#
# Il token è contenuto nel file credenziali.py 
# (non sincronizzato su GitHub per evitare utilizzi impropri)
TOKEN=p.bot_token
link=p.link
note_link=p.note_link


#****************** funzioni ****************************#

def esegui_query(connection,query,query_type):
    '''
    Function to execute a generic query in a postresql DB
    
    Query_type:
    
        i = insert
        u = update
        s = select
       
    The function returns:
    
        1 = if the query didn't succeed
        0 = if the query succeed (for query_type u and i)
        array of tuple with query's result = if the query succeed (for query_type s)
    '''
    
    if isinstance(query_type,str)==False:
        logging.warning('query type must be a str. The query {} was not executed'.format(query))
        return 1
    elif query_type != 'i' and query_type !='u' and query_type != 's':
        logging.warning('query type non recgnized for query: {}. The query was not executed'.format(query))
        return 1
    
    
    curr = connection.cursor()
    connection.autocommit = True
    try:
        curr.execute(query)
    except Exception as e:
        logging.error('Query non eseguita per il seguente motivo: {}'.format(e))
        return 1
    if query_type=='s':
        result= curr.fetchall() 
        curr.close()   
        return result
    else:
        return 0


def tiny_url(url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urlopen(apiurl + url).read()
    return tinyurl.decode("utf-8")


def layer_order(lizmap_cfg_path): #lizmap_config

    with open(lizmap_cfg_path) as json_file:
        data = json.load(json_file)

    layernames = list(data['layers'].keys())
    
    return layernames

""" 
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

def lista_mezzi(codicegiro, str_targa=''): #targa completa o primi caratteri della targa 
    #conn = psycopg2.connect(host=ip, dbname=db, user=user, password=pwd, port=port) 
    # ora mi connetto al DB
    conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    #query su t mezzi manca filtro su data
    #query='''select name, fleetname from ws_way.t_mezzi  
    #         where name ilike '%{}%'
    #         and fleetname not in ('presse', 'cassoni', 'scarrabili', 'siam-wappy')
    #         order by name limit 50;'''.format(str_targa.strip())

    query='''select name, fleetname from ws_way.v_last_position2
             where name ilike '%{}%'
             and fleetname != 'autovetture'
             order by name limit 50;'''.format(str_targa.strip()) 

    try:
        cur.execute(query)
        stazioni=cur.fetchall()
    except Exception as e:
        logging.error(e)
        

    logging.debug(query)
    

    
    messaggio= '{0} Clicca sul bottone per scegliere il mezzo {1}'.format(emoji.emojize(" :backhand_index_pointing_down: ", use_aliases=True), emoji.emojize(" :truck: ", use_aliases=True))
    inline_array = []
    for s in stazioni:
        logging.debug(s)
        testo_bottone='Mezzo {}, flotta  {}\n'.format(s[0], s[1])   
        logging.debug(testo_bottone)
        cod='_{}_{}'.format(codicegiro,s[0])
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
    return messaggio, keyboard """

def keyboard (kb_config):
    _keyboard= types.InlineKeyboardMarkup ()
    for rows in kb_config:
        btn= types.InlineKeyboardButton (
            callback_data= rows [0],
            text= rows [1]
        )
        _keyboard.insert (btn)
    return _keyboard

#********************* Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@ dp.callback_query_handler ()
async def callback (callback_query: types.CallbackQuery):

    await bot.answer_callback_query (callback_query.id, text= callback_query.data,)
    con = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
    if callback_query.data=='':
        pass
    else:
        pass

#**************************** inizio command '/servizio'
class Form (StatesGroup):
    
    badge_operatore = State()             #codice badge operatore
    incarico = State()
    #aggiungere qui altri states of the user per aggiungere funzionalità




@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: not message.text.isdigit() or len(message.text)!= 7,state=Form.badge_operatore)
async def process_invalid_text(message: types.Message, state: FSMContext):

    return await message.reply("Codice badge inserito con valido. Riprova {}".formt(emoji.emojize(":warning:",use_aliases=True)))


@dp.message_handler(lambda message: message.text.isdigit() and len(message.text) == 7, state=Form.badge_operatore)
async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await Form.next()
        await state.update_data(badge_operatore=message.text)
        data['badge_operatore'] = message.text        
        logging.debug('******************** badge {} *******************'.format(data['badge_operatore']))

        con = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
        #query_servizio = '''select * from schedulazione.servizio where TRIM("COD BADGE OPERATORE") ='{}' and "DATA SERVIZIO" >= now()::date'''.format(data['badge_operatore'])
        query_servizio = '''select * from schedulazione.servizio where TRIM("COD BADGE OPERATORE") ='{}' 
                            and "DATA SERVIZIO" >= '2021-07-16'::date 
                            order by  "DATA SERVIZIO", "DA ORA A ORA"''' .format(data['badge_operatore'])

        check_servizio = esegui_query(con,query_servizio,'s')

        if check_servizio == 1:
            await bot.send_message(message.chat.id,'''{} Si è verificato un problema, e non è possibile verificare quali incarichi ti sono assegnati:
                        \nSe visualizzi questo messaggio prova a contattare un tecnico'''.format(emoji.emojize(":warning:",use_aliases=True)))
            
            await state.finish()

        elif len(check_servizio) == 0:
            await bot.send_message(message.chat.id,'''{} Al momento non risultano servizi associati al tuo codice badge, per cui non puoi usare questo comando.
                                                        \nContatta un amministratore di sistema per maggiori informazioni '''.format(emoji.emojize(":no_entry_sign:",use_aliases=True)))
            await state.finish()

        else:
            #await bot.send_message(message.chat.id,'''{}  Visualizzazione incarichi'''.format(emoji.emojize(":thumbs_up:",use_aliases=True)))
            
            nome_operatore = check_servizio[0][9].strip().title()
            """ 
            reply_list = [['row_{0}_{1}'.format(i[0], i[1]),  #sostituire con identificativo riga appena disponibile
                            '{} {} {} {} '.format(emoji.emojize(":date:",use_aliases=True),
                                                    i[0], #data
                                                    emoji.emojize("::clock830:",use_aliases=True),
                                                    i[1]), #ora
                            "message text", 
                            None] 
                            for i in check_servizio]
            await bot.send_message(
                chat_id=message.from_user.id,
                text='''{} Ciao {}, ecco gli incarichi che ti sono assegnati
                \n\n{} Scegli un incarico per maggiori dettagli'''.format(emoji.emojize(":white_check_mark:",use_aliases=True),
                                                                          nome_operatore,
                                                                          emoji.emojize(":hourglass_flowing_sand:",use_aliases=True)),
                reply_markup= keyboard(reply_list))

            #elimino messaggio con comando per evitare tocchi maldestri
            #await bot.delete_message(message.chat.id,message.message_id)
            """

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            incarichi = {}
            c = 0
            for i in check_servizio:
                c+=1
                text_incarico = '{} - {} {} \n{} {} '.format(c,
                                                              emoji.emojize(":date:",use_aliases=True),
                                                              i[0], #data
                                                              emoji.emojize(":clock830:",use_aliases=True),
                                                              i[1])
                markup.add(text_incarico)
                
                incarichi[str(c)]=i  

            await Form.incarico.set()
            #async with state.proxy() as data:
            data['incarichi']= incarichi
            data['user']= nome_operatore


            await bot.send_message(
                chat_id=message.from_user.id,
                text='''{} Ciao {}, ecco gli incarichi che ti sono assegnati
                \n{} Scegli un incarico per maggiori dettagli'''.format(emoji.emojize(":white_check_mark:",use_aliases=True),
                                                                        nome_operatore,
                                                                        emoji.emojize(":point_down:",use_aliases=True)),
                reply_markup= markup)
            #await state.finish()

@dp.message_handler(state=Form.incarico)
async def process_incarico(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logging.debug('*************** DATA KEYS {}'.format(data.keys()))
        logging.debug('*************** INCARICO SELEZIONATO {}'.format(message.text[0]))
        #logging.debug('*************** INCARIZHI SELEZIONABILI {}'.format( [i[0] for i in data['incarichi'].keys()])) #data['incarichi'].keys()))

        #if message.text not in data['incarichi'].keys():
        if message.text[0] not in data['incarichi'].keys(): #[i[0] for i in data['incarichi'].keys()]:
            await message.reply('Il testo inserito non è valido. Seleziona un incarico usando le opzioni presenti sulla tastiera.')
        else:
            data['incarico'] = message.text
            markup_old = types.ReplyKeyboardRemove()
            #await bot.send_message(message.chat.id,'Hai selezionato {}'.format(data['incarico']), reply_markup=markup_old)

            info_incarico = data['incarichi'][data['incarico'][0]]

            # Preparo reindirizzamento alla mappa GISHOSTING
            #par_giro=query_data[1:].split('_')
            #col=par_giro[0]
            #giro=par_giro[1]
            mezzo=info_incarico[7].strip()
            giro = ''
            col = ''



            #mappa
            url_gishosting='www.gishosting.gter.it/lizmap-web-client/lizmap/www/index.php/view/map/'
            repository = 'sisambiente3'
            project='percorsi_progetto_pubblico'
            epsg=3857
            crs='EPSG:{}'.format(epsg)
            #bbox=
            

            
            #layers
            #layers='B0TTTTTTTF' #per vedere solo i percorsi
            #layers='B0TTTTTTTT'
            #dal basso verso l'alto 
            # 'B00000TTF' baselayer? zero ? TTF= true for frazioni and comuni , false per giri
            #a T or F for giro in giri group
            #'TTTTTT'  = include anche i mezzi
            #layers = 'B00000TTF' + 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFT' + 'TTTTTT'
            
            #verifico i layer pubblicatisul web 
            layerlist = layer_order(p.lizmap_config)
            layerlist_giri = [i for i in layerlist if i.startswith('v_giri')]
            activelayers = ['v_last_position2', 'limiti_amministrativi', 'frazioni',  'giri']
            
            if col != '':
                #aggiungo il percorso scelto alla listadei layer da rendere visibili
                percorso_scelto = 'v_giro_{}_{}'.format(col.lower(), giro.lower().replace(' ', ''))
                activelayers.append(percorso_scelto)
            else:
                activelayers = activelayers + layerlist_giri
                

            #costrusico la stringa per l'indirizzo inserendo una 'T' per ogni layer attivo
            # NB ordine inverso : la lista dei layer deve essere definita dal basso verso l'altro 
            layers = 'B0' + ''.join(['T' if i in activelayers else 'F' for i  in reversed(layerlist) ])
            #layers = 'B00000TTF' + ''.join(['T' if i = percorso_scelto else 'F' for i  in reversed(layerlist_giri) ])  + 'TTTTTT'

            #filtro percorso
            #query_filtro='''select id, 
            #    replace(replace(replace(st_extent(st_transform(geom,{0}))::text,'BOX(',''),')',''),' ',',')
            #    from percorsi.mv_contatori_utenze mcu
            #    where zona ='{1}' and giro='{2}'
            #    group by id'''.format(epsg, col, giro)

            #query estensione standart: bbocx comprendente tutti i percorsi
            query_filtro='''select 
                replace(replace(replace(st_extent(st_transform(geom,{0}))::text,'BOX(',''),')',''),' ',',')
                from percorsi.mv_contatori_utenze mcu'''.format(epsg, col, giro)

            try:
                conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                cur.execute(query_filtro)
                filtro=cur.fetchall()
            except Exception as e:
                logging.error(e)

            #filtro mezzo 
            query_filtro_mezzo =''' select id
                from ws_way.v_last_position2 v
                where name = '{0}'; '''.format(mezzo.lower().strip())

            try:
                cur2 = conn.cursor()
                cur2.execute(query_filtro_mezzo)                
            except Exception as e:
                logging.error(e)

            
            filtro_mezzo=cur2.fetchall()

            
            
            #Definisco URL
            #url_gter ='''{}?repository={}&project={}&layers={}&bbox={}&crs={}&filter=mv_contatori_utenze:"id"+IN+(+{}+)'''.format(url_gishosting, repository, project,layers,f[1],crs,f[0])
            params={ 'repository' : repository,
                'project': project,
                'layers': layers,
                'bbox': filtro[0][0],
                'crs':crs,
                #'filter': 'mv_contatori_utenze:"id"+IN+(+{}+)'.format(f[0])
                #'filter': 'v_last_position2:"id"+IN+(+{}+)'.format(filtro_mezzo[0][0])
                }
            
            if filtro_mezzo == []:
                logging.warning('Mezzo non trovato')
                mezzo = ''
            else:
                params['filter']= 'v_last_position2:"id"+IN+(+{}+)'.format(filtro_mezzo[0][0])

            url_gter2 = urlencode(params)
            url_gter = '{}?{}'.format(url_gishosting, url_gter2)
            logging.debug(url_gter) 
            
            
            if giro == '' and mezzo!= '':
                info_mappa ='''Per questo incarico non è disponibile il percorso. 
                               \nPuoi comunque consultare la mappa per visualizzare la posizione del mezzo \n\n{0}'''.format(url_gter)
            elif giro != '' and  mezzo == '':
                info_mappa ='''Per questo incarico non è disponibile il tracciamento del mezzo 
                              \nPuoi comunque consultare la mappa per visualizzare il percorso \n\n{0}'''.format(url_gter)
            elif giro == '' and  mezzo == '':                  
                info_mappa ='''Per questo incarico la mappa non è disponibile'''
            else:
                info_mappa ='Visualizza il percorso e la posizione del mezzo sulla mappa  \n\n{0}'.format(url_gter)
            

            to_send = '''Ecco i dettagli dell'incarico selezionato: \n\n{} \n{} {} \n{} {} \n{} {} \n{} {}'''.format(data['incarico'][3:].strip(), #data e ora
                                         emoji.emojize(":recycling_symbol:" , use_aliases=True), info_incarico[3].strip(),   #"DESCRIZIONE SERVIZIO"
                                         emoji.emojize(":truck:", use_aliases=True), info_incarico[7].strip(),                #mezzo
                                         emoji.emojize(":arrow_lower_right:", use_aliases=True), info_incarico[5].strip(),                     #"DESCRIZIONE ZONA"
                                         emoji.emojize(":world_map:", use_aliases=True), info_mappa
                                         )
            
            #link_mappa=short_url.encode_url(link_mappa)
            #kml=short_url.encode_url(kml)
            #sent = "Clicca sul link {0} per visualizzare il giro su google maps.\n Visualizza il KML {1} o scaricalo {2} ".format(link_gmaps, link_mappa, kml)
            

            await bot.send_message(message.chat.id,to_send, reply_markup=markup_old)
            await state.finish()




#Command hendler for command '/servizio'
@dp.message_handler(commands='servizio')
async def cmd_start(message: types.Message):

    #check id telegram
    con = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)   
    query_telegram_id= "select * from schedulazione.t_telegramid where telegramid ='{}'".format(message.chat.id)
    
    check_telegram = esegui_query(con,query_telegram_id,'s')

    if check_telegram ==1:
        await bot.send_message(message.chat.id,'''{} Si è verificato un problema, e non è possibile capire se il tuo dispositivo è abilitato per interagire con il BOT di Sitema Ambiente.
                        \nSe visualizzi questo messaggio prova a contattare un tecnico'''.format(emoji.emojize(":warning:",use_aliases=True)))


    elif len(check_telegram) == 0:
        await bot.send_message(message.chat.id,'''{} Il telegram_id associato al dispositivo non è registrato nel sistema e pertanto non puoi usare questo comando.
                        \nContatta un amministratore di sistema per abilitare il dispositivo, e dopo esser stato abilitato ripeti questo comando.'''.format(emoji.emojize(":no_entry_sign:",use_aliases=True)))
    
    else:
        # Set state
        await Form.badge_operatore.set()    
        await message.reply("Ciao, inserisci il codice del badge per visualizzare gli incarichi assegnati")            







#****************************************** Altri comandi
@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await bot.send_message(message.chat.id,"Benvenuto/a {}!\nQuesto BOT è stato realizzato per il personale interno di Sistema Ambiente SPA (Lucca)\nScopri cosa può fare questo BOT andando sul comando /help".format(message.from_user.first_name))

@dp.message_handler(commands='help')
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await bot.send_message(message.chat.id,"""Le funzioni del Bot di Sistema Ambiente sono:\n
    \n{0} start: Avvia il bot per la prima volta
    \n{0} help: Scopri le funzionalità del BOT
    \n{0} telegram_id: Ottieni il codice telegram da comuicare per abilitare il bot sul dispositivo
    \n{0} servizio: Visualizza gli incarichi assegnati
    \n\nPuoi accedere a questi comandi cliccando sul Menu in basso a sinistra o digitando il comando desiderato preceduto dal carattere '/'  (es. /start). """.format(emoji.emojize(":arrow_forward:",use_aliases=True)))
    ##\n\nTramite questo BOT potrai anche ricevere notifiche dal sistema. Per fare questo devi inserire il tuo telegram_id nel portale e attivare le notifiche.
    #\n{0} webgis: restituisce il link al webgis

# comando per telegram ID
@dp.message_handler(commands=['telegram_id'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/telegram_id` command
    """
    await message.reply("Ciao {}, il codice (telegram id) da comunicare per far abilitare questo device a interagire con questo BOT è {}".format(message.from_user.first_name,message.chat.id))

# comando per webgis
@dp.message_handler(commands=['webgis'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/webgis` command
    """
    await message.reply("Ciao {}, il link al webGIS di Sistema Ambiente è {}, {}".format(message.from_user.first_name, link, note_link))






# questa funzione deve essere l'ultima dello script 
# altrimenti entra qui dentro e ignora le funzioni successive
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message):
    await message.reply('Il comando che hai inserito non è riconosciuto dal sistema. Usa il comando /help per scoprire le funzionalità di questo bot') 

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
