# sistema_ambiente
Script python per Sistema Ambiente


Update giornaliero vista materializzata
------------------------------------------------------------------
- update_vm.py: script per l'update giornaliero della vista materializzata




Bot telegram
------------------------------------------------------------------
Il bot è stato creato con BotFather (inizialmente da Roberto Marzocchi, ma la proprietà pèuò essere cambiata)


[!bot_father](img/bot_father.PNG)

[!bot_father](./img/bot_father2.PNG)


Nome bot: @sistema_ambiente_percorsi



servono le librerie telepot e emoji che si possono installare con pip3

e.g.
```
sudo pip3 install telepot
```

Il bot telegram è sempre in ascolto. 
Parte all'avvio del server grazie allo script sh avvio_bot.sh che va personalizzato e che va messo in `/etc/init.d/`


Loggandosi come utente sudo  (`sudo su`)
1) fare un link degli script in /etc/init.d/ 
2) assegnare i permessi
3) impostare come script di avvio

```
ln -s $(pwd)/avvio_bot_sistema_ambiente.sh /etc/init.d/
chmod +x /etc/init.d/avvio_bot_sistema_ambiente.sh
update-rc.d avvio_bot_sistema_ambiente.sh defaults
touch crash.log
touch bot.pid
```

Il file *avvio_bot_sistema_ambiente.sh* di fatto lancia lo script *forever2.py* che effettua 2 operazioni:
- segnala ogni avvio o ripartenza dello script nel file *crash.log*
- salva il PID dell'ultimo processo partito nel file *bot.pid*

Conoscere il PID è utile perchè in questo modo il bot può essere modificato (script python) e riavviato manualmente tramite un *kill* del processo attivo:


```
cat bot.pid
```

```
sudo kill PID_NUMBER
```

Il bot si serve di un file credenziali.py che per ovvie ragioni non è caricato su un repository e che ha questo formato :

```
db='nome_db'
port=5432 # or different port
user='username'
pwd='password'
host='server_host or IP'


bot_token='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' #bot per notifiche file scaricati
chatID_lorenzo='XXXXXXXXX'

link='https://www.gishosting.gter.it/si_ambiente'
note_link= 'altro testo associato alla visualizzazione del link'

G_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```



sono stati impostati i seguenti comandi da Bot Father:

lista_percorsi_gialla - per visualizzare i percorsi della zona gialla
lista_percorsi_blu - per visualizzare i percorsi della zona gialla
lista_percorsi_rossa - per visualizzare i percorsi della zona gialla
webgis - link al webGIS ad accesso profilato di sistema Ambiente 
help - Aiuto

la seguente descrizione: 


Si tratta di un bot telegram ad uso interno del personale di Sistema Ambiente per visualizzare i percorsi su mappa. Il bot si appoggia al servizio in cloud https://www-gishosting.gter.it. 

Per maggiori informazioni sui percorsi è possibile scrivere a g.cascini@sistemaambientelucca.it, sul bot telegram a info@gter.it

Invia un testo qualunque (es. xx) per procedere e segui le istruzioni. 

e la seguente icona: 
[!percorsi_v.qgis](./img/percorsi_v.qgs.png)


così come tre tasti analoghi qualora non si usi un comando riconosciuto dal bot

Il bot è gestito dal comando **bot_multithread.py**
