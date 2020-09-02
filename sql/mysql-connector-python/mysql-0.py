#!/bin/env python3.8

import mariadb import sys
from mariadb import Error

try:
    connection = mariadb.connect(host='172.17.0.2',
                                         user='master',
                                         password='2547561')
    
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to Mariadb Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("create database db ;")
        cursor.execute("select database(db);")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("Mariadb connection is closed")

