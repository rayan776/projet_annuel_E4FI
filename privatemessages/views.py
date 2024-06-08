from django.http import JsonResponse
from django.shortcuts import render, redirect
from uncoup2pouce.users import Users
from privatemessages.messages import Messages
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    messages = Messages()
    context = dict()
    context["popup_message"] = ""
    context["isConnected"] = request.session.get("logged_user", False)
    if not context["isConnected"]:
        return redirect("http://127.0.0.1:8000/accounts/login")
    
    context["module"] = "dmLink"
    context["initiales"] = request.session.get("initiales", "")
    context["login"] = ""
    users = Users()
    context["login"] = request.session["login"]
    context["level"] = users.getLevel(request, request.session["login"])

    if not request.POST.get("sendDM", None) is None:
        context["popup_message"] = messages.send_message(request.session["idUser"], request.POST.get("toUser", "0"), request.POST.get("dmTitle", ""), request.POST.get("dmContent", ""))
    
    context["nb_unread"] = messages.get_count_of_unread_messages_for_user(request.session["idUser"])
    messages_to_show = messages.get_messages(request.session["idUser"])
    context["received"] = messages_to_show["received"]
    context["sent"] = messages_to_show["sent"]
    context["has_received"] = len(messages_to_show["received"])>0
    context["has_sent"] = len(messages_to_show["sent"])>0
    context["writeTo"] = request.GET.get("writeTo", None)

    return render(request, "privatemessages/index.html", context)

@csrf_exempt
def get_nb_unread_messages(request):
    messages = Messages()
    ok = True
    nb_unread = 0

    if not request.session.get("logged_user", False) or not request.POST.get("get_unread", False):
        ok = False
    else:
        try:
            nb_unread = messages.get_count_of_unread_messages_for_user(request.session["idUser"])
            if nb_unread == 0:
                ok = False
        except:
                ok = False
    
    return JsonResponse({'ok':ok, 'nb_unread':nb_unread})

@csrf_exempt
def getMessage(request):
    ok = True
    messages = Messages()
    
    if not request.session.get("logged_user", False):
        ok = False
    else:
        idMessage = request.POST.get("idMessage", 0)
        try:
            idMessage = int(idMessage[3:])
            if not messages.has_user_received_or_sent_this_message(idMessage, request.session["idUser"]):
                ok = False
        except:
            ok = False

    if not ok:
        return JsonResponse({'ok':False})
    else:
        return JsonResponse({'ok':True, 'message':messages.get_message(idMessage, request.session["login"], request.session["idUser"])})