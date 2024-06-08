async function showInfo(e, textToShow) {
    let info_bubble = document.getElementById("info");
    const rect = e.currentTarget.getBoundingClientRect();

    info_bubble.style.display = 'block';
    await sleep(100);
    info_bubble.style.pointerEvents = 'all';
    info_bubble.innerText = textToShow;
    info_bubble.style.opacity = 1.0;
    info_bubble.style.left = rect.left + window.scrollX + 'px';
    info_bubble.style.top = rect.top + window.scrollY + 'px';

    info_bubble.style.transform = "translateX(20px)";
}

async function closeInfo() {
    let info_bubble = document.getElementById("info");
    info_bubble.style.opacity = 0.0;
    info_bubble.style.transform = "translateX(-15px)";
    await sleep(100);
    info_bubble.style.display = 'none';
}

function createListeners(helper, text) {
    helper.addEventListener("click", function(e) {
        e.stopPropagation();
        showInfo(e, text);
    }, false);
}

function closeBox(divName) {
    const divToClose = document.getElementById(divName);
    if (divToClose != null) {
        divToClose.style.display = "none";
        divToClose.style.pointerEvents = "none";
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showBox(event, divName, module) {
    const divToShow = document.getElementById(divName);
    if (divToShow != null) {
        divToShow.style.display = "flex";
        divToShow.style.pointerEvents = "all";
        if (module == "announces") {
            showBoxAnnounces(event, divName, divToShow);
        }
        else if (module == "dm") {
            showBoxDM(event, divToShow);
        }
    }
}

function makeDraggable(element) {
    let mousePosition;
    let offset = [0,0];
    let isDragging = false;

    element.addEventListener('mousedown', function(e) {
        isDragging = true;
        element.style.position = 'absolute';
        isDown = true;
        offset = [
            element.offsetLeft - e.clientX,
            element.offsetTop - e.clientY
        ];
        element.style.zIndex = 1000;
    });

    document.addEventListener('mousemove', function(e) {
        e.preventDefault();
        if (isDragging) {
            mousePosition = {
                x : e.clientX,
                y : e.clientY
            };
            element.style.left = (mousePosition.x + offset[0]) + 'px';
            element.style.top = (mousePosition.y + offset[1]) + 'px';
        }
    });

    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
}