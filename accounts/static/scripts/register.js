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