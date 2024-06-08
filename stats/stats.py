from uncoup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
from uncoup2pouce.users import Users
from announces.announce import Announce
from announces.review import Review

class Stats:

    mySQLCo = None
    
    def __init__(self):
        self.mySQLCo = MySQLConnectionSingleton()

    def get_max_rows_for_stats(self, stats, statName, query, maxInd, cols):
        empty_tuple = tuple()
        db_rows = self.mySQLCo.execute_prepared_query(query, empty_tuple, True)
        stats[statName] = 0
        count = 0
        max = 0
        for row in db_rows:
            if count == 0:
                stats[statName] = dict()
                max = row[maxInd]
            
            if row[maxInd] < max:
                break

            stats[statName][count] = {col: val for col, val in zip(cols, row)}
            count += 1

    def get_stats(self):
        
        stats = dict()
        empty_tuple = tuple()

        nb_users_query = "SELECT count(idUser) FROM users"
        stats["nb_users"] = self.mySQLCo.execute_prepared_query(nb_users_query, empty_tuple, True)[0][0]
        
        nb_announces_query = "SELECT count(idAnnounce), typeAnnounce FROM announce WHERE valid = 1 GROUP BY (typeAnnounce) ORDER BY typeAnnounce"
        results = self.mySQLCo.execute_prepared_query(nb_announces_query, empty_tuple, True)
        stats["nb_announces"] = dict()
        stats["nb_announces"]["total"] = 0
        stats["nb_announces"]["type1"] = 0
        stats["nb_announces"]["type2"] = 0
        counter = 1
        if len(results)>0:
            for row in results:
                stats["nb_announces"]["total"] += row[0]
                stats["nb_announces"][f"type{counter}"] = row[0]
                counter += 1

        nb_reviews_query = "SELECT count(idReview) FROM review INNER JOIN users USING (idUser) WHERE privilegeLevel > 0"
        stats["nb_reviews"] = self.mySQLCo.execute_prepared_query(nb_reviews_query, empty_tuple, True)[0][0]

        best_announce_query = "SELECT idAnnounce, intitule, avg(score) FROM announce INNER JOIN users ON (announce.idUser = users.idUser) INNER JOIN review USING (idAnnounce) WHERE valid = 1 AND privilegeLevel > 0 GROUP BY (idAnnounce) ORDER BY avg(score) DESC LIMIT 10"
        best_announce_db = self.mySQLCo.execute_prepared_query(best_announce_query, empty_tuple, True)
        stats["best_announces"] = dict()
        for announce in best_announce_db:
            stats["best_announces"][announce[0]] = {'idAnnounce':announce[0], 'intitule':announce[1], 'score':announce[2]}
        
        users_with_most_announces_query = "SELECT idUser, username, lastname, firstname, count(idAnnounce) nb_announces FROM announce INNER JOIN users USING (idUser) WHERE privilegeLevel > 0 AND valid = 1 GROUP BY (idUser) ORDER BY nb_announces DESC"
        self.get_max_rows_for_stats(stats, "users_with_most_announces", users_with_most_announces_query, 4, ["idUser", "username", "lastname", "firstname", "nb_announces"])

        users_with_most_comments_query = "SELECT idUser, username, lastname, firstname, count(idReview) nb_reviews FROM review INNER JOIN users USING (idUser) WHERE privilegeLevel > 0 GROUP BY (idUser) ORDER BY nb_reviews DESC"
        self.get_max_rows_for_stats(stats, "users_with_most_comments", users_with_most_comments_query, 4, ["idUser", "username", "lastname", "firstname", "nb_reviews"])

        return stats