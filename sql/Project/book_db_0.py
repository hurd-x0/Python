#!/bin/env python3

import mysql.connector as mariadb
from mysql.connector import Error


try:

	connection = mariadb.connect(
					host="172.17.0.2", 
					user="master", 
					password="2547561", 
					database="py_test_db_0")

	if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to Mariadb Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to Mariadb", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("Mariadb connection is closed")




