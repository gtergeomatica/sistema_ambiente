
#import shapely
import psycopg2
import pandas as pd
import openrouteservice as ors

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir1 = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir1)
sys.path.append(parentdir2)
from credenziali import db, port, user, pwd, host, ors_token

import logging
path=os.path.realpath(__file__).replace('ors_caller.py', '')
logfile='{}/log/ors_caller.log'.format(parentdir2)


logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode='a', # overwrite or append
    filename=logfile,
    #level=logging.INFO)
    level=logging.DEBUG)


logging.info('Connessione al db')
try:
    conn = psycopg2.connect(dbname=db,
                    port=port,
                    user=user,
                    password=pwd,
                    host=host)
    curr = conn.cursor()
    conn.autocommit = True
except:
    logging.error('connessione al db fallita ')
    logging.exception('')
    os._exit(1)   




#load data, setting arbitrary amount for every point (1 in this case), view of the df
#deliveries_data = pd.read_csv(r'path\to\the\file\punti_rm.csv')
select_query= ''' select * from anagrafiche.pannoloni_to_ors limit 10'''

try:
	#curr.execute(select_query)
	#conn.commit()
    deliveries_data =  pd.read_sql_query(select_query, conn)
    conn = None
    logging.debug(''' Retrieved information''')
except:
    logging.error('Query fallita')
    logging.exception('')
    os._exit(1) 


# needed amount potrebbe essere calcolato nella vista  e per indicare il numero di richieste per indirizzo



#depot = [41.8719643, 12.4737054] 
depot = [43.85263337200871, 10.505420932726183] #borgo giannotti


# vehicles start/end address: random point in Rome (depot = [41.8719643, 12.4737054])
# vehicle capacity: 300 (arbitrary)
# vehicle operational times: 08:00 - 20:00
# service location: delivery location -> pick up in my case!
# service time windows: individual delivery location's time window
# service amount: individual delivery location's needs



# trovare il modo di definire le timewindow (6-12) /(12-18)
# aggiungere conversione da timestamp a POSIX timestamp
vehicles = list()
for idx in range(3): #3 is max
    vehicles.append(
        ors.optimization.Vehicle(
            id=idx, 
            start=list(reversed(depot)),
            #end=list(reversed(depot)),
            capacity=[300],
            time_window=[1553241600, 1553284800]  # Fri 8-20:00, expressed in POSIX timestamp
        )
    )

deliveries = []
#open_from= "2019-03-22 08:00:00" ??? - not necessary

for delivery in deliveries_data.itertuples():
    deliveries.append(
        ors.optimization.Job(
            id=delivery.Index,
            location=[delivery.x, delivery.y],
            service=60,    #120,  # Assume 2 minutes at each site
            amount=[delivery.amount],
            #time_windows=[[
            #    int(delivery.Open_From.timestamp()),  # VROOM expects UNIX timestamp
            #    int(delivery.Open_To.timestamp())
            #]]
        )
    )
#Now the analysis
ors_client = ors.Client(key=ors_token)  # Get an API key from https://openrouteservice.org/dev/#/signup
result = ors_client.optimization(
    jobs=deliveries,
    vehicles=vehicles,
    geometry=True
    
)
#'Request parameters exceed the server configuration limits. Only a total of 3500 routes are allowed.'
#500 ({'code': 3, 'error': 'Request parameters exceed the server configuration limits. The specified number of waypoints must not be greater than 50.'})


# Only extract relevant fields from the response
extract_fields = ['distance', 'amount', 'duration']
data = [{key: route[key] for key in extract_fields} for route in result['routes']]

vehicles_df = pd.DataFrame(data)
vehicles_df.index.name = 'vehicle'


# Create a list to display the schedule for all vehicles
stations = list()
for route in result['routes']:
    vehicle = list()
    for step in route["steps"]:
        vehicle.append(
            [
                step.get("job", "Depot"),  # Station ID
                step["arrival"],  # Arrival time
                step["arrival"] + step.get("service", 0),  # Departure time
                
            ]
        )
    stations.append(vehicle)


#Now we can look at each individual vehicle's timetable,
# for example for vehicle 0 (the same can be done for other 2 vehicles)
df_stations_0 = pd.DataFrame(stations[0], columns=["Station ID", "Arrival", "Departure"])
df_stations_0['Arrival'] = pd.to_datetime(df_stations_0['Arrival'], unit='s')
df_stations_0['Departure'] = pd.to_datetime(df_stations_0['Departure'], unit='s')
