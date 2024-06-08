function openTab(tabId) {
    var tabContents = document.getElementsByClassName('tab-content');
    for (var i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = 'none';
        tabContents[i].style.pointerEvents = 'none';
    }

    var tabs = document.getElementsByClassName('tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active-tab');
    }

    document.getElementById(tabId).style.display = 'block';
    document.getElementById(tabId).style.pointerEvents = 'all';
    document.querySelector('[onclick="openTab(\'' + tabId + '\')"]').classList.add('active-tab');
}