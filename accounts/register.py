from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
import project_1coup2pouce.security as security

class Register:
    firstname = ""
    lastname = ""
    username = ""
    pwd = ""
    pwdconf = ""
    secretQ = ""
    secretA = ""
    LOGIN_MIN_LENGTH = 6
    LOGIN_MAX_LENGTH = 20
    ALLOWED_CHARS_USERNAME = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
    ALLOWED_CHARS_NAME = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- '

    def __init__(self, firstname, lastname, username, pwd, pwdconf, secretQ, secretA):
        self.firstname = firstname.strip()
        if len(self.firstname)>0:
            self.firstname = self.firstname[0].upper() + self.firstname[1:].lower()

        self.lastname = lastname.strip().lower()
        if len(self.lastname)>0:
            self.lastname = self.lastname[0].upper() + self.lastname[1:].lower()

        self.username = username.strip()
        self.pwd = pwd.strip()
        self.pwdconf = pwdconf.strip()
        self.secretQ = secretQ.strip()
        self.secretA = secretA
    
    def has_got_only_allowed_chars(nameToCheck, isUsername):
        if isUsername:
            return all (c in Register.ALLOWED_CHARS_USERNAME for c in nameToCheck)
        else:
            return all (c in Register.ALLOWED_CHARS_NAME for c in nameToCheck)

    def is_valid_name(name, isUsername):
        if isUsername:
            return Register.has_got_only_allowed_chars(name, True) and Register.LOGIN_MIN_LENGTH <= len(name) <= Register.LOGIN_MAX_LENGTH
        else:
            return Register.has_got_only_allowed_chars(name, False)
    
    def is_login_already_taken(self):
        mySQLInstance = MySQLConnectionSingleton()
        results = mySQLInstance.execute_prepared_query(f"SELECT username FROM users WHERE username = %s", (self.username,), True)
        return len(results) > 0

    def are_names_valid(self):
        """
            vérifie que les nom et prénom saisis lors de l'inscription sont conformes (que des lettres)
        """
        return Register.is_valid_name(self.lastname, False) and Register.is_valid_name(self.firstname, False)

    def is_username_valid(self):
        """
            vérifie que le login saisi lors de l'inscription est conforme (que des lettres, longueur entre min et max, login disponible)
        """
        return Register.is_valid_name(self.username, True) and not self.is_login_already_taken()
    
    def is_pwd_valid(self):
        return security.is_pwd_strong_enough(self.pwd) and self.pwd == self.pwdconf
    
    def are_register_requirements_fulfilled(self):
        return self.are_names_valid() and self.is_username_valid() and self.is_pwd_valid() and len(self.secretQ) > 0 and len(self.secretA) > 0

    def create_account(self):
        """
            essaye de créer un compte à partir des données fournies par l'utilisateur
        """
        if self.are_register_requirements_fulfilled():
            try:
                mySQLInstance = MySQLConnectionSingleton()
                values = (self.firstname, self.lastname, self.username, security.hashStrToSha512(self.pwd), self.secretQ, str(security.aes_encrypt(self.secretA)))
                mySQLInstance.execute_prepared_query(f"INSERT INTO users (firstname, lastname, username, password, privilegeLevel, dateRegister, secretQuestion, secretAnswer) VALUES (%s, %s, %s, %s, 1, CURRENT_TIMESTAMP, %s, %s)", values, False)
            except:
                return (-1, "Une erreur inattendue est survenue lors de l'essai de la création du compte.")

            return (0, "Votre compte a été crée avec succès, vous pouvez désormais vous connecter.")
        else:
            return (-1, "Un ou plusieurs champs sont mal renseignés, veuillez vérifier vos saisies.")
