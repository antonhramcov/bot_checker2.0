import psycopg2
from psycopg2 import Error
from config import db_name, user, password, host, port

def find (s:str):
    try:
        connection = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()
        postgresql_select_query = "SELECT '{}' FROM leaks;".format(s)
        cursor.execute(postgresql_select_query)
        records = cursor.fetchall()
    except (Exception, Error) as error:
        return ("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            if records == None:
                return False
            else:
                return records

print(find('.mail'))