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
    take all the filed we need
    """
    for k in dictionary:
        # dictionary[k]["Timestamp"] = dictionary[k]["Data"] + dictionary[k]["Orario"]
        dictionary[k] = dictionary[k][
            ["Cod  ", "X", "Y", "Data", "Orario", "Indirizzo"]
        ]
        # al momento riempio con colonna vuota
        dictionary[k].insert(1, "cod_bracciale", [0, 0, 0], True)


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

    # Cod, cod_bracciale, X, Y, Data, Orario, Indirizzo
    takeInfo(dictDf)

    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    main()
