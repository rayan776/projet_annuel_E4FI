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

function checkIfUsernameAvailable() {
    let formData = new FormData();
    let username = document.getElementById("input_username").value;

    formData.append('username', username);

    const request = new Request('http://127.0.0.1:8000/accounts/checkUsername/', {
        method: 'POST',
        body: formData,
    });
        
    fetch(request)
        .then(response => response.json())
        .then(result => {
            if (result["username_exists"]) {
                document.getElementById("username_exists").innerText = "Ce nom d'utilisateur est déjà pris.";
            }
            else {
                document.getElementById("username_exists").innerText = "";
            }
        })
}

$(document).ready(function() {

    createListeners(document.getElementById("password-help"), "Votre mot de passe doit faire au moins 8 caractères et contenir au moins: 1 caractère spécial, 1 chiffre, 1 minuscule, 1 majuscule.");
    createListeners(document.getElementById("secret-q-help"), "Votre question secrète ainsi que sa réponse vous permettront de réinitialiser votre mot de passe. Vous ne pourrez plus les modifier : assurez vous de ne pas les oublier. La question secrète ne doit pas être vide.");
    createListeners(document.getElementById("secret-a-help"), "Votre réponse secrète ne doit pas être vide.");

    let inputUsername = document.getElementById("input_username");
    inputUsername.addEventListener("input", checkIfUsernameAvailable, false);

    let nameHelps = document.getElementsByClassName("name-help");
    for (let i=0; i<nameHelps.length; i++) {
        createListeners(nameHelps[i], "Caractères autorisés : lettres, espaces et tirets. 50 caractères max.");
    }
    
    document.getElementById("info").addEventListener("click", function(e) {
        e.stopPropagation();
    }, false);

    document.body.addEventListener("click", function() {
        closeInfo();
    }, false);
});