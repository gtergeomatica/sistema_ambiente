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

    profilo_telegram = State()
    badge_operatore = State()     
    incarico = State()
    redo = State()    
    #aggiungere qui altri states of the user per aggiungere funzionalità




@dp.message_handler(state='*', commands='reset')
@dp.message_handler(Text(equals='reset', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    #logging.debug('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Reset effettuato! Seleziona un comando per rincominciare ad usare il Bot', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: not message.text.isdigit() or len(message.text)!= 7,state=Form.badge_operatore)
async def process_invalid_text(message: types.Message, state: FSMContext):

    return await message.reply("Codice badge inserito con valido. Riprova {}".format(emoji.emojize(":warning:",use_aliases=True)))


@dp.message_handler(lambda message: message.text.isdigit() and len(message.text) == 7, state=Form.badge_operatore)
async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await Form.next()
        await state.update_data(badge_operatore=message.text)
        data['badge_operatore'] = message.text        
        logging.debug('******************** badge {} *******************'.format(data['badge_operatore']))

        con = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
        #query_servizio = '''select * from schedulazione.servizio where TRIM("COD BADGE OPERATORE") ='{}' and "DATA SERVIZIO" >= now()::date'''.format(data['badge_operatore'])
        # query_servizio = '''select "DATA SERVIZIO",
        #                           "DA ORA A ORA",
        #                           "COD SERVIZIO",
        #                           "DESCRIZIONE SERVIZIO",
        #                           "COD ZONA",
        #                           "DESCRIZIONE ZONA",
        #                           "COD MEZZO",
        #                           "MATRICOLA MEZZO",
        #                           "COD BADGE OPERATORE",
        #                           "COGNOME E NOME",
        #                           "DATA MODIFICA",
        #                           utente 
        #                           from schedulazione.t_servizi 
        #                           where TRIM("COD BADGE OPERATORE") ='{}' 
        #                           and ("DATA SERVIZIO" = now()::date
        #                           or "DATA SERVIZIO" = now()::date + interval '1' day)
        #                           ''' .format(data['badge_operatore'])
        query_servizio = '''select * from schedulazione.v_query_bot
                             where TRIM(cod_badge_op) ='{}' 
                            order by data_servizio, ore_servizio'''.format(data['badge_operatore'])

                            
        check_servizio = esegui_query(con,query_servizio,'s')

        if check_servizio == 1:
            await bot.send_message(message.chat.id,'''{} Si è verificato un problema, e non è possibile verificare quali servizi ti sono assegnati:
                        \nSe visualizzi questo messaggio prova a contattare un tecnico'''.format(emoji.emojize(":warning:",use_aliases=True)))
            
            await state.finish()

        elif len(check_servizio) == 0:
            await bot.send_message(message.chat.id,'''{} Al momento non risultano servizi associati al tuo codice badge, per cui non puoi usare questo comando.
                                                        \nContatta un amministratore di sistema per maggiori informazioni '''.format(emoji.emojize(":no_entry_sign:",use_aliases=True)))
            await state.finish()

        else:
            #await bot.send_message(message.chat.id,'''{}  Visualizzazione incarichi'''.format(emoji.emojize(":thumbs_up:",use_aliases=True)))
            
            nome_operatore = check_servizio[0][13]
            if nome_operatore == None:
                nome_operatore= ''
            else:
                nome_operatore = nome_operatore.strip().title()
           
                      
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
            markup_list=[]
            c = 0
            for i in check_servizio:
                c+=1
                text_incarico = '{} - {} {} {} {} \n{} {} '.format(c,
                                                              emoji.emojize(":date:",use_aliases=True),
                                                              i[1], 
                                                              emoji.emojize(":clock830:",use_aliases=True),
                                                              i[2], 
                                                              emoji.emojize(":truck:", use_aliases=True),
                                                              i[9] or 'Non definito')
                markup.add(text_incarico)
                markup_list.append(text_incarico)
                incarichi[str(c)]=i  

            await Form.incarico.set()
            #async with state.proxy() as data:
            data['incarichi']= incarichi
            data['user']= nome_operatore
            data['markup_list'] = markup_list


            await bot.send_message(
                chat_id=message.from_user.id,
                text='''{} Ciao {}, ecco i servizi che ti sono assegnati
                \n{} Scegli un servizio per maggiori dettagli'''.format(emoji.emojize(":white_check_mark:",use_aliases=True),
                                                                        nome_operatore,
                                                                        emoji.emojize(":point_down:",use_aliases=True)),
                reply_markup= markup)
            #await state.finish()

@dp.message_handler(state=Form.incarico)
async def process_incarico(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        #logging.debug('*************** DATA KEYS {}'.format(data.keys()))
        #logging.debug('*************** INCARICO SELEZIONATO {}'.format(message.text[0]))
        #logging.debug('*************** INCARIZHI SELEZIONABILI {}'.format( [i[0] for i in data['incarichi'].keys()])) #data['incarichi'].keys()))

        #if message.text not in data['incarichi'].keys():
        if message.text[0] not in data['incarichi'].keys(): #[i[0] for i in data['incarichi'].keys()]:
            await message.reply('Il testo inserito non è valido. Seleziona un servizio usando le opzioni presenti sulla tastiera.')
        else:
            data['incarico'] = message.text
            
            

            info_incarico = list(data['incarichi'][data['incarico'][0]])
            info_incarico = [ '' if i == None else i for i in info_incarico   ]
            info_incarico = [ i.strip() if type(i) == 'str' else i for i in info_incarico   ]
            



            # Preparo reindirizzamento alla mappa GISHOSTING
             
            s_id = info_incarico[0]
            s_data_servizio = info_incarico[1]
            s_ore_servizio= info_incarico[2]
            s_ora_inizio= info_incarico[3]
            s_ora_fine = info_incarico[4]
            s_cod_servizio = info_incarico[5]
            s_desc_servizio = info_incarico[6]
            s_cod_zona = info_incarico[7]
            s_desc_zona = info_incarico[8]
            s_cod_mezzo = info_incarico[9]
            s_matricola_mezzo = info_incarico[10]
            s_id_mezzo_query = info_incarico[11]
            s_cod_badge_op = info_incarico[12]
            s_nome_op = info_incarico[13]
            s_data_mod = info_incarico[14]
            s_utente_mod = info_incarico[15]
            s_cod_uni = info_incarico[16]
            s_giro = info_incarico[17] #numero giro
            s_zona= info_incarico[18] #colore (RBG)
            s_note = info_incarico[19]



            #mappa
            url_gishosting='www.gishosting.gter.it/lizmap-web-client/lizmap/www/index.php/view/map/'
            repository = 'sisambiente3'
            project='percorsi_progetto_pubblico'
            epsg=3857
            crs='EPSG:{}'.format(epsg)
            

            
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
            activelayers = ['limiti_amministrativi', 'frazioni'] #,  'giri'] 
            #giri è un gruppo - abilito la funzione hide checkbox for group

            if data['profilo_telegram'] in ['T', 'O'] and s_id_mezzo_query != '' and s_id_mezzo_query != None :
                #aggiungo alla lista dei layer da rendere :
                #aggiungo alla lista dei layer da rendere visibili 
                # il layer contente le posizioni dei mezzi per i soli utenti abilitati 
                # e solo se il mezzo è disponibile
                #logging.debug('********************** Aggiungo layer mezzi :{}'.format(s_id_mezzo_query))
                activelayers.append('v_last_position2')
            
            if s_zona != '' and s_giro != '':
                #aggiungo il percorso scelto alla lista dei layer da rendere visibili
                percorso_scelto = 'v_giro_{}_{}'.format(s_zona.lower(), s_giro.lower().replace(' ', ''))
                activelayers.append(percorso_scelto)
            else:
                activelayers = activelayers + layerlist_giri
                

            #costrusico la stringa per l'indirizzo inserendo una 'T' per ogni layer attivo
            # NB ordine inverso : la lista dei layer deve essere definita dal basso verso l'altro 
            layers = 'B0' + ''.join(['T' if i in activelayers else 'F' for i  in reversed(layerlist) ])
            if 'v_last_position2' in activelayers:
                # in caso questo layer si attivo richiede 2 T invece che 1 per essere visualizzato
                layers = layers[:-2] + 'TT' 
            #layers = 'B00000TTF' + ''.join(['T' if i = percorso_scelto else 'F' for i  in reversed(layerlist_giri) ])  + 'TTTTTT'
            #logging.debug('ACTIVELAYERS '+ '{}, '.join(activelayers))
            #filtro percorso
            #query_filtro='''select id, 
            #    replace(replace(replace(st_extent(st_transform(geom,{0}))::text,'BOX(',''),')',''),' ',',')
            #    from percorsi.mv_contatori_utenze mcu
            #    where zona ='{1}' and giro='{2}'
            #    group by id'''.format(epsg, col, giro)

            #query estensione standart: bbocx comprendente tutti i percorsi
            query_filtro='''select 
                replace(replace(replace(st_extent(st_transform(geom,{0}))::text,'BOX(',''),')',''),' ',',')
                from percorsi.mv_contatori_utenze mcu'''.format(epsg, s_zona, s_giro)

            try:
                conn = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                cur.execute(query_filtro)
                filtro=cur.fetchall()
            except Exception as e:
                logging.error(e)

            
            
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
            #aggiungo filtro sul mezzo     
            if data['profilo_telegram'] in ['T', 'O'] and s_id_mezzo_query != '' and s_id_mezzo_query != None :
                params['filter']= 'v_last_position2:"id"+IN+(+{}+)'.format(s_id_mezzo_query)

            url_gter2 = urlencode(params)
            url_gter = '{}?{}'.format(url_gishosting, url_gter2)
            #logging.debug(url_gter) 
            

            if s_giro == '' and s_id_mezzo_query!= '':
                if data['profilo_telegram'] in ['T', 'O']:
                    info_mappa ='''Per questo servizio non è disponibile il percorso. 
                               \nPuoi comunque consultare la mappa per visualizzare la posizione del mezzo \n\n{0}'''.format(url_gter)
                else:
                    info_mappa = '''Mappa non disponibile. Per questo servizio il tracciamento del mezzo è attivo ma il tuo profilo utente non è abilitato a visualizzarlo. Percorso non disponibile. '''
            elif s_giro != '' and  s_id_mezzo_query == '':
                if data['profilo_telegram'] in ['T', 'O']:
                    info_mappa ='''Per questo servizio non è disponibile il tracciamento del mezzo 
                              \nPuoi comunque consultare la mappa per visualizzare il percorso \n\n{0}'''.format(url_gter)
                else:
                    info_mappa = '''Per questo servizio non è disponibile il tracciamento del mezzo e il tuo profilo utente non è abilitato a visualizzarlo
                              \nPuoi comunque consultare la mappa per visualizzare il percorso \n\n{0}'''.format(url_gter)
                
            elif s_giro == '' and  s_id_mezzo_query == '':                  
                info_mappa ='''Per questo servizio la mappa non è disponibile'''
            else:
                if data['profilo_telegram'] in ['T', 'O']:
                    info_mappa ='Visualizza il percorso e la posizione del mezzo sulla mappa  \n\n{0}'.format(url_gter)
                else:
                    info_mappa ='Per questo servizio il tracciamento del mezzo è attivo ma il tuo profilo utente non è abilitato a visualizzare la posizione del mezzo. Puoi comunque consultare la mappa per visualizzare il percorso  \n\n{0}'.format(url_gter)
            

            to_send = '''Ecco i dettagli del servizio selezionato: \n\n{}{} \n{} {} \n{} {} \n{} {} \n{} {} \n{} {} \n{} {}'''.format(emoji.emojize(":date:",use_aliases=True), s_data_servizio,
                                                            emoji.emojize(":clock830:",use_aliases=True), s_ore_servizio,
                                                            emoji.emojize(":truck:", use_aliases=True), s_matricola_mezzo,
                                                            emoji.emojize(":recycling_symbol:" , use_aliases=True), s_desc_servizio,
                                                            emoji.emojize(":arrow_lower_right:", use_aliases=True), s_desc_zona,
                                                            emoji.emojize(":information:", use_aliases=True), s_note or '',
                                                            emoji.emojize(":world_map:", use_aliases=True), info_mappa
                                                            )
                                
            #link_mappa=short_url.encode_url(link_mappa)
            #kml=short_url.encode_url(kml)
            #sent = "Clicca sul link {0} per visualizzare il giro su google maps.\n Visualizza il KML {1} o scaricalo {2} ".format(link_gmaps, link_mappa, kml)
            
            markup_to_close = types.ReplyKeyboardRemove()
            await bot.send_message(message.chat.id,to_send, reply_markup=markup_to_close)

            await Form.redo.set()
            markup_again = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup_again.add("si", "no")

            await bot.send_message(message.chat.id,'Vuoi visualizzare i dettagli di un altro servizio? ', reply_markup=markup_again)

            


@dp.message_handler(state=Form.redo)
async def process_other(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        #logging.debug('*************** DATA KEYS {}'.format(data.keys()))
        #logging.debug('***************  opzione selezionata {}'.format(message.text))
        #logging.debug('*************** INCARIZHI SELEZIONABILI {}'.format( [i[0] for i in data['incarichi'].keys()])) #data['incarichi'].keys()))
       
        
        message_parsed = message.text.lower().strip()
        if message_parsed not in ['si', 's', 'yes', 'y', 'no', 'n']:
            await message.reply('''Il testo inserito non è valido. Seleziona una delle opzioni presenti sulla tastiera o scrivi 
                                   \n'si' per vedere un altro servizio
                                   \n'no' per chiudere la comunicazione''')
        else:
            markup_to_close = types.ReplyKeyboardRemove()
            data['redo'] = message_parsed

            if data['redo'] in ['si', 's', 'yes', 'y']:
                await Form.incarico.set()

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                for row in data['markup_list']:
                    markup.add(row)

                await bot.send_message(
                chat_id=message.from_user.id,
                text=''' {} Scegli un servizio per maggiori dettagli {}'''.format(emoji.emojize(":white_check_mark:",use_aliases=True),
                                                                         emoji.emojize(":point_down:",use_aliases=True)),
                reply_markup= markup)

            else:
                await bot.send_message(
                chat_id=message.from_user.id,
                text='''Grazie per aver utilizzato il Bot SIU Sistema Ambiente. A presto! {}'''.format( emoji.emojize(":wave:",use_aliases=True)),
                reply_markup= markup_to_close)
                await state.finish()



#Command hendler for command '/servizio'
@dp.message_handler(commands='servizio')
async def cmd_start(message: types.Message, state: FSMContext):

    #check id telegram
    con = psycopg2.connect(host=p.host, dbname=p.db, user=p.user, password=p.pwd, port=p.port)   
    query_telegram_id= "select d_profilo  from schedulazione.t_telegramid where telegramid ='{}'".format(message.chat.id)
    
    check_telegram = esegui_query(con,query_telegram_id,'s')

    if check_telegram ==1:
        await bot.send_message(message.chat.id,'''{} Si è verificato un problema, e non è possibile capire se il tuo dispositivo è abilitato per interagire con il BOT di Sitema Ambiente.
                        \nSe visualizzi questo messaggio prova a contattare un tecnico'''.format(emoji.emojize(":warning:",use_aliases=True)))


    elif len(check_telegram) == 0:
        await bot.send_message(message.chat.id,'''{} Il telegram_id associato al dispositivo non è registrato nel sistema e pertanto non puoi usare questo comando.
                        \nUtilizza il comado /telegram_id per maggiori informazioni.'''.format(emoji.emojize(":no_entry_sign:",use_aliases=True)))
    
    else:

        async with state.proxy() as data:
            data['profilo_telegram'] = check_telegram[0][0] #'T', 'A', 'O'

        # Set state
        await Form.badge_operatore.set()          
        await message.reply("Ciao, inserisci il codice del badge per visualizzare i servizi assegnati")            







#****************************************** Altri comandi
@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await bot.send_message(message.chat.id,"Benvenuto/a!\nQuesto BOT è stato realizzato per il personale interno di Sistema Ambiente SPA (Lucca)\nScopri cosa può fare questo BOT andando sul comando /help")

@dp.message_handler(commands='help')
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await bot.send_message(message.chat.id,"""Le funzioni del Bot di Sistema Ambiente sono:\n
    \n{0} start: Avvia il bot per la prima volta
    \n{0} help: Scopri le funzionalità del BOT
    \n{0} telegram_id: Ottieni il codice telegram da comuicare per abilitare il bot sul dispositivo
    \n{0} servizio: Visualizza i servizi assegnati
    \n\nPuoi accedere a questi comandi cliccando sul Menu in basso a sinistra o digitando il comando desiderato preceduto dal carattere '/'  (es. /telegram_id). """.format(emoji.emojize(":arrow_forward:",use_aliases=True)))
    ##\n\nTramite questo BOT potrai anche ricevere notifiche dal sistema. Per fare questo devi inserire il tuo telegram_id nel portale e attivare le notifiche.
    #\n{0} webgis: restituisce il link al webgis

# comando per telegram ID
@dp.message_handler(commands=['telegram_id'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/telegram_id` command
    """
    await message.reply("Ecco il tuo telegram id: {}. \nComunica questo codice ad un amministratore di sistema per poter interagire con il Bot SIU Sistema Ambiente da questo dispositivo.".format(message.chat.id))

# comando per webgis
@dp.message_handler(commands=['webgiss'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/webgis` command
    """
    await message.reply("Ciao, il link al WebGIS di Sistema Ambiente è {}, {}".format(link, note_link))






# questa funzione deve essere l'ultima dello script 
# altrimenti entra qui dentro e ignora le funzioni successive
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message):
    await message.reply('Il comando che hai inserito non è riconosciuto dal sistema. Usa il comando /help per scoprire le funzionalità di questo bot') 

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
