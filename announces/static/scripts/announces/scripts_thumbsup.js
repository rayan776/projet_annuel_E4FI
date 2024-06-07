$(document).ready(function(e) {
    let thumbs = document.getElementsByClassName("thumbs");

    for (let i=0; i<thumbs.length; i++) {
            $(thumbs[i]).click(function(e) {

                e.preventDefault();
                let formData = new FormData();
                formData.append('rate_review', e.currentTarget.id);
                let csrfTokenValue = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
                const request = new Request('http://127.0.0.1:8000/announces/rate_review/', {
                    method: 'POST',
                    body: formData,
                    headers: {'X-CSRFToken': csrfTokenValue}
                });

            fetch(request)
                    .then(response => response.json())
                    .then(result => {
                        if (result["ok"]) {
                            document.getElementById(result["idDivScorePlus"]).innerText = result["score_plus"];
                            document.getElementById(result["idDivScoreMinus"]).innerText = result["score_minus"];
                        }
                    })
            });
    }
    
});