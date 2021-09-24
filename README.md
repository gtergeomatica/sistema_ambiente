# sistema_ambiente
Script python per Sistema Ambiente


Update giornaliero vista materializzata
------------------------------------------------------------------
- update_vm.py: script per l'update giornaliero della vista materializzata 


Elaborazione dei dati OSM per il calcolo  dei percorsi con pg routing
------------------------------------------------------------------
- osm_downloader.py: script per il download deli dati osm con tag 'highway'
- osm2db.py: script per l'upload dei dati osm sul db postgres


Bot telegram
------------------------------------------------------------------
Il bot è stato creato con BotFather


![bot_father](https://user-images.githubusercontent.com/4061154/115054392-7522a600-9ee0-11eb-8866-4db76c5ea96d.PNG)


![bot_father2](https://user-images.githubusercontent.com/4061154/115054558-a307ea80-9ee0-11eb-8c1f-ddd4b1095d12.PNG)




Nome bot: @sistema_ambiente_percorsi 
Alias: SIU Sistema Ambiente
 



In una prima versione del bot ( gestita dal comano **bot_multithread_sistema_ambiente.py**) servivano le librerie telepot e emoji (installabili con pip3)
(telepot non supporta gli ultimi sviluppi per cui meglio usare il seguente fork)

e.g.
```
sudo pip3 install git+https://github.com/MoumenKhadr/telepot.git --upgrade
```

Nella versione attualmente supportata del bot (**bot_multithread_sistema_ambiente_v2.py**) la libreria telepot è stata sostituita con la libreria aiogram (https://github.com/aiogram/aiogram) e ciene lanciata con python 3.9.


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

start - Avvia il Bot per la prima volta
help -  Scopri le funzionalità del Bot
telegram_id - Ottieni il codice da comunicare per abilitare il bot su questo dispositivo
servizio - Visualizza gli incarichi assegnati
assistenti - Visualizza il nome degli assistenti in turno
reset - Termina un precedente comando

la seguente descrizione: 


Bot telegram ad uso interno del personale di Sistema Ambiente  Spa (Lucca)  configurato per inviare indicazioni sui servizi assegnati e per visualizzare i percorsi su mappa. Il bot si appoggia al servizio in cloud https://www-gishosting.gter.it. 
I contenuti sono accessibili ai soli utenti abilitati. 


Per maggiori informazioni su abilitazione, percorsi e servizi assegnati scrivere a g.cascini@sistemaambientelucca.it, sul bot telegram a info@gter.it

il seguente 'about':

Bot telegram ad uso del personale interno di Sistema Ambiente Spa (Lucca)


e la seguente icona: --DA MODIFICARE


![percorsi_v qgs](https://user-images.githubusercontent.com/4061154/115054574-a8653500-9ee0-11eb-95fc-6764019254dd.png  {width=150px height=150px})



Ecco l'anteprima del bot 

![image](https://user-images.githubusercontent.com/4061154/115054627-bc109b80-9ee0-11eb-9caf-c1ca2f5b01b7.png)


