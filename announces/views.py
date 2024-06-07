# Create your views here.

from django.http import JsonResponse
from django.shortcuts import render
from announces.announce import Announce
from announces.map_generator import MapGenerator
from project_1coup2pouce.users import Users
import ast

def index(request):
    context = dict()
    context["module"] = "announceLink"
    context["initiales"] = request.session.get("initiales", "")
    context["isConnected"] = request.session.get("logged_user", False)
    context["login"] = ""
    context["level"] = ""
    if context["isConnected"] == True:
        users = Users()
        context["login"] = request.session["login"]
        context["level"] = users.getLevel(request, request.session["login"])

    context["announce_message"] = ""
    actionToDo = request.POST.get("whatToDo", "")
    announce = Announce()
    defaultSearch = True

    if (actionToDo == "search"):
        defaultSearch = False
    elif (actionToDo == "new"):
        hasAnnounceBeenAdded = announce.add_new_announce(request)
        if not hasAnnounceBeenAdded:
            context["announce_message"] = "La création de l'annonce a échoué."
        else:
            context["announce_message"] = "Votre annonce a été publiée. Elle devra être validée par l'administration avant d'être visible."

    announcesToShow = announce.get_announces(request, defaultSearch)

    # récupérer les catégories
    announceObject = Announce()
    context["categories"] = announceObject.get_categories()
    context["announces_list"] = announcesToShow["announces"]

    # initialisation de la map
    map_generator = MapGenerator()
    map_generator.generate_map(context, request, announcesToShow)

    if actionToDo == "search":
        context["announce_message"] = f"Annonces trouvées"
    else:
        context["nb_announces"] = ""

    return render(request, "announces/index.html", context)

def viewAnnounce(request, idAnnounce):
    context = dict()
    context["module"] = "announceLink"
    context["announce_message"] = ""
    context["initiales"] = request.session.get("initiales", "")
    context["login"]= request.session.get("login", "")
    context["isConnected"] = request.session.get("logged_user", False)
    context["not_found"] = False
    context["level"] = ""
    context["new_review_msg"] = ""
    context["announce_deleted"] = False
    
    if context["isConnected"]:
        users = Users()
        context["level"] = users.getLevel(request, request.session["login"])

    announce_object = Announce()
    context["categories"] = announce_object.get_categories()

    try:
        idAnnounce = int(idAnnounce)
    except:
        idAnnounce = -1
    
    # modération
    if (not request.POST.get("validate", None) is None):
            announce_object.moderate_announce(request, "validate", idAnnounce, context["level"])
            context["announce_message"] = "L'annonce a été approuvée."
    elif (not request.POST.get("invalidate", None) is None):
        announce_object.moderate_announce(request, "invalidate", idAnnounce, context["level"])
        context["announce_message"] = "L'annonce n'est désormais plus visible jusqu'à nouvel ordre."
    
    # poster un commentaire
    if (not request.POST.get("newReview", None) is None):
        context["announce_message"] = announce_object.new_review(request, idAnnounce, context["level"])
    
    # modifier
    if not request.POST.get("edit", None) is None:
        context["announce_message"] = announce_object.edit_announce(request, idAnnounce)

    announce = announce_object.get_announce(request, idAnnounce, context["level"]=="admin")

    delete_announce_return_val = ""

    if (announce is None):
        context["not_found"] = True
        context["announce_message"] = "Nous n'avons pas pu trouver cette annonce..."
    else:
        context["score_range"] = range(5)
        context["reviews"] = announce_object.get_reviews(idAnnounce)
        context["nb_reviews"] = len(context["reviews"])
        context["idAnnounce"] = announce[0]
        context["typeAnnounce"] = "Je propose" if announce[1] == 1 else "Je recherche"
        context["dateAnnounce"] = announce[2]
        context["intitule"] = announce[3]
        context["description"] = announce[4]
        context["localisation"] = ast.literal_eval(announce[7])
        context["valid"] = announce[8]
        context["idCat"] = announce[9]
        context["idUser"] = announce[10]
        context["catName"] = announce[11]
        context["username"] = announce[12]
        context["firstname"] = announce[13]
        context["lastname"] = announce[14]
        context["is_owner_current_user"] = context["isConnected"] and context["username"] == context["login"]
        if context["isConnected"]:
            context["has_current_user_already_commented"] = announce_object.has_user_already_commented(idAnnounce, request.session["idUser"])

        if not request.POST.get("delete", None) is None:
            delete_announce_return_val = announce_object.remove_announce(idAnnounce, context["is_owner_current_user"], context["level"])
            context["announce_message"] = delete_announce_return_val[1]
            context["announce_deleted"] = delete_announce_return_val[0] == 0
        else:
            context["announce_score"], context["announce_score_stars"] = announce_object.get_score(idAnnounce)

    return render(request, "announces/announce_template.html", context)

def rateReview(request):
    ok = False
    results = None
    rating = None
    idReview = None

    if request.session.get("logged_user", False):
        try:
            rate_review = request.POST.get("rate_review").split("_")
            if rate_review[0] == 'up':
                rating = 1
            elif rate_review[0] == 'down':
                rating = -1
            else:
                ok = False

            ok = (rating == 1 or rating == -1)
            if ok:
                idReview = int(rate_review[1])
                ok = True
        except:
            ok = False

    if ok:
        announce_obj = Announce()
        results = announce_obj.rate_review(request, idReview, request.session["idUser"], rating, request.session["login"])

    if results is None:
        return JsonResponse({'ok':False})
    else:
        return JsonResponse(results)
