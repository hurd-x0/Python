#!/usr/bin/python

import pymysql

con = pymysql.connect('localhost', 'user7',
            's$cret', 'testdb')

try:

        with con.cursor() as cur:

                    cur.execute('SELECT VERSION()')

                            version = cur.fetchone()

                                    print(f'Database version: {version[0]}')

finally:

        con.close()

print "give me a bottle of rum!"
