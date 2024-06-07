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