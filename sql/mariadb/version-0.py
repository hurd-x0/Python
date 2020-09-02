#!/bin/env python3

import mariadb

con = mariadb.connect(
	host="172.17.0.2", 
	user="master", 
	password="2547561", 
	database="mysql"
)

try:
        with con.cursor() as cur:

                    cur.execute('SELECT VERSION()')

                    version = cur.fetchone()

                    print(f'Database version: {version[0]}')

finally:

        con.close()
