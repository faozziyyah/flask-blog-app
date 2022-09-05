import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", 
    port="root",
    password="OPEyemi2001",
    )

my_cursor = mydb.cursor()

my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)