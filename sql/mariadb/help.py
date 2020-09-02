
#!/usr/local/bin/python3

import requests
import queue
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import ujson
from datetime import datetime
import mysql.connector as mariadb
from mysql.connector import Error
from mysql.connector import errorcode
from threading import Thread
import time

num_threads = 4
threads = []
urls = queue.Queue()


def create_url():
    try:
        mariadb_connection = mariadb.connect(dbstuff)
        cursor = mariadb_connection.cursor()

        cursor.execute('SELECT type_id from tbl_items')
        item_list = cursor.fetchall()

        for row in item_list:
            url = 'https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=all&page=1&type_id=' + \
                str(row[0])
            urls.put(url)

        return urls

    except mariadb.Error as error:
        mariadb_connection.rollback()  # rollback if any exception occured
        print("Failed retrieving itemtypes from tbl_items table {}".format(error))

    finally:
        if mariadb_connection.is_connected():
            cursor.close()
            mariadb_connection.close()


def import_mo_jita(i, urls):
    station_id = 60003760

    print("worker:", i)

    try:
        mariadb_connection = mariadb.connect(dbstuff)
        cursor = mariadb_connection.cursor()

        while (True):
            url = urls.get()
            print("Worker %s processes %s queue# %s" % (i, url, urls.qsize()))
            if url == None:
                break
            s = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))
            jsonraw = s.get(url)
            jsondata = ujson.loads(jsonraw.text)

            for row in jsondata:
                if (row['location_id'] == station_id):
                    cursor.execute('INSERT INTO tbl_mo_jita_esi_tmp (order_id) VALUES (%s)', (row['order_id'], ))
                    mariadb_connection.commit()
                    cursor.execute('SELECT order_id, price, volume FROM tbl_mo_jita WHERE order_id = %s', (row['order_id'], ))
                    db_data = cursor.fetchall()
                    #print (db_data)
                    if len(db_data) != 0:
                        for x in db_data:
                            db_order_id = x[0]
                            db_price = x[1]
                            db_volume = x[2]

                    if len(db_data) != 0:
                        if db_price == row['price'] and db_volume == row['volume_remain']:
                            continue
                        else:
                            print("updating order#", row['order_id'])
                            cursor.execute('UPDATE tbl_mo_jita SET volume = %s, price = %s WHERE order_id = %s', (row['volume_remain'], row['price'], row['order_id'], ))
                            mariadb_connection.commit()
                    else:
                        print("newly inserting order#", row['order_id'])
                        cursor.execute('INSERT INTO tbl_mo_jita (type_id, order_id, ordertype,volume, price) VALUES (%s,%s,%s,%s,%s)', (row['type_id'], row['order_id'], row['is_buy_order'], row['volume_remain'], row['price'], ))
                        mariadb_connection.commit()
                else:
                    continue
            urls.task_done()

    except mariadb.Error as error:
        mariadb_connection.rollback()  # rollback if any exception occured
        print("Failed retrieving itemtypes from tbl_items table {}".format(error))

    finally:
        if mariadb_connection.is_connected():
            cursor.close()
            mariadb_connection.close()


def cleanup_mo():
    try:
        mariadb_connection = mariadb.connect(dbstuff)
        cursor = mariadb_connection.cursor()

        cursor.execute('SELECT order_id FROM tbl_mo_jita')
        list_mo_sql = cursor.fetchall()
        cursor.execute('SELECT order_id FROM tbl_mo_jita_esi_tmp')
        list_mo_esi = cursor.fetchall()
        list_mo_purge = list(set(list_mo_sql)-set(list_mo_esi))
        print(len(list_mo_purge))

        for row in list_mo_purge:
            cursor.execute('DELETE FROM tbl_mo_jita WHERE order_id = %s', ((row[0]), ))

        cursor.execute('TRUNCATE tbl_mo_jita_esi_tmp')
        mariadb_connection.commit()

    except mariadb.Error as error:
        mariadb_connection.rollback()  # rollback if any exception occured
        print("Failed retrieving itemtypes from tbl_items table {}".format(error))

    finally:
        if mariadb_connection.is_connected():
            cursor.close()
            mariadb_connection.close()


create_url()

for i in range(num_threads):
    urls.put(None)

for i in range(num_threads):
    worker = Thread(target=import_mo_jita, args=(i, urls,))
    worker.setDaemon(True)
    threads.append(worker)
    worker.start()


for worker in threads:
    worker.join()

cleanup_mo()


#I wrote a python script that imports market data into a MariaDB database. To speed up the import I decided to use the module threading. So at first a function populates a queue with urls from which data is downloaded and imported into my database. I have no problem if the scripts runs for the first time no matter how many threads are given, thus the available data is imported for the first time. When run again the stored data will be checked and updated if necessary. Else it will be ignored.

#Oddly I get an error message when the script runs with more than 1 thread and for the second time, where updating mechanics are involved.

#I struggling with this problem for over a week now and I help you can give me a hint to what could be the problem.
