from uncoup2pouce import security
from uncoup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton

class LoginCheck:
    username = ""
    pwd = ""

    def __init__(self, username, pwd):
        self.username = username
        self.pwd = security.hashStrToSha512(pwd)
    
    def checkCredentials(self):
        mySQLInstance = MySQLConnectionSingleton()
        query_result = mySQLInstance.execute_prepared_query(f"SELECT * FROM users WHERE username = %s AND password = %s", (self.username, self.pwd), True)
        
        return len(query_result) == 1
