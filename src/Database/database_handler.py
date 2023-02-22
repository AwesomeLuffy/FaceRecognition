import mysql.connector as mc


class DatabaseHandler:
    ConnectionData = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "test",
        "database": "data_faces",
    }

    # Return a connection to the database but not close it
    @staticmethod
    def get_conn():
        return mc.connect(**DatabaseHandler.ConnectionData)

    # Query to do insert query
    # In case of no fetch, return -1
    # In case of MySQL error return -2
    # In case of other error return -3
    @staticmethod
    def insert_query(sql: str, val: list[tuple] | tuple) -> int:
        conn = DatabaseHandler.get_conn()
        cursor = conn.cursor()
        try:
            if type(val) is list:
                cursor.executemany(sql, val)
            elif type(val) is tuple:
                cursor.execute(sql, val)
            conn.commit()

            return cursor.rowcount
        except mc.errors.Error as e:
            print(e)
            return -2
        except Exception as e:
            print(e)
            return -3
        finally:
            cursor.close()
            conn.close()

    # Method to check if value exists in a table
    # Connexion can be passed as parameter to not open another one
    # (will not be closed after, the method will act as subquery)
    @staticmethod
    def check_value_exists(table_name: str, column_name: str, value: tuple, connexion=None):
        conn = connexion if connexion is not None else DatabaseHandler.get_conn()
        cursor = conn.cursor()
        SQL_RAW_QUERY = f"SELECT {column_name} FROM {table_name} WHERE {column_name} = %s"
        try:
            cursor.execute(SQL_RAW_QUERY, value)

            return len(cursor.fetchall()) > 0
        except Exception as e:
            print(e)
            return True
        finally:
            cursor.close()
            if connexion is None:
                conn.close()

    @staticmethod
    def read_values(sql: str, where=None) -> list[tuple]:
        conn = DatabaseHandler.get_conn()
        cursor = conn.cursor()
        try:
            if where is not None:
                cursor.execute(sql, where)
            else:
                cursor.execute(sql)

            return cursor.fetchall()
        except Exception as e:
            print(e)
            return []
        finally:
            cursor.close()
            conn.close()
