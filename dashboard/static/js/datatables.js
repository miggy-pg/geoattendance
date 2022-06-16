$(document).ready(async function() {

    const formatTime = (time) =>{
        time = time.split(":")
        hour = parseInt(time[0])
        AmOrPm = hour >= 12 ? 'PM' : 'AM';
        hour = (hour % 12) || 12
        minutes = time[1].length<2?`0${time[1]}`:time[1] // starts with zero if minutes only one digit

        formattedTime = `${hour}:${minutes} ${AmOrPm}`
        return formattedTime
    }

    res = await fetch('http://' + window.location.host +'/students/')
    var dataSet = await res.json();  
    var dataSet = dataSet.map((x) => {
        if (x.timein && x.timeout && x.prev_timeout) {
            return{...x, timein:formatTime(x.timein), timeout:formatTime(x.timeout), prev_timeout:formatTime(x.prev_timeout)}
        } else {
            return{...x}
        }
    }).filter((item)=>{
        return item['admin'] != true;
    });
    
    $('#student_record_table').DataTable( {
        dom: '<"toolbar">Bfrtip',      // The B is the Buttons extension and it tell DataTables where to put each element in the DOM that it creates
        data: dataSet, 
        "bLengthChange": false,
        createdRow: function(row, data, dataIndex) {
            $(row).attr('data-id', data.user_idnumber);
        },
        columns: [
            { "data": "user_idnumber" },
            { "data": "user_fname" },
            { "data": "user_lname" },
            { "data": "email" },
            { "data": "college" },
            { "data": "yearlevel" },
            { "data": "user_gender" },
            { "data": "timein" },
            { "data": "timein_status" },
            { "data": "timeout",
                render: function ( data, type, row ) {
                    if(row.prev_timeout == null){
                        return row.timeout;
                    }
                    else{
                        return row.timeout + '<br>' + '<p style="color:red; font-weight:700;">' + '(' + row.prev_timeout + ')' + '</p>';
                    }
                } 
            },
            { "data": "timeout_status" },
            { "data": "status" }
        ],
        "columnDefs": [
             {   "className": "dt-center",   // align text center
                 "targets": "_all"
             },
        ],
        buttons: [
            {
                extend: 'pdfHtml5',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                text: '<b>PDF</b>&nbsp&nbsp&nbsp<i class="fa fa-file-pdf-o"></i>',
                titleAfter: 'PDF',
            },
            {
                extend: 'csvHtml5',
                text: '<b>CSV</b>&nbsp&nbsp&nbsp<i class="fa fa-file-excel-o"></i>',
                titleAfter: 'CSV',
            }, 
            {
                extend: 'print',
                text: '<b>Print</b>&nbsp&nbsp&nbsp<i class="fa fa-print"></i>',
                titleAfter: 'Print',
            },
            {
                extend: 'colvis',
                text: '<b>Column Visibility</b>&nbsp&nbsp&nbsp<i class="fa fa-filter"></i>',
                titleAfter: 'Colvis',
            },
        ],
        language: {
            searchPlaceholder: "Search",
            search: "",
        },
    } );
    $('div.toolbar').html('<b>Export</b>&nbsp&nbsp&nbsp');
});