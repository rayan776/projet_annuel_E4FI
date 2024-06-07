from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
import project_1coup2pouce.security as security
import ast

class Users:

    mySQLconnection = ""

    def __init__(self):
        self.mySQLconnection = MySQLConnectionSingleton()

    def logout(self, request, context):
        request.session.flush()
        request.session['logged_user'] = False
        context["isConnected"] = False

    def login(self, request, context):
        request.session['logged_user'] = True
        results = self.mySQLconnection.execute_prepared_query(f"SELECT idUser, username FROM users WHERE username = %s", (request.POST.get("username"),),True)
        request.session["idUser"] = results[0][0]
        request.session['login'] = results[0][1]
        context["login"] = results[0][1]
        context["isConnected"] = True
        self.getInitiales(request, context)
    
    def getPrivilegeLevel(self, request, username):
        if request.session.get("logged_user", False):
            result = self.mySQLconnection.execute_prepared_query(f"SELECT privilegeLevel FROM users WHERE username = %s", (username,),True)
            return result[0][0]
        else:
            return ""
        
    def getLevel(self, request, username):
        role = self.getPrivilegeLevel(request, username)
        if role == 0:
            return "banned"
        elif role == 2:
            return "admin"
        elif role == 1:
            return "normal"
        else:
            return ""
    
    def getInitiales(self, request, context):
        if request.session.get("logged_user", False):
            result = self.mySQLconnection.execute_prepared_query(f"SELECT CONCAT(SUBSTRING(lastname, 1, 1), SUBSTRING(firstname, 1, 1)) AS initials FROM users WHERE username = %s", (request.session["login"],), True)
            if len(result) == 1:
                request.session["initiales"] = result[0][0]
                context["initiales"] = result[0][0]
    
    def get_user_id(self, username):
        result = self.mySQLconnection.execute_prepared_query(f"SELECT idUser FROM users WHERE username = %s", (username,), True)
        if len(result)==1:
            return result[0][0]
        else:
            return -1
    
    def get_username_and_name(self, idUser):
        result = self.mySQLconnection.execute_prepared_query(f"SELECT username, lastname, firstname FROM users WHERE idUser = %s", (idUser,),True)
        if len(result)==1:
            return {'username':result[0][0], 'lastname':result[0][1], 'firstname':result[0][2]}
        else:
            return None
        
    def get_score(self, idUser):
        result = self.mySQLconnection.execute_prepared_query(f"SELECT avg(score) FROM review INNER JOIN announce USING (idAnnounce) INNER JOIN users ON review.idUser = users.idUser WHERE privilegeLevel > 0 AND announce.idUser = %s", (idUser,), True)
        score = 0.0
        try:
            score = float(result[0][0])
        except:
            pass

        return score
    
    def has_user1_blocked_user2(self, idUser1=0, idUser2=0, user1="", user2="", byID=True):
        values = []
        if not byID:
            idUser1 = self.get_user_id(user1)
            idUser2 = self.get_user_id(user2)

        values.append(idUser1)
        values.append(idUser2)

        result = self.mySQLconnection.execute_prepared_query(f"SELECT * FROM blocking WHERE idUserBlocking = %s AND idUserBlocked = %s ", values, True)
        return len(result)==1
    
    def user1_blocks_user2(self, block, idUser1=0, idUser2=0, user1="", user2="", byID=True):

        success = False

        if idUser1 != idUser2:
            values = []
            if not byID:
                idUser1 = self.get_user_id(user1)
                idUser2 = self.get_user_id(user2)
            
            if (idUser1 != -1 and idUser2 != -1):
                values.append(idUser1)
                values.append(idUser2)

                already_blocked = self.has_user1_blocked_user2(idUser1, idUser2)
                if already_blocked:
                    if not block:
                        query = f"DELETE FROM blocking WHERE idUserBlocking = %s AND idUserBlocked = %s"
                        self.mySQLconnection.execute_prepared_query(query, values, False)
                        success = True
                else:
                    if block:
                        query = f"INSERT INTO blocking (idUserBlocking, idUserBlocked) VALUES (%s, %s)"
                        self.mySQLconnection.execute_prepared_query(query, values, False)
                        success = True
        
        return success

    def ban_user(self, idUser, ban):
        level = 0 if ban else 1
        ban_query = f"UPDATE users SET privilegeLevel = %s WHERE idUser = %s"
        self.mySQLconnection.execute_prepared_query(ban_query, (level, idUser), False)

    def change_pwd(self, idUser, actual_pwd, new_pwd, new_pwd_conf):
        result_message = "Désolé, nous n'avons pas pu changer votre mot de passe."
        change_pwd_ok = (new_pwd == new_pwd_conf)
        if change_pwd_ok:
            change_pwd_ok = change_pwd_ok and security.is_pwd_strong_enough(new_pwd)
            if change_pwd_ok:
                check_actual_pwd_query = f"SELECT password FROM users WHERE password = %s AND idUser = %s"
                values = (security.hashStrToSha512(actual_pwd), idUser)
                results = self.mySQLconnection.execute_prepared_query(check_actual_pwd_query, values, True)
                change_pwd_ok = change_pwd_ok and len(results)==1
                if change_pwd_ok:
                    # changement de mot de passe
                    change_pwd_query = f"UPDATE users SET password = %s WHERE idUser = %s"
                    self.mySQLconnection.execute_prepared_query(change_pwd_query, (security.hashStrToSha512(new_pwd), idUser), False)
                    result_message = "Mot de passe modifié avec succès."
                else:
                    result_message = "Vous n'avez pas saisi votre mot de passe actuel correctement."
            else:
                result_message = "Le nouveau mot de passe ne respecte pas les critères de sécurité."
        else:
            result_message = "Le nouveau mot de passe n'a pas été confirmé correctement."
        
        return result_message
    
    def delete_account(self, idUser, actual_pwd, actual_pwd_conf):
        delete_success = (actual_pwd == actual_pwd_conf)
        if delete_success:
            check_pwd_query = f"SELECT * FROM users WHERE idUser = %s AND password = %s"
            values = (idUser, security.hashStrToSha512(actual_pwd))
            results = self.mySQLconnection.execute_prepared_query(check_pwd_query, values, True)
            delete_success = delete_success and len(results)==1
            if delete_success:
                delete_tokens_query = f"DELETE FROM tokens WHERE idUser = %s"
                values = (idUser,)
                self.mySQLconnection.execute_prepared_query(delete_tokens_query, values, False)

                delete_blockings_query = f"DELETE FROM blocking WHERE idUserBlocking = %s OR idUserBlocked = %s"
                values = (idUser, idUser)
                self.mySQLconnection.execute_prepared_query(delete_blockings_query, values, False)

                idReviews = self.mySQLconnection.execute_prepared_query(f"SELECT idReview FROM review WHERE idUser = %s", (idUser,), True)
                for row in idReviews:
                    self.mySQLconnection.execute_prepared_query(f"DELETE FROM reviewrating WHERE idReview = %s", (row[0],), False)
                
                delete_review_ratings_query = f"DELETE FROM reviewrating WHERE idUser = %s"
                values = (idUser,)
                self.mySQLconnection.execute_prepared_query(delete_review_ratings_query, values, False)

                delete_reviews_query = f"DELETE FROM review WHERE idUser = %s"
                self.mySQLconnection.execute_prepared_query(delete_reviews_query, values, False)

                idAnnounces = self.mySQLconnection.execute_prepared_query(f"SELECT idAnnounce FROM announce WHERE idUser = %s", (idUser,), True)
                for row in idAnnounces:
                    id_reviews = self.mySQLconnection.execute_prepared_query(f"SELECT idReview FROM review WHERE idAnnounce = %s", (row[0],), True)
                    for review in id_reviews:
                        self.mySQLconnection.execute_prepared_query(f"DELETE FROM reviewrating WHERE idReview = %s", (review[0],), False)

                    self.mySQLconnection.execute_prepared_query(f"DELETE FROM review WHERE idAnnounce = %s", (row[0],), False)

                delete_announces_query = f"DELETE FROM announce WHERE idUser = %s"
                self.mySQLconnection.execute_prepared_query(delete_announces_query, values, False)

                delete_dm_query = f"DELETE FROM privateMessages WHERE idFrom = %s OR idTo = %s"
                self.mySQLconnection.execute_prepared_query(delete_dm_query, (idUser, idUser), False)

                delete_user_query = f"DELETE FROM users WHERE idUser = %s"
                self.mySQLconnection.execute_prepared_query(delete_user_query, values, False)

                delete_success = True

        return delete_success
    
    def get_blocked_list(self, idUser):
        query = f"SELECT users.idUser, username, lastname, firstname FROM blocking INNER JOIN users ON blocking.idUserBlocked = users.idUser WHERE idUserBlocking = %s"
        results = self.mySQLconnection.execute_prepared_query(query, (idUser,), True)

        return [{'idUser':row[0], 'username':row[1], 'lastname':row[2], 'firstname':row[3]} for row in results]
    
    def if_login_exists(self, login):
        query = f"SELECT username FROM users WHERE username = %s"
        return len(self.mySQLconnection.execute_prepared_query(query, (login,), True))==1
    
    def get_secret_question(self, idUser):
        query = f"SELECT secretQuestion FROM users WHERE idUser = %s"
        results = self.mySQLconnection.execute_prepared_query(query, (idUser,), True)
        if len(results)==1:
            return results[0]
        else:
            return None
        
    def get_secret_answer(self, idUser):
        query = f"SELECT secretAnswer FROM users WHERE idUser = %s"
        results = self.mySQLconnection.execute_prepared_query(query, (idUser,), True)
        if len(results)==1:
            return security.aes_decrypt(ast.literal_eval(results[0]))
        else:
            return None
        
    def check_secret_answer(self, idUser, secretAnswerInput):
        query = f"SELECT secretAnswer FROM users WHERE idUser = %s"
        results = self.mySQLconnection.execute_prepared_query(query, (idUser,), True)
        
        if len(results)==1:
            security_dict = ast.literal_eval(results[0][0])
            unencrypted_secret_answer = security.aes_decrypt(security_dict)
            if secretAnswerInput == unencrypted_secret_answer:
                return True
        
        return False

    def get_secret_question_and_answer(self, idUser, actual_pwd, actual_pwd_conf):
        result = dict()
        result["ok"] = False

        are_infos_ok = (actual_pwd == actual_pwd_conf)
        if are_infos_ok:
            query_result = self.mySQLconnection.execute_prepared_query(f"SELECT secretQuestion, secretAnswer FROM users WHERE idUser = %s AND password = %s", (idUser, security.hashStrToSha512(actual_pwd)), True)
            are_infos_ok = len(query_result)==1
            if are_infos_ok:
                result["ok"] = True
                result["secret_question"] = query_result[0][0]
                result["secret_answer"] = security.aes_decrypt(ast.literal_eval(query_result[0][1]))
        
        return result

    
    def generate_token(self, idUser, length=32):
        return security.create_token(idUser, length)
    
    def reset_pwd(self, token, idUser, new_pwd, new_pwd_conf):
        return_msg = ""

        reset_pwd_ok = (new_pwd == new_pwd_conf)
        if reset_pwd_ok:
            reset_pwd_ok = reset_pwd_ok and security.is_pwd_strong_enough(new_pwd)
            if reset_pwd_ok:
                is_token_ok = security.is_token_valid(token, idUser)
                reset_pwd_ok = reset_pwd_ok and is_token_ok
                if reset_pwd_ok:
                    update_pwd_query = f"UPDATE users SET password = %s WHERE idUser = %s"
                    values = (security.hashStrToSha512(new_pwd), idUser)
                    self.mySQLconnection.execute_prepared_query(update_pwd_query, values, False)
                    return_msg = "Mot de passe réinitialisé avec succès."
                else:
                    return_msg = "Vous avez mis trop de temps à réinitialiser votre mot de passe, veuillez réessayer."
            else:
                return_msg = "Votre mot de passe n'est pas assez fort."
        else:
            return_msg = "Vous n'avez pas confirmé votre mot de passe."
        
        return return_msg
