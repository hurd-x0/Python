
__author__ = 'hurd_x0'

import pymysql

#  database connection
db = pymysql.connect("172.17.0.2", "master", "2547561", )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# Drop table if it already exist using execute() method.
cursor.execute("DROP TABLE IF EXISTS PERSON")

# Create table as per requirement
sql = """CREATE TABLE PERSON (
   ID INT NOT NULL,
   FIRST_NAME  CHAR(20) NOT NULL,
   LAST_NAME  CHAR(20),
   AGE INT,
   SEX CHAR(1),
   PRIMARY KEY (ID) )"""

cursor.execute(sql)

# disconnect from server
db.close()
