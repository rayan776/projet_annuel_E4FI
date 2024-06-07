import mysql.connector

class MySQLConnectionSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(MySQLConnectionSingleton, cls).__new__(cls)
            cls._instance.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='esiee'
            )
        return cls._instance

    def execute_prepared_query(self, query, values, isSelect):
        result = []
        try:
            cursor = self.connection.cursor(prepared=True)
            cursor.execute(query,values)
            if not isSelect:
                self.connection.commit()
            if cursor.with_rows:
                result = cursor.fetchall()
        except Exception as e:
            result = [e]
        finally:
            cursor.close()
            
        return result