# Create your views here.

from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts.loginCheck import LoginCheck
from accounts.register import Register
from project_1coup2pouce.users import Users
from accounts.user_profile import UserProfile
from django.views.decorators.csrf import csrf_exempt


def index(request):
    if request.session.get("logged_user", False):
        if request.POST.get('logout', "") == 'logout':
            request.session.flush()
            request.session['logged_user'] = False
        else:
                return redirect(f"viewProfile/{request.session['login']}")
        
    return redirect("index")

def login(request):
    context = dict()
    context["module"] = "myAccountLink"
    context["login"] = '.' # pas de login
    context["initiales"] = request.session.get("initiales", "")
    context["isConnected"] = request.session.get("logged_user", False)
    if not request.session.get("logged_user", False):
        # tentative de connexion (si requête POST de login formulée)
        if not request.POST.get('username', None) is None and not request.POST.get('pwd', None) is None:
            loginChk = LoginCheck(request.POST.get('username'), request.POST.get('pwd'))
            if loginChk.checkCredentials():
                 # login réussi
                users = Users()
                users.login(request, context)
            else:
                context["login"] = 'w' # échec de login
    else:
        context["login"] = request.session.get("login")

    return render(request, "accounts/login.html", context)

def register(request):
    context = dict()
    context["module"] = "myAccountLink"
    context["login_min_length"] = Register.LOGIN_MIN_LENGTH
    context["login_max_length"] = Register.LOGIN_MAX_LENGTH
    context["registerMessage"] = ""
    context["firstname"] = ""
    context["lastname"] = ""
    context["username"] = ""
    context["login"] = "."
    context["registerOK"] = False
    context["initiales"] = request.session.get("initiales", "")
    context["isConnected"] = request.session.get("logged_user", False)
    if not request.session.get("logged_user", False):
        if request.POST.get("registerAttempt", "") != "":
            # tentative d'inscription
            firstname = request.POST.get("firstname", "")
            lastname = request.POST.get("lastname", "")
            username = request.POST.get("username", "")
            pwd = request.POST.get("pwd", "")
            pwdconf = request.POST.get("pwdconf", "")
            secretQuestion = request.POST.get("secretQuestion", "")
            secretAnswer = request.POST.get("secretAnswer", "")
            register = Register(firstname, lastname, username, pwd, pwdconf, secretQuestion, secretAnswer)
            context["firstname"] = firstname
            context["lastname"] = lastname
            context["username"] = username
            context["secretQuestion"] = secretQuestion
            context["secretAnswer"] = secretAnswer
            createAccountMessage = register.create_account()
            context["registerMessage"] = createAccountMessage[1]
            if (createAccountMessage[0] != 0):
                # inscription ratée
                return render(request, "accounts/register.html", context)
            else:
                # inscription réussie
                context["registerOK"] = True
                return render(request, "accounts/index.html", context)
        else:
            # pas de tentative d'inscription
            return render(request, "accounts/register.html", context)
    else:
        # déjà connecté
        return redirect('accounts')
    
def view_profile(request, login):
    context = dict()
    user_profile = UserProfile()
    users = Users()
    idUser = users.get_user_id(login)
    context["module"] = "myAccountLink"
    context["initiales"] = request.session.get("initiales", "")
    context["isConnected"] = request.session.get("logged_user", False)
    context["popup"] = ""

    if context["isConnected"]:
        context["login"] = request.session["login"]
        context["current_user_ID"] = request.session["idUser"]
        context["level"] = users.getLevel(request, request.session["login"])

        # change pwd
        if not request.POST.get("change_pwd", None) is None:
            context["popup"] = users.change_pwd(request.session['idUser'], request.POST.get("actual_pwd", ""), request.POST.get("new_pwd", ""), request.POST.get("new_pwd_conf", ""))
        
        # delete account
        if not request.POST.get("delete_my_account", None) is None:
            was_account_deleted = users.delete_account(request.session['idUser'], request.POST.get("actual_pwd", ""), request.POST.get("actual_pwd_conf", ""))
            if was_account_deleted:
                request.session.flush()
                request.session['logged_user'] = False
                return render(request, "accounts/bye.html")
            else:
                context["popup"] = "Votre compte n'a pas pu être supprimé. Vous avez peut-être mal saisi votre mot de passe."

        # block
        if not request.POST.get("blockUser", None) is None:
            users.user1_blocks_user2(True, request.session['idUser'], request.POST.get("idUserTarget", 0))
        # unblock
        if not request.POST.get("unblockUser", None) is None:
            users.user1_blocks_user2(False, request.session['idUser'], request.POST.get("idUserTarget", 0))
        
        if context["level"] == "admin":
            # ban
            if not request.POST.get("banUser", None) is None:
                users.ban_user(request.POST.get("idUserTarget", 0), True)
            
            # unban
            if not request.POST.get("unbanUser", None) is None:
                users.ban_user(request.POST.get("idUserTarget", 0), False)


    context["view_profile_infos"] = user_profile.get_infos_for_user_profile_template(idUser, request.session.get("idUser", 0))
    context["stars"] = range(5)

    return render(request, "accounts/view_profile.html", context)

def getBlockedList(request):
    result = dict()
    result["ok"] = False

    if request.session.get("logged_user", False):
        users = Users()
        idUserToUnblock = request.POST.get("idUserToUnblock", "0")[8:]
        result["ok"] = users.user1_blocks_user2(False, request.session['idUser'], idUserToUnblock)
        if result["ok"]:
            result["div_to_remove"] = f"blocked_{idUserToUnblock}"
    
    return JsonResponse(result)

def resetPassword(request):
    context = dict()
    
    if not request.session.get("logged_user", False):
        if not request.POST.get("reset_pwd", None) is None:
            users = Users()
            context["popup"] = users.reset_pwd(request.POST.get("token", ""), request.POST.get("idUser", ""), request.POST.get("new_pwd", ""), request.POST.get("new_pwd_conf", ""))
    else:
        return redirect("index")

    return render(request, "accounts/reset_password.html", context)

@csrf_exempt
def checkUsername(request):
    result = dict()
    result["username_exists"] = False
    if not request.session.get("logged_user", False):
        users = Users()
        result["username_exists"] = users.if_login_exists(request.POST.get("username", ""))
        if result["username_exists"]:
            result["idUser"] = users.get_user_id(request.POST["username"])
            result["secretQuestion"] = users.get_secret_question(result["idUser"])
    
    return JsonResponse(result)

@csrf_exempt
def checkSecretAnswer(request):
    result = dict()
    if not request.session.get("logged_user", False):
        idUser = request.POST.get("idUser", 0)
        secretAnswer = request.POST.get("secretAnswer", "")
        users = Users()
        result["isSecretAnswerOk"] = users.check_secret_answer(idUser, secretAnswer)
        if result["isSecretAnswerOk"]:
            result["idUser"] = idUser
            result["new_pwd_token"] = users.generate_token(idUser)

    return JsonResponse(result)

@csrf_exempt
def showSecretAnswer(request):
    result = dict()
    if request.session.get("logged_user", False):
        if not request.POST.get("view_secret_answer", None) is None:
            idUser = request.POST.get("idUser", 0)
            actual_pwd = request.POST.get("actual_pwd", "")
            actual_pwd_conf = request.POST.get("actual_pwd_conf", "")
            users = Users()
            result = users.get_secret_question_and_answer(idUser, actual_pwd, actual_pwd_conf)
    
    return JsonResponse(result)
        
