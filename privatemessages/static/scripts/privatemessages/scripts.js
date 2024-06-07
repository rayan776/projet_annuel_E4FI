function showBoxDM(event, divToShow) {
    if (event != null) {
        divToShow.style.left = event.clientX + 'px';
        divToShow.style.top = event.clientY + 'px';
    }
    else {
        divToShow.style.left = "50%";
        divToShow.style.top = "25%";
    }
}

$(document).ready(function() {
    document.getElementById("btnSendMessage").addEventListener("click", function(event) {
        document.getElementById("toUser").value = "";
        showBox(event, "sendMessages", "dm");
    }, false);
    document.getElementById("btnCloseSendDM").addEventListener("click", function(event) {
        closeBox("sendMessages");
    }, false);
    document.getElementById("btnCloseViewMessage").addEventListener("click", function(event) {
        closeBox("viewMessage");
    }, false);
    document.getElementById("reply").addEventListener("click", function(event) {
        document.getElementById("toUser").value = document.getElementById("recipient").innerText;
        showBox(event, "sendMessages", "dm");
    }, false);

    let closePopup = document.getElementById("btnClosePopup");
    if (closePopup) {
        closePopup.addEventListener("click", function(event) {
            closeBox("dmPopup");
        }, false);
    }
    makeDraggable(document.getElementById("sendMessages"));
    makeDraggable(document.getElementById("viewMessage"));

    let msg = document.getElementsByClassName("msg");

    for (let i=0; i<msg.length; i++) {
            $(msg[i]).click(function(e) {

                e.preventDefault();
                let formData = new FormData();
                formData.append('idMessage', e.currentTarget.id);
            
                const request = new Request('http://127.0.0.1:8000/privatemessages/getMessage/', {
                    method: 'POST',
                    body: formData
                });
            
            fetch(request)
                    .then(response => response.json())
                    .then(result => {
                        if (result["ok"]) {
                            msg[i].classList.remove('unread');

                            document.getElementById("viewMessageSentToA").innerText = result["message"]["dest_lastname"] + " " + result["message"]["dest_firstname"] + " (" + result["message"]["dest_user"] + ")";
                            document.getElementById("viewMessageSentToA").setAttribute('href', "http://127.0.0.1:8000/accounts/viewProfile/" + result["message"]["dest_user"])
                            document.getElementById("viewMessageSentByA").innerText = result["message"]["exp_lastname"] + " " + result["message"]["exp_firstname"] + " (" + result["message"]["exp_user"] + ")";
                            document.getElementById("viewMessageSentByA").setAttribute('href', "http://127.0.0.1:8000/accounts/viewProfile/" + result["message"]["exp_user"])
                            document.getElementById("viewMessageTitle").innerText = result["message"]["title"];
                            document.getElementById("viewMessageContent").innerText = result["message"]["content"];
                            document.getElementById("viewMessageDate").innerText = result["message"]["dateMsg"];
                            
                            if (result["message"]["type"] == "received") {
                                document.getElementById("recipient").innerText = result["message"]["exp_user"];
                                document.getElementById("reply").style.display = 'inline';
                                document.getElementById("reply").style.pointerEvents = 'all';
                                document.getElementById("viewMessageDest").style.display = 'none';
                                document.getElementById("viewMessageDest").style.pointerEvents = 'none';
                                document.getElementById("viewMessageExp").style.display = 'inline';
                                document.getElementById("viewMessageExp").style.pointerEvents = 'all';
                                document.getElementById("unread_msg").innerText = result["message"]["nb_unread"] + " messages non lus"
                            }
                            else {
                                document.getElementById("recipient").innerText = "";
                                document.getElementById("reply").style.display = 'none';
                                document.getElementById("reply").style.pointerEvents = 'none';
                                document.getElementById("viewMessageDest").style.display = 'inline';
                                document.getElementById("viewMessageDest").style.pointerEvents = 'all';
                                document.getElementById("viewMessageExp").style.display = 'none';
                                document.getElementById("viewMessageExp").style.pointerEvents = 'none';
                            }
                            
                            showBox(e, "viewMessage", "dm");

                            if (result["message"]["opened"]==0) {
                                update_unread_messages_bubble();
                            }
                        }
                    })
            });
    }
    
});

