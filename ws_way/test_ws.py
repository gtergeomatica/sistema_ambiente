#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Gter copyleft 2021
# Author: Roberto Marzocchi
# Script che interroga i WS di WAY srl per ottenere le posizioni dei mezzi






import os, sys, re  # ,shutil,glob

import getopt  # per gestire gli input

#import pymssql

import psycopg2
#import credenziali as p
import requests

import logging

path=os.path.realpath(__file__).replace('test_ws.py', '')
#tmpfolder=tempfile.gettempdir() # get the current temporary directory
logfile='{}/log/ws.log'.format(path)
#if os.path.exists(logfile):
#    os.remove(logfile)

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', # overwrite or append
    #filename=logfile,
    level=logging.WARNING)

import token_api as t

import xml.etree.ElementTree as et

from xml.etree.ElementTree import parse


def GetVehicleList(token):
    
    ''' Ottengo XML con la lista dei veicoli di SistemaAmbiente
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
    #print("Info recieved...")
    #print(response.content)
    ret= r.status_code
    if ret == 200: 
        logging.debug("Vehicle List obtained")
    #print(r.content)
    root = et.fromstring(r.content)
    #print(root)
    n_Vehicle=len(root[0][0][0][5].tag)
    i=0
    id_mezzi=[]
    nomi=[]
    targhe=[]
    brands=[]
    modelli=[]
    while i<n_Vehicle:  
        id_mezzi.append(root[0][0][0][5][i][0].text)
        nomi.append(root[0][0][0][5][i][4].text)
        targhe.append(root[0][0][0][5][i][5].text)
        brands.append(root[0][0][0][5][i][7].text)
        modelli.append(root[0][0][0][5][i][8].text)
        i+=1

    # la funzione restituisce i seguenti array
    return id_mezzi, nomi, targhe, brands, modelli 





def GetVehicleHistoryEvents(token):

    ''' Ottengo XML con lalista dei veicoli di SistemaAmbiente
    unico input è il token che scade dopo un'ora di inattività'''


    

def main():
    # recupero il token 
    r= requests.get('{}/GetToken'.format(t.url), params={'serverName':t.servername, 'userName':t.username, 'password':t.password})
    print(r.status_code)
    print(r.url)
    root = et.fromstring(r.content)
    token=root.text
    print(token)
    
    
    risposta=GetVehicleList(token)
    #print(risposta[0])
    id_mezzi=risposta[0]
    i=0
    while i < len(id_mezzi):
        print(id_mezzi[i])
        i+=1

    # sono da caricare i mezzi sul DB PostgreSQL

    # ciclo sui mezzi

    # per ogni mezzo usare due funzioni a definire che chiamino i 2 metodi 
    # GetVehicleHistoryEvents (la storia precedente) 
    # e GetVehicleLastEvent



    exit()
    IdSegnalante = t.IdSegnalante
    risposta=[]
    risposta=get_response_from_provider(token, id_pc,  descrizione, id_manufatto, codvia, ncivico, colore, lettera)
    response = risposta[0]
    id_segnalazione = risposta [1]
    print(response.status_code)
    print(id_segnalazione)
    # print(response)
    if response.status_code == 200:
        # print('OK')
        return 200
    # ORA SI RICHIAMA IL WS


if __name__ == "__main__":
    main()