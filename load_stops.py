import logging
import time
from logging import basicConfig
from threading import Thread

import progressbar
from sqlalchemy.orm import sessionmaker

from api.api import TransAPI
from api.proxy import FileProxyManager, MosTransportBan
from db.db import engine
from models import Stop
from station import stops_coord
from utils import stops_list_to_queue


api = TransAPI(FileProxyManager(file_name='proxy.txt'))
session = sessionmaker(bind=engine)()
stops_list = list(stops_coord(f_name="data.csv"))
basicConfig(level=logging.DEBUG, filemode="a", filename="load_stops.log")
parsed_stops = 0
max_stops = len(stops_list)
queue = stops_list_to_queue(stops_list)


def parse_stop():
    global queue, session, parsed_stops
    while not queue.empty():
        coord = lon, lat = queue.get()
        stop = None
        while stop is None:
            try:
                stop = Stop.parse_obj(api.get_station_info(lon=lon, lat=lat))
            except MosTransportBan:
                api.change_ip()
            except:
                api.change_ip()
        parsed_stops += 1
        stop.save_stop(session, commit=False)
    return True


threads = []
N = 49
for i in range(N):
    t = Thread(name=f"{i}", target=parse_stop)
    t.start()
    threads.append(t)

bar = progressbar.ProgressBar(max_value=max_stops)
while parsed_stops < max_stops:
    bar.update(parsed_stops)
    time.sleep(1)
    if parsed_stops % 100 == 0:
        session.commit()

print("Commiting")
session.commit()

