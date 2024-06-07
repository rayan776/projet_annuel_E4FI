from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
from project_1coup2pouce.users import Users
from datetime import datetime

class Messages:
    mysqlCo = None
    users = None

    def __init__(self):
        self.mysqlCo = MySQLConnectionSingleton()
        self.users = Users()
    
    def get_count_of_unread_messages_for_user(self, idUser):
        query = f"SELECT count(idMsg) FROM privateMessages WHERE idTo = %s AND opened = 0"
        unread_count = 0
        try:
            unread_count = self.mysqlCo.execute_prepared_query(query, (idUser,), True)[0][0]
        except:
            pass

        return unread_count

    def has_user_received_or_sent_this_message(self, idMessage, idUser):
        query = f"SELECT idMsg FROM privateMessages WHERE idMsg = %s AND (idFrom = %s OR idTo = %s) "
        values = (idMessage, idUser, idUser)
        result = self.mysqlCo.execute_prepared_query(query, values, True)
        return len(result)==1

    def send_message(self, idFrom, toUser, title, content):

        # vérifier que les id existent et que idTo et idFrom ne se sont pas bloqués.
        # title et content ne doivent pas être vides

        return_msg = "Echec de l'envoi du message."

        try:
            from_infos = self.users.get_username_and_name(idFrom)
            idTo = self.users.get_user_id(toUser)
            to_infos = self.users.get_username_and_name(idTo)
            if not from_infos is None and not to_infos is None:
                # on ne peut pas DM quelqu'un qui nous a bloqué / qu'on a bloqué
                if not self.users.has_user1_blocked_user2(idTo, idFrom) and not self.users.has_user1_blocked_user2(idFrom, idTo):
                    title = title.strip()
                    content = content.strip()
                    if len(title) > 0 and len(content) > 0:
                        if not self.users.has_user1_blocked_user2(idUser1=idTo, idUser2=idFrom):
                            query = f"INSERT INTO privateMessages (title, content, dateMsg, idFrom, idTo) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s) "
                            values = (title, content, idFrom, idTo)
                            self.mysqlCo.execute_prepared_query(query, values, False)
                            return_msg = "Message envoyé."
        except:
            pass

        return return_msg
    
    def get_message(self, idMessage, current_user, idUser):
        query = f"SELECT title, content, dateMsg, u.username AS exp_user, u.firstname AS exp_firstname, u.lastname AS exp_lastname, u2.username AS dest_user, u2.firstname AS dest_firstname, u2.lastname, opened AS dest_lastname FROM privatemessages p INNER JOIN users u ON p.idFrom = u.idUser INNER JOIN users u2 ON p.idTo = u2.idUser WHERE idMsg = %s"
        result = self.mysqlCo.execute_prepared_query(query, (idMessage,), True)
        result_dic = dict()
        for msg in result:
            result_dic['title'] = f"Titre : {msg[0]}"
            result_dic['content'] = msg[1]
            result_dic['dateMsg'] = "Le " + msg[2].strftime("%d/%m/%Y") + " à " + msg[2].strftime("%H:%M")
            result_dic['exp_user'] = msg[3]
            result_dic['exp_firstname'] = msg[4]
            result_dic['exp_lastname'] = msg[5]
            result_dic['dest_user'] = msg[6]
            result_dic['dest_firstname'] = msg[7]
            result_dic['dest_lastname'] = msg[8]
            result_dic['opened'] = msg[9]
            result_dic['type'] = 'received' if current_user == msg[6] else 'sent'
        
            if result_dic['type'] == 'received':
                query = f"UPDATE privateMessages SET opened = 1 WHERE idMsg = %s"
                self.mysqlCo.execute_prepared_query(query, (idMessage,), False)
                result_dic['nb_unread'] = self.get_count_of_unread_messages_for_user(idUser)

        return result_dic

        
    def get_messages(self, idUser):
        query_sent_messages = f"SELECT idMsg, title, dateMsg, username, firstname, lastname FROM privateMessages p INNER JOIN users u ON p.idTo = u.idUser WHERE idFrom = %s ORDER BY dateMsg DESC"
        query_received_messages = f"SELECT idMsg, title, dateMsg, username, firstname, lastname, opened FROM privateMessages p INNER JOIN users u ON p.idFrom = u.idUser WHERE idTo = %s ORDER BY dateMsg DESC"

        values = (idUser,)
        sent_messages = self.mysqlCo.execute_prepared_query(query_sent_messages, values, True)
        received_messages = self.mysqlCo.execute_prepared_query(query_received_messages, values, True)

        sent_messages_dic = dict()
        received_messages_dic = dict()

        counter = 0

        for tuple in sent_messages:
            sent_messages_dic[counter] = {'idMsg':tuple[0], 'title':tuple[1], 'dateMsg':tuple[2], 'username':tuple[3], 'firstname':tuple[4], 'lastname':tuple[5]}
            counter += 1
        
        counter = 0
        
        for tuple in received_messages:
            received_messages_dic[counter] = {'idMsg':tuple[0], 'title':tuple[1], 'dateMsg':tuple[2], 'username':tuple[3], 'firstname':tuple[4], 'lastname':tuple[5], 'opened':tuple[6]}
            counter += 1

        return {'received':received_messages_dic, 'sent':sent_messages_dic}

        