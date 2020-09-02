#!/bin/env python3

import mariadb

mydb = mariadb.connect(
  host="172.17.0.2",
  user="master",
  password="2547561"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x) 
