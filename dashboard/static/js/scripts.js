var endpoint = 'api/chart'


      $.ajax({
        method: "GET",
        url: endpoint,
        success: function(data){  /* "data" - response data */
            labels_bar = data.labels_bar
            data_bar = data.items_bar

            // labels_pie = data.labels_pie
            // data_pie = data.items_pie

            labels_line = data.labels_line
            // labels_line_early = data.labels_line_early
            // labels_line_late = data.labels_line_late
            // data_line_early = data.items_line_early
            // data_line_late = data.items_line_late

            setBarGraph()
            // setPieGraph()
            setLineGraph()
        },
        error: function(error_data){
          console.log("error")
          console.log(error_data)
        }
      })

      function PrintImage(e) {
        graph = e.target.getAttribute('id').replace('print','')
        console.log(graph)
        var canvas = document.getElementById(graph);
        var win = window.open();
        win.document.write("<br><img src='" + canvas.toDataURL() + "'/>");
        setTimeout(()=>win.print(),500)
        win.document.close();
    
    }
    // function printData(){
    //     console.log('here')
    //     var divToPrint=document.getElementById("student_record_table");
    //     newWin= window.open("");
    //     newWin.document.write(divToPrint.outerHTML);
    //     newWin.print();
    //     newWin.document.close();
    // }

      $('.print').on('click',PrintImage)
    //   $('#print_student_record').on('click',printData)

      function setBarGraph(){
        var ctx = document.getElementById('bargraph').getContext('2d');
        var myChart = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: labels_bar,
              datasets: [{
                  label: '',
                  data: data_bar,
                  backgroundColor: [
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                      'rgba(153, 102, 255, 0.2)',
                      'rgba(255, 159, 64, 0.2)'
                  ],
                  borderColor: [
                      'rgba(255, 99, 132, 1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                      'rgba(153, 102, 255, 1)',
                      'rgba(255, 159, 64, 1)'
                  ],
                  borderWidth: 1
              }]
          },
          options: {
                plugins:{
                    legend: {
                    display: false
                    }
                },
                scales: {
                    ticks: {
                        beginAtZero: true,
                    }
              }
          }
      });

      }

    //   function setPieGraph(){
    //     var ctx = document.getElementById('piegraph').getContext('2d');
    //     var myChart = new Chart(ctx, {
    //       type: 'pie',
    //       data: {
    //           labels: labels_pie,
    //           datasets: [{
    //               label: '',
    //               data: data_pie,
    //               backgroundColor: [
    //                   'rgba(255, 99, 132, 0.2)',
    //                   'rgba(54, 162, 235, 0.2)',
    //                   'rgba(255, 206, 86, 0.2)',
    //                   'rgba(75, 192, 192, 0.2)',
    //                   'rgba(153, 102, 255, 0.2)',
    //                   'rgba(255, 159, 64, 0.2)'
    //               ],
    //               borderColor: [
    //                   'rgba(255, 99, 132, 1)',
    //                   'rgba(54, 162, 235, 1)',
    //                   'rgba(255, 206, 86, 1)',
    //                   'rgba(75, 192, 192, 1)',
    //                   'rgba(153, 102, 255, 1)',
    //                   'rgba(255, 159, 64, 1)'
    //               ],
    //               borderWidth: 1
    //           }]
    //       },
    //       options: {
    //           scales: {
    //               y: {
    //                   beginAtZero: true
    //               }
    //           }
    //       }
    //   });
    //   }

      function setLineGraph(){
        var ctx = document.getElementById('linegraph').getContext('2d');
        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
              labels: labels_line,
              datasets: [{
                // label: labels_line_early,
                // data: data_line_early,
                backgroundColor: 'transparent',
                borderColor: 'rgba(93, 255, 114, 0.8)',
                borderWidth: 4
              },
            //   {
            //     label: labels_line_late,
            //     data: data_line_late,
            //     backgroundColor: 'transparent',
            //     borderColor: 'rgba(255, 99, 132, 1)',
            //     borderWidth: 4
            //   }
            ],
          },
          options: {
              elements:{
                  line: {
                      tension:0
                  }
              },
              scales: {
                  yAxes: [{
                      ticks: {
                          beginAtZero: true
                      }
                  }],
                  xAxes: [{
                    type: 'time',
                  }] 
                }
            }
  });
  }


document.body.addEventListener('htmx:configRequest', (event) =>{
    event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
})

/* DISABLE BUTTON */
var button = $('#event_submit');
var orig = [];

$.fn.getType = function () {
    return this[0].tagName == "INPUT" ? $(this[0]).attr("type").toLowerCase() : this[0].tagName.toLowerCase();
}

$("form :input").each(function () {
    var type = $(this).getType();
    var tmp = {
        'type': type,
        'value': $(this).val()
    };
    if (type == 'radio') {
        tmp.checked = $(this).is(':checked');
    }
    orig[$(this).attr('id')] = tmp;
});

$('form').bind('change keyup', function () {

    var disable = true;
    $("form :input").each(function () {
        var type = $(this).getType();
        var id = $(this).attr('id');

        if (type == 'text' || type == 'select') {
            disable = (orig[id].value == $(this).val());
        }

        if (!disable) {
            return false; // break out of loop
        }
    });

    button.prop('disabled', disable);
});

