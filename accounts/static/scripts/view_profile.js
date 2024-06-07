

$(document).ready(function() {
    let btnClosePopup = document.getElementById("btnClosePopup");

    if (btnClosePopup) {
        btnClosePopup.addEventListener("click", function(e) {
            closeBox("viewProfilePopup");
        }, false);
    }

    let unblock_info_element = document.getElementById("info-unblock");
    let blocked_list_unblock_buttons_icons = document.getElementsByClassName("blocked-list-unblock-btn-icon");

    for (let i=0; i<blocked_list_unblock_buttons_icons.length; i++) {
        blocked_list_unblock_buttons_icons[i].addEventListener('mouseenter', function(e) {
            const rect = e.currentTarget.getBoundingClientRect();
            unblock_info_element.style.display = 'block';
            unblock_info_element.style.opacity = 1.0;
            unblock_info_element.style.pointerEvents = 'all';
            unblock_info_element.style.position = 'absolute';
            
            unblock_info_element.style.left = rect.left + window.scrollX + 'px';
            unblock_info_element.style.top = rect.top + window.scrollY + 'px';
    
            unblock_info_element.style.transform = "translate(15px,15px)";
        });

        blocked_list_unblock_buttons_icons[i].addEventListener('mouseleave', function(e) {
            unblock_info_element.style.opacity = 0.0;
            while (unblock_info_element.style.opacity > 0.0) {
                unblock_info_element.style.pointerEvents = 'none';
                unblock_info_element.style.position = 'relative';
                unblock_info_element.style.transform = "translate(-15px,-15px)";
            }
        });
    }

    let blocked_list_unblock_buttons = document.getElementsByClassName("blocked-list-unblock-btn");

    for (let i=0; i<blocked_list_unblock_buttons.length; i++) {

        $(blocked_list_unblock_buttons[i]).click(function(e) {

            e.preventDefault();
            let formData = new FormData();
            formData.append('idUserToUnblock', e.currentTarget.id);
            let csrfTokenValue = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
            const request = new Request('http://127.0.0.1:8000/accounts/getBlockedList/', {
                method: 'POST',
                body: formData,
                headers: {'X-CSRFToken': csrfTokenValue}
            });
        
        fetch(request)
                .then(response => response.json())
                .then(result => {
                    if (result["ok"]) {
                        document.getElementById(result["div_to_remove"]).remove();
                        unblock_info_element.style.opacity = 0.0;
                        while (unblock_info_element.style.opacity > 0.0) {
                            unblock_info_element.style.pointerEvents = 'none';
                            unblock_info_element.style.position = 'relative';
                            unblock_info_element.style.transform = "translate(-15px,-15px)";
                        }
                    }
                })
        });
        
    }
});