function showImage(imgName) {
    let divImg = document.getElementById("show_image");
    let divImgSrc = document.getElementById("show_image_img");
    divImg.style.display = 'block';
    divImg.style.pointerEvents = 'all';
    divImg.style.top = '50%';
    divImg.style.left = '50%';
    divImg.style.transform = 'translate(-50%, -50%)';
    divImg.style.position = 'fixed';
    divImgSrc.src = 'static/img/' + imgName;
    divImg.style.zIndex = '3000';
    document.getElementById("invisible").style.display = 'block';
}

$(document).ready(function() {
    document.getElementById("invisible").addEventListener("click", function() {
        let showImg = document.getElementById("show_image");
        showImg.style.display = 'none';
        showImg.style.pointerEvents = 'all';
        document.getElementById("invisible").style.display = 'none';
    }, false);

    document.getElementById("show_image_img").addEventListener("click", function(e) {
        e.stopPropagation();
    }, false);

    document.getElementById("search_announces_image").addEventListener("click", function(e) {
        e.stopPropagation();
        showImage("search_announces.png");
    }, false);

    document.getElementById("view_announces_image").addEventListener("click", function(e) {
        e.stopPropagation();
        showImage("view_announces.png");
    }, false);
});