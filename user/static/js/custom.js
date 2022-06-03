$("#id_school").change(function () {
    const url = $("#registerForm").attr("data-course-url");  // get the url of the `load_cities` view
    const countryId = $(this).val();  // get the selected country ID from the HTML input

    $.ajax({                       // initialize an AJAX request
        url: url,                    // set the url of the request (= /persons/ajax/load-cities/ )
        data: {
            'college_id': countryId       // add the country id to the GET parameters
        },
        success: function (data) {   // `data` is the return of the `load_cities` view function
            $("#id_course").html(data);  // replace the contents of the city input with the data that came from the server
        }
    });
});

/* ==== FEEDBACK BOX ==== */
document.getElementById("feedback-popup-btn").addEventListener("click",function(){
document.getElementsByClassName("feedback")[0].classList.add("active");
});
    
document.getElementById("send-popup-btn").addEventListener("click",function(){
document.getElementsByClassName("feedback")[0].classList.remove("active");
});
document.getElementById("feedback-cancel-btn").addEventListener("click",function(){
document.getElementsByClassName("feedback")[0].classList.remove("active");
});

/* ==== DIALOG BOX ==== */
document.getElementById("open-popup-btn").addEventListener("click",function(){
document.getElementsByClassName("popup")[0].classList.add("active");
});
   
document.getElementById("logout-popup-btn").addEventListener("click",function(){
document.getElementsByClassName("popup")[0].classList.remove("active");
});
document.getElementById("cancel-popup-btn").addEventListener("click",function(){
document.getElementsByClassName("popup")[0].classList.remove("active");
});
  
sessionStorage.setItem('default', '#5c5c5c');
sessionStorage.setItem('green', '#006702');
sessionStorage.setItem('red', '#006702');