from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton

def get_latest_announces(limit):
    query = f"SELECT idAnnounce, intitule FROM announce ORDER BY dateAnnounce DESC LIMIT %s"
    values = (limit,)
    mysqlCo = MySQLConnectionSingleton()
    rows = mysqlCo.execute_prepared_query(query, values, True)
    return [{'idAnnounce':row[0], 'intitule':row[1]} for row in rows]

