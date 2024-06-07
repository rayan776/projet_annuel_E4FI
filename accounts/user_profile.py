from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
from project_1coup2pouce.users import Users

class UserProfile:

    mySQLCo = None
    users = None

    def __init__(self):
        self.mySQLCo = MySQLConnectionSingleton()
        self.users = Users()

    def get_infos_for_user_profile_template(self, idTargetUser, idActualUser):
        infos_dict = dict()

        # infos:
        # nom, prénom, login, date d'inscription, niveau de privilège, score, est ce qu'il a bloqué l'utilisateur qui voit la page (si connecté)

        get_user_infos_query = f"SELECT idUser, lastname, firstname, dateRegister, privilegeLevel, username FROM users WHERE idUser = %s"
        values = []
        values.append(idTargetUser)
        values = tuple(values)
        results = self.mySQLCo.execute_prepared_query(get_user_infos_query, values, True)

        if len(results) == 1:
            infos_dict["user_found"] = True
            infos_dict["idUser"] = results[0][0]
            infos_dict["lastname"] = results[0][1]
            infos_dict["firstname"] = results[0][2]
            infos_dict["date_register"] = results[0][3]
            infos_dict["privilege_level"] = results[0][4]
            if results[0][4] == 0:
                infos_dict["role"] = "Banni"
                infos_dict["username_color"] = "red"
            elif results[0][4] == 1:
                infos_dict["role"] = "Utilisateur"
            elif results[0][4] == 2:
                infos_dict["role"] = "Administrateur"
                infos_dict["username_color"] = "#0958f4"
                
            infos_dict["username"] = results[0][5]
            infos_dict["score"] = self.users.get_score(idTargetUser)
            infos_dict["blocked"] = self.users.has_user1_blocked_user2(idActualUser, idTargetUser)
            if idActualUser > 0:
                infos_dict["has_blocked_current_user"] = self.users.has_user1_blocked_user2(idTargetUser, idActualUser)
            infos_dict["nb_announces"] = self.mySQLCo.execute_prepared_query(f"SELECT count(idAnnounce) FROM announce WHERE idUser = %s AND valid = 1", values, True)[0][0]
            infos_dict["nb_comments"] = self.mySQLCo.execute_prepared_query(f"SELECT count(idReview) FROM review INNER JOIN announce USING (idAnnounce) WHERE valid = 1 AND review.idUser = %s", values, True)[0][0]
            if idActualUser == idTargetUser:
                infos_dict["blocked_list"] = self.users.get_blocked_list(idActualUser)
        else:
            infos_dict["user_found"] = False

        return infos_dict