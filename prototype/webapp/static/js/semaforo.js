
function set_sentimaforo() {
    var ps   = document.querySelectorAll(".post_content p");
    var score_positivo = parseFloat(document.querySelector(".score-positivo").innerHTML);
    var score_negativo = parseFloat(document.querySelector(".score-negativo").innerHTML) * -1;

    var result = "neutral";
    if (score_positivo - score_negativo < 5 && score_positivo - score_negativo > -5){
        result = "neutral";
    }else if (score_positivo > score_negativo){
        result = "positive";
        if (score_positivo > 9.9 && score_positivo < 35){
            result = "slightly-" + result;
        }else if (score_positivo > 79.9){
            result = "very-" + result;
        }
    }else{
        result = "negative";
        if (score_negativo > 9.9 && score_negativo < 35){
            result = "slightly-" + result;
        }else if (score_negativo > 79.9){
            result = "very-" + result;
        }
    }

    var glow = "";
    if ( result.indexOf("positive") > -1 ) {
        glow = "verde";
    } else if ( result.indexOf("negative") > -1 ) {
        glow = "rojo";
    } else { 
        glow = "blue";
    } 
 
    spans = document.querySelectorAll(".sentimaforo span." + result);

    for (var i = 0; i < spans.length; i++){
        var span = spans[i];
        span.setAttribute("class", span.getAttribute("class") + " glow-" + glow + " selected" );
    }
}
