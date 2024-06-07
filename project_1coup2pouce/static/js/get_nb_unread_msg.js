function update_unread_messages_bubble() {
    let formData = new FormData();
    formData.append('get_unread', 1)

    const request = new Request('http://127.0.0.1:8000/privatemessages/getNbUnreadMsg/', {
        method: 'POST',
        body: formData
    });

    fetch(request)
        .then(response => response.json())
            .then(result => {
                let unread_div = document.getElementById("sidebar_unread");

                if (unread_div) {
                    unread_div.style.display = 'none';
                    unread_div.style.pointerEvents = 'none';
                    unread_div.innerText = "";
                }
                
                if (result["ok"]) {
                    if (unread_div && result["nb_unread"]>0) {
                        unread_div.style.display = 'inline';
                        unread_div.style.pointerEvents = 'all';
                        unread_div.innerText = result["nb_unread"];
                    }
                }
            })
}

$(document).ready(function() { 
    update_unread_messages_bubble();
});