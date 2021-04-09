# sistema_ambiente
Script python per Sistema Ambiente


Update giornaliero vista materializzata
------------------------------------------------------------------
- update_vm.py: script per l'update giornaliero della vista materializzata




Bot telegram
------------------------------------------------------------------
Il bot è stato creato con BotFather (inizialmente da Roberto Marzocchi, ma la proprietà pèuò essere cambiata)

Nome bot: @sistema_ambiente_percorsi



servono le librerie telepot e emoji che si possono installare con pip3

e.g.
```
sudo pip3 install telepot
```

Il bot telegram è sempre in ascolto. 
Parte all'avvio del server grazie allo script sh avvio_bot.sh che va personalizzato e che va messo in `/etc/init.d/`


Loggandosi come utente sudo 
1) fare un link degli script in /etc/init.d/ 
2) assegnare i permessi
3) impostare come script di avvio

```
ln -s $(pwd)/avvio_bot.sh /etc/init.d/
chmod +x /etc/init.d/avvio_bot_sistema_ambiente.sh
update-rc.d avvio_bot_sistema_ambiente.sh defaults
```

Il bot si serve di un file credenziali.py che per ovvie ragioni non è caricato suò repository e che ha questo formato :

```
db='nome_db'
port=5432 # or different port
user='username'
pwd='password'
host='server_host or IP'


bot_token='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' #bot per notifiche file scaricati
chatID_lorenzo='XXXXXXXXX'

link='https://www.gishosting.gter.it/si_ambiente'
```


sono stati impostati 3 comandi:
\telegram_id

\webgis

\stato_stazioni

così come tre tasti analoghi qualora non si usi un comando riconosciuto dal bot

Il bot è gestito dal comando **bot_multithread.py**