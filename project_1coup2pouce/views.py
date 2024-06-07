from datetime import datetime
from django.shortcuts import render
from project_1coup2pouce.users import Users
from project_1coup2pouce.homepage import get_latest_announces

def index(request):
    context = dict()
    context["login"] = ""
    context["initiales"] = request.session.get("initiales", "")
    context["latest_announces"] = get_latest_announces(5)
    context["isConnected"] = request.session.get("logged_user", False)
    if request.session.get("logged_user", False) == True:
        if request.POST.get('logout', "") == 'logout':
            usrLogout = Users()
            usrLogout.logout(request, context)
        else:
            context["login"] = request.session.get("login")

    return render(request, "project_1coup2pouce/index.html", context)