$(document).ready(function () {
    let btnClosePopup = document.getElementById("btnClosePopup");
    if (btnClosePopup) {
        document.getElementById("btnClosePopup").addEventListener("click", function(event) {
            closeBox("announcePopup");
        }, false);
    }
});