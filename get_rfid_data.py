#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Script per la sincronizzazione giornaliera
dei dati dei tag rfid dei cestini


"""

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
import pathlib
from io import BytesIO, StringIO


from sqlalchemy import create_engine
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


def getCsvFileList(ftp):
    """
    list of csv file in the folder
    """

    files = []

    try:
        files = ftp.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            logging.error("No files in this directory")
        else:
            raise

    for file in files:
        if pathlib.Path(file).suffix != ".csv":
            files.remove(file)

    return files


def filesGrabber(listFile, ftp):
    """
    return a dict with name of the csv file as key and pd.dataframe as value
    """

    dicts = {}
    for file in listFile:

        r = BytesIO()
        ftp.retrbinary(f"RETR {file}", r.write)

        r.seek(0)
        df = pd.read_csv(r, delimiter="|")

        dicts[file] = df

    return dicts


def takeInfo(dictionary):
    """
    take all the filed we need: cod, cod_bracciale, x, y, data, orario, indirizzo
    """
    for k in dictionary:
        # dictionary[k]["Timestamp"] = dictionary[k]["Data"] + dictionary[k]["Orario"]
        dictionary[k] = dictionary[k][
            ["Cod  ", "X", "Y", "Data", "Orario", "Indirizzo"]
        ]

        # al momento riempio con colonna vuota
        dictionary[k].insert(1, "cod_bracciale", [0, 0, 0], True)

        # correzione
        dictionary[k].rename(
            columns={
                "Cod  ": "cod",
                "X": "x",
                "Y": "y",
                "Data": "data",
                "Orario": "orario",
                "Indirizzo": "indirizzo",
            },
            inplace=True,
        )

        # change the "," with "." in X and Y
        dictionary[k]["x"] = dictionary[k]["x"].apply(lambda x: x.replace(",", ".", 1))
        dictionary[k]["y"] = dictionary[k]["y"].apply(lambda x: x.replace(",", ".", 1))


def sqlStatement():
    """
    return a list with the queries
    """

    tableCreateSql = """ CREATE TABLE IF NOT EXISTS cestini.bracciali (
                     --id serial primary key,
                    "cod" varchar primary key,
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

    logging.info("Connessione al db")
    conn = psycopg2.connect(dbname=db, port=port, user=user, password=pwd, host=host)

    cur = conn.cursor()
    conn.autocommit = True

    return cur, conn


def executeSqlQuery(cur, sqlQueryList):
    """
    it executes the queries one create the table if it does not exist, the other clean the table from existing data
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


def sendDataToDb(dictionary):
    """
    send data to DB
    """

    for k in dictionary:
        # connString = 'postgres://{}:{}@{}/{}'.format(user, pwd, host, db )
        connString = f"postgres://{user}:{pwd}@{host}/{db}"
        engine = create_engine(connString)
        connection = engine.connect()

        try:
            # df.to_sql('anag_garbage', con=connection, schema='anagrafiche2', if_exists='append', index=False)
            # df.to_sql('bracciali', con=connection, schema='cestini', if_exists='append', index=False)
            dictionary[k].to_sql(
                "bracciali",
                con=connection,
                schema="cestini",
                if_exists="append",
                index=False,
            )
            logging.info(f"dati inseriti per {k}")
        except:
            logging.error("Sql command fail")
            logging.exception("")
            os._exit(1)


def sendFileToTableStorico(listOfFile, cur):
    """
    insert in already created table
    """

    sql = "INSERT INTO cestini.storicoFile(nome_file) VALUES(%s)"

    for d in listOfFile:
        try:

            cur.execute(sql, (d,))
            logging.info(f"nome del file: {d}, inserito in DB in data {datetime.now()}")
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

    try:
        with FTP(ftp_host_g, ftp_user_g_01, ftp_pwd_g_01) as ftp:

            dir_list = []
            ftp.dir(dir_list.append)
            logging.info(f"lista di file presenti su area ftp {dir_list}")

            fileList = getCsvFileList(ftp)
            dictDf = filesGrabber(fileList, ftp)

            ftp.quit()
            logging.info(f"lista di file parsati nello script {[(k) for k in dictDf]}")

    except:
        logging.error("Trasferimento non riuscito")
        logging.exception("")
        os._exit(1)

    takeInfo(dictDf)

    sqlQuery = sqlStatement()

    cur, conn = initDbConnection()

    executeSqlQuery(cur, sqlQuery)

    sendDataToDb(dictDf)

    sendFileToTableStorico(fileList, cur)

    quitConncetion(cur, conn)

    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    main()
