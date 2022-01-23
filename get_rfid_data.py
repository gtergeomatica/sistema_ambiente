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
import csv
import pathlib

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


def getFileList(ftp):
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
    return files


def csvGrabber(listFile, ftp):
    """
    download files from ftp folder to actual folder if they are csv
    """
    for file in listFile:
        with open(file, "wb") as downloadedFile:
            ftp.retrbinary(f"RETR {file}", downloadedFile.write)
            logging.info(f"{file} è stato scaricato")

        downloadedFile.close()


def parser():
    pass


def main():
    initLogger()
    try:
        with FTP(ftp_host_g, ftp_user_g_01, ftp_pwd_g_01) as ftp:

            dir_list = []
            ftp.dir(dir_list.append)
            logging.info(f"lista di file presenti {dir_list}")

            fileList = getFileList(ftp)

            filename = "letture_bracciale.csv"
            csvGrabber(fileList, ftp)

            ftp.quit()

    except:
        logging.error("Trasferimento non riuscito")
        logging.exception("")
        os._exit(1)

    logging.info("*" * 20 + "FINE ESECUZIONE" + "*" * 20)


if __name__ == "__main__":
    main()
