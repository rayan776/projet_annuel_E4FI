function checkSecretAnswer() {
    let secretAnswer = document.getElementById("secretAnswer").value;
    let idUser = document.getElementById("idUser_secretAnswer").value;

    let formData = new FormData();
    formData.append('secretAnswer', secretAnswer);
    formData.append('idUser', idUser);

    const request = new Request('http://127.0.0.1:8000/accounts/checkSecretAnswer/', {
        method: 'POST',
        body: formData,
    });

    fetch(request)
        .then(response => response.json())
        .then(result => {
            if (result["isSecretAnswerOk"]) {
                document.getElementById("secret_answer_result").innerText = "Bonne réponse !"
                document.getElementById("secret_answer_result").style.color = 'green';
                document.getElementById("new_mdp_section").style.opacity = 1;
                document.getElementById("new_mdp_section").style.height = '250px';
                document.getElementById("token").value = result["new_pwd_token"];
                document.getElementById("idUser_resetPwd").value = result["idUser"];
                document.getElementById("reset-pwd-btn-answer").style.backgroundColor = 'white';
                document.getElementById("reset-pwd-btn-answer").style.color = 'blue';
                document.getElementById("reset-pwd-btn-answer").style.border = '1px solid blue';
                document.getElementById("reset-pwd-btn-answer").disabled = true;
                document.getElementById("secretAnswer").value = "";
                document.getElementById("secretAnswer").disabled = true;
                document.getElementById("reset_pwd_btn").style.pointerEvents = 'all';
            }
            else {
                document.getElementById("secret_answer_result").innerText = "Mauvaise réponse !";
                document.getElementById("secret_answer_result").style.color = 'red';
                resetNewMdpSection();
            }
        })


}

function resetSecretAnswerSection() {
    document.getElementById("secret_answer_result").innerText = "";
    document.getElementById("secretAnswer").value = "";
    document.getElementById("secretQuestion").innerText = "";
}

function resetNewMdpSection() {
    document.getElementById("new_mdp_section").style.opacity = 0;
    document.getElementById("new_mdp_section").style.height = '0px';
    document.getElementById("token").value = "";
    document.getElementById("idUser_resetPwd").value = "";
    document.getElementById("new_pwd").value = "";
    document.getElementById("new_pwd_conf").value = "";
}

function checkUsername() {
    let username = document.getElementById("username").value;

    let formData = new FormData();
    formData.append('username', username);

    const request = new Request('http://127.0.0.1:8000/accounts/checkUsername/', {
        method: 'POST',
        body: formData,
    });
    
    fetch(request)
            .then(response => response.json())
            .then(result => {
                let secret_question_section = document.getElementById("secret_question_section");
                resetSecretAnswerSection();
                resetNewMdpSection();
                if (result["username_exists"]) {
                    secret_question_section.style.height = '250px';
                    secret_question_section.style.opacity = 1;
                    document.getElementById("secretQuestion").innerText = result["secretQuestion"];
                    document.getElementById("idUser_secretAnswer").value = result["idUser"];
                    document.getElementById("username_not_found").innerText = "";
                    document.getElementById("reset-pwd-btn-check-username").style.backgroundColor = 'white';
                    document.getElementById("reset-pwd-btn-check-username").style.color = 'blue';
                    document.getElementById("reset-pwd-btn-check-username").style.border = '1px solid blue';
                    document.getElementById("reset-pwd-btn-check-username").disabled = true;
                    document.getElementById("username").disabled = true;
                }
                else {
                    secret_question_section.style.height = '0px';
                    secret_question_section.style.opacity = 0;
                    document.getElementById("secretQuestion").innerText = "";
                    document.getElementById("idUser_secretAnswer").value = "";
                    document.getElementById("username_not_found").innerText = "Cet utilisateur n'existe pas."
                }
            })
}

$(document).ready(function () {
    document.getElementById("reset-pwd-btn-check-username").addEventListener("click", function() {
        checkUsername();
    }, false);

    document.getElementById("reset-pwd-btn-answer").addEventListener("click", function() {
        checkSecretAnswer();
    }, false);

    let closePopup = document.getElementById("btnClosePopup");
    if (closePopup) { 
        closePopup.addEventListener("click", function () {
            closeBox("resetPwdPopup");
        }, false);
    }

    createListeners(document.getElementById("password-help"), "Votre mot de passe doit faire au moins 8 caractères et contenir au moins: 1 caractère spécial, 1 chiffre, 1 minuscule, 1 majuscule.");

    document.getElementById("info").addEventListener("click", function(e) {
        e.stopPropagation();
    }, false);

    document.body.addEventListener("click", function() {
        closeInfo();
    }, false);
    
});