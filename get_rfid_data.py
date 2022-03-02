#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Script per la sincronizzazione giornaliera
dei dati dei tag rfid dei cestini


"""

from ftplib import FTP, error_perm
import os
import sys
import shutil
import re
import glob
import getopt
from datetime import datetime, timedelta
import psycopg2
import logging
import pandas as pd
import pathlib
from io import BytesIO

from sqlalchemy import create_engine, text
from credenziali import *


def initLogger():
    """
    define log file as simple as possibile
    """

    spath = os.path.dirname(os.path.realpath(__file__))

    logging.basicConfig(
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        filemode="a",  # overwrite or append
        filename=f"{spath}/log/get_rfid.log",
        level=logging.INFO,
    )
    logging.info("*" * 20 + "NUOVA ESECUZIONE" + "*" * 20)


def connectToFtp(host, username, password):
    """
    connect to ftp area
    """

    try:
        #with FTP(host, username, password) as ftp:
        ftp = FTP(host, username, password)
        dir_list = []
        ftp.dir(dir_list.append)
        logging.info(f"lista di file presenti su area ftp {dir_list}")
            
        return ftp

    except:
        logging.error("Connessione ad area ftp non riuscita")
        logging.exception("")
        os._exit(1)


def getCsvFileList(ftp):
    """
    list only the csv files in the folder of the ftp area
    """

    files = []

    try:
        files = ftp.nlst()
    except error_perm as resp:
        if str(resp) == "550 No files found":
            logging.error("No files in this directory")
        else:
            raise

    for file in files:
        if pathlib.Path(file).suffix != ".csv":
            files.remove(file)

    return files


def checkFileisInDB(listOfFile, cur, ftp ):
    """
    check if the csv file name is in the db cestini.storicoFile (so it checks if this filename has been already parsed)
    check if the time of parsing - now > 7 days in order to clean the ftp area
    """

    sql = "SELECT EXISTS (SELECT nome_file FROM  cestini.storicoFile WHERE nome_file = %s)"

    sql2 = "SELECT data_caricamento FROM  cestini.storicoFile WHERE nome_file = %s"
    
    for d in listOfFile:
        try:

            cur.execute(sql, (d,)) 
            boolValue = cur.fetchone()[0]

            if not boolValue:
                continue

            listOfFile.remove(d) 
            logging.info(f"il file {d} è già presente nel Db e non verrà parsato")
            
            cur.execute(sql2, (d,)) 
            dateParse = cur.fetchone()[0]
            a = datetime.now()-dateParse
            
            if ( (datetime.now()-dateParse) < timedelta (days=7)):
                continue
           
            #ftp.delete(d)   #decommentare per eliminare i file.
            logging.info(f"il file {d} è stato parsato {dateParse} ed è stato appena eliminato dall'area ftp")

        except:
            logging.error("Sql command fail on sendFileToTableStorico function")
            logging.exception("")
            os._exit(1)


def filesGrabber(listFile, ftp):
    """
    return a dict with name of the csv file as key and pd.dataframe with content of the csv file as value
    """

    dicts = {}
    for file in listFile:

        r = BytesIO()
        ftp.retrbinary(f"RETR {file}", r.write)

        r.seek(0)
        df = pd.read_csv(r, delimiter="|", encoding='latin-1')

        dicts[file] = df

    logging.info(f"lista di file parsati nello script {[(k) for k in dicts]}")
    return dicts


def takeInfo(dictionary):
    """
    take all the filed we need: cod, cod_bracciale, x, y, data, orario, indirizzo
    """

    for k in dictionary:
        dictionary[k] = dictionary[k][
            ["cod_cestino", "cod_bracciale", "x", "y", "data", "orario","indirizzo"]
        ]

        try:
          # change the "," with "." in X and Y
          dictionary[k]["x"] = dictionary[k]["x"].apply(lambda x: x.replace(",", ".", 1))
          dictionary[k]["y"] = dictionary[k]["y"].apply(lambda x: x.replace(",", ".", 1))
        except:
            logging.warning('Il parsing delle coordinate non è andato a buon fine.')


def sqlStatement():
    """
    return a list with the queries, at the moment the only queries are the creation of table
    """

    tableCreateSql = """ CREATE TABLE IF NOT EXISTS cestini.bracciali (
                     id serial primary key,
                    "cod_cestino" varchar ,
                    "cod_bracciale" varchar,
                    "x" DOUBLE PRECISION,
                    "y" DOUBLE PRECISION,
                    "data" varchar,
                    "orario" varchar,
                    "indirizzo" varchar
                    )
                    """

    tableCreateStoricoFileSql = """ CREATE TABLE IF NOT EXISTS cestini.storicoFile (
                     --id serial primary key,
                    "nome_file" varchar,
                    "data_caricamento" timestamp NOT NULL DEFAULT NOW()
                    )
                    """

    # truncatSql = '''TRUNCATE TABLE cestini.bracciali'''

    # sqlList = [ tableCreateSql,  truncatSql ]
    sqlList = [tableCreateSql, tableCreateStoricoFileSql]

    return sqlList


def initDbConnection():
    """
    set up for the connection
    """
    try: 
        logging.info("Connessione al db")
        conn = psycopg2.connect(dbname=db, port=port, user=user, password=pwd, host=host)

        cur = conn.cursor()
        conn.autocommit = True

        return cur, conn

    except:
        logging.error("Connessione al DB non riuscita")
        logging.exception("")
        os._exit(1)


def executeSqlQuery(cur, sqlQueryList):
    """
    it executes the queries
    """

    for idx, s in enumerate(sqlQueryList):

        # logging.info(s)
        """
        if s.startswith('COPY'):

            try:
                cur.copy_expert(s, open(filename, "r", encoding="latin_1"))
            except:
                logging.error('Sql COPY command fail')
                logging.exception('')
                os._exit(1)
        """

        try:
            cur.execute(s)
            logging.info(f"esecuzione query nr {idx+1} di sqlQuery")
        except:
            logging.error("Sql command fail on executeSqlQuery function")
            logging.exception("")
            os._exit(1)


def sendDataToDb(dictionary, cur):
    """
    #send data to DB in the table cestini.bracciali and store the file name of the csv file in another table called storicoFile
    create temporary table and upload DataFrame  and merge temp_table into main_table (cestini.bracciali) to upsert
    """
    
    for k in dictionary:
        # connString = 'postgres://{}:{}@{}/{}'.format(user, pwd, host, db )
        connString = f"postgres://{user}:{pwd}@{host}/{db}"
        engine = create_engine(connString)
        connection = engine.connect()
        
        try:
            # step 1 - create temporary table 
            connection.execute(
                text('''CREATE TEMPORARY TABLE temp_table (
                        --id serial primary key,
                        "cod_cestino" varchar ,
                        "cod_bracciale" varchar,
                        "x" DOUBLE PRECISION,
                        "y" DOUBLE PRECISION,
                        "data" varchar,
                        "orario" varchar,
                        "indirizzo" varchar);'''
                )
            )

            # step 2 - upload DataFrame
            # df.to_sql('bracciali', con=connection, schema='cestini', if_exists='append', index=False)
            dictionary[k].to_sql(
                "temp_table",
                con=connection,
                #schema="cestini",
                if_exists="append",
                index=False,
            )

            # step 3 - merge temp_table into cestini.bracciali

            connection.execute(
                text('''INSERT INTO cestini.bracciali (cod_cestino,
                                                cod_bracciale,
                                                x,
                                                y,
                                                data,
                                                orario,
                                                indirizzo) 
                        SELECT * FROM temp_table
                        ON CONFLICT ON CONSTRAINT bracciali_unique
                        DO NOTHING; '''
                )
            )

            logging.info(f"dati inseriti per {k}")

            sendSingleFileToTableStorico(k, cur)
        except:
            logging.error("Sql command fail")
            logging.exception("")
            os._exit(1)


def sendSingleFileToTableStorico(file, cur):
    """
    insert name of the csv file in table stroricoFile
    """

    sql = "INSERT INTO cestini.storicoFile(nome_file) VALUES(%s)"

    try:
        cur.execute(sql, (file,))
        logging.info(f"nome del file: {file}, inserito in cestini.storicoFile in data {datetime.now()}")
    except:
        logging.error("Sql command fail on sendFileToTableStorico function")
        logging.exception("")
        os._exit(1)


def quitConncetion(cur, conn):
    """
    close connection with db
    """

    if (cur is not None) or (conn is not None):
        cur.close()
        conn.close()
        logging.info(f"chiusura connessioni al db")


def main():

    initLogger()

    ftp = connectToFtp(ftp_host_g, ftp_user_g_01, ftp_pwd_g_01)

    cur, conn = initDbConnection()

    sqlQuery = sqlStatement()

    executeSqlQuery(cur, sqlQuery)

    fileList = getCsvFileList(ftp)

    checkFileisInDB(fileList, cur, ftp)

    dictDf = filesGrabber(fileList, ftp)
    
    ftp.quit()

    takeInfo(dictDf)

    sendDataToDb(dictDf, cur)

    quitConncetion(cur, conn)

    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    
    main()