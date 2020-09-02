#!/bin/env python3

import pymysql

con = pymysql.connect('172.17.0.2', 'master', '2547561', 'mysql')

try:

        with con.cursor() as cur:

                    cur.execute('SELECT VERSION()')

                    version = cur.fetchone()

                    print(f'Database version: {version[0]}')

finally:

        con.close()
