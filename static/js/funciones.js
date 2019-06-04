// token de conexion

$(function(){
    //Obtenemos la información de csfrtoken que se almacena por cookies en el cliente
    var csrftoken = getCookie('csrftoken');

    //Agregamos en la configuración de la funcion $.ajax de Jquery lo siguiente:
    $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                            // Send the token to same-origin, relative URLs only.
                            // Send the token only if the method warrants CSRF protection
                            // Using the CSRFToken value acquired earlier
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
    });

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

// usando jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


    function csrfSafeMethod(method) {
        // estos métodos no requieren CSRF
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
});

// fin token


// Grab elements, create settings, etc.
var video = document.getElementById('video');
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
var img = document.getElementById('img');

// Get access to the camera!
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Not adding `{ audio: true }` since we only want video now
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        //video.src = window.URL.createObjectURL(stream);
        video.srcObject = stream;
        video.play();

    });
}

jQuery(document).ready(function($){

	$("#btnEntrar").click(() => {
		alert('Entró');
	});

  var proceso;
  var contador = 0;
  var puntos = '';

  function takeFrame(){
    contador++;
    b64 = canvas.toDataURL('image/jpeg');
    // console.log(b64);
    // img.src = b64;
    context.drawImage(video,0,0,320,240);
    parametros = {
      'base' : b64
    };
    $.ajax({
      url:'detectar/',
      type: 'POST',
      data: parametros,
      success: function(data){
        if (data == 'None') {
          switch (contador) {
            case 1:
              puntos = '.';
              break;
            case 2:
              puntos = '..';
              break;
            case 3:
              puntos = '...';
              break;
            default:
              contador=0;
              puntos = '';
              break;
          }
          $("#msge").html('Leyendo'+puntos);
        }else {
          // clearInterval(proceso);
          $("#msge").html(data);
          // proceso = setInterval(takeFrame,1000);
        }

      }
    });
  }



  proceso = setInterval(takeFrame,1000);

});
