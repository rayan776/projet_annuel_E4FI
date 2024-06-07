function showBoxAnnounces(event, divName, divToShow) {
    if (divName != "legende") {
        divToShow.style.left = event.clientX + 'px';
        divToShow.style.top = event.clientY + 'px';
    }
    else {
        divToShow.style.left = '2%';
        divToShow.style.top = '75%;'
    }
}

function formatDate(date) {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function setDefaultDate() {
    const today = new Date();
    const formattedToday = formatDate(today);

    let oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
    const formattedOneMonthAgo = formatDate(oneMonthAgo);

    if ((date1 = document.getElementById("announceDate1"))) {
        date1.value = formattedOneMonthAgo;
    }

    if ((date2 = document.getElementById("announceDate2"))) {
        date2.value = formattedToday;
    }
}

$(document).ready(function () {
    document.getElementById("btnSearchAnnounces").addEventListener("click", function(event)  {
        showBox(event, "searchDiv", "announces");
    }, false);
    document.getElementById("btnCloseSearchBox").addEventListener("click", function(event) {
        closeBox("searchDiv");
    }, false);
    
    document.getElementById("btnShowLegende").addEventListener("click", function(event) {
        showBox(event, "legende", "announces");
    }, false);
    document.getElementById("btnCloseLegende").addEventListener("click", function(event) {
        closeBox("legende");
    }, false);

    let btnNewAnnounce = document.getElementById("btnNewAnnounce");
    if (btnNewAnnounce) {
        document.getElementById("btnNewAnnounce").addEventListener("click", function(event)  {
            showBox(event, "newAnnounceDiv", "announces");
        }, false);
    }
    let btnCloseNewAnnounceBox = document.getElementById("btnCloseNewAnnounceBox");
    if (btnCloseNewAnnounceBox) {
        document.getElementById("btnCloseNewAnnounceBox").addEventListener("click", function(event) {
            closeBox("newAnnounceDiv");
        }, false);
    }

    makeDraggable(document.getElementById("searchDiv"));
    makeDraggable(document.getElementById("newAnnounceDiv"));
    makeDraggable(document.getElementById("legende"));

    setDefaultDate();
});