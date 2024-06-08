from django.shortcuts import render, redirect
from uncoup2pouce.users import Users
from stats.stats import Stats

# Create your views here.
def index(request):
    context = dict()
    users = Users()
    stats = Stats()
    context["isConnected"] = request.session.get("logged_user", False)
    context["module"] = "statsLink"
    context["initiales"] = request.session.get("initiales", "")
    context["level"] = ""
    context["login"] = request.session.get("login", "")
    context["level"] = users.getLevel(request, context["login"])
    context["stats"] = stats.get_stats()
    context["stars"] = range(5)
    
    return render(request, "stats/index.html", context)

