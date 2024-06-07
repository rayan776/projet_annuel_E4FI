import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import ast
from random import Random
from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton

def get_random_token(length):
    random = Random()
    
    chars = 'abcdef0123456789'
    newtoken = []
    for i in range(length):
        newtoken.append(chars[round(random.random()*15)])
    
    return "".join(newtoken)

def create_token(idUser, length=32):
     query = f"INSERT INTO tokens (token, idUser) VALUES (%s, %s)"
     token = get_random_token(length)
     values = (token, idUser)
     mySQLCo = MySQLConnectionSingleton()
     mySQLCo.execute_prepared_query(query, values, False)
     return token

def is_token_valid(token, idUser):
     query = f"SELECT * FROM tokens WHERE token = %s AND idUser = %s AND expiration_date > CURRENT_TIMESTAMP"
     values = (token, idUser)
     mySQLCo = MySQLConnectionSingleton()
     return len(mySQLCo.execute_prepared_query(query, values, True))==1

def aes_encrypt(text):
     key = get_random_bytes(16)
     cipher = AES.new(key, AES.MODE_EAX)
     encrypted_text, tag = cipher.encrypt_and_digest(text.encode())
     nonce = cipher.nonce
     return {'key':key, 'encrypted':encrypted_text, 'tag':tag, 'nonce':nonce}

def aes_encrypt_with_params(text, key):
    cipher = AES.new(key, AES.MODE_EAX)
    encrypted_text, tag = cipher.encrypt_and_digest(text.encode())
    nonce = cipher.nonce
    return {'key':key, 'encrypted':encrypted_text, 'tag':tag, 'nonce':nonce}

def aes_decrypt(encryption_dict):
     cipher = AES.new(encryption_dict['key'], AES.MODE_EAX, encryption_dict['nonce'])
     data = cipher.decrypt_and_verify(encryption_dict['encrypted'], encryption_dict['tag'])
     return data.decode()

def hashStrToSha512(strToHash):
    hashObject = hashlib.sha512()
    hashObject.update(strToHash.encode())
    return hashObject.hexdigest()

def is_pwd_strong_enough(pwd):
        """
            vérifie que le mot de passe saisi lors de l'inscription respecte les critères de sécurité
            (au moins 8 caractères avec 1 minuscule, 1 majuscule, 1 chiffre et 1 caractère spécial)
        """
        compteurMin = 0
        compteurMaj = 0
        compteurNum = 0
        compteurSpec = 0

        listChars = [char for char in pwd]
        if len(listChars) < 8:
            return False
        
        for char in listChars:
            if char.isnumeric():
                compteurNum = compteurNum + 1
            elif char.islower():
                compteurMin = compteurMin + 1
            elif char.isupper():
                compteurMaj = compteurMaj + 1
            else:
                compteurSpec = compteurSpec + 1
        
        return compteurMin >= 1 and compteurMaj >= 1 and compteurNum >= 1 and compteurSpec >= 1