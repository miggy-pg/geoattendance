$(document).ready(async function() {

    const formatTime = (time) =>{
        time = time.split(":")
        hour = parseInt(time[0])
        AmOrPm = hour >= 12 ? 'pm' : 'am';
        hour = (hour % 12) || 12
        minutes = time[1].length<2?`0${time[1]}`:time[1] // starts with zero if minutes only one digit

        formattedTime = `${hour}:${minutes} ${AmOrPm}`
        return formattedTime
    }

    res = await fetch('http://' + window.location.host +'/students/')
    var dataSet = await res.json();  
    var dataSet = dataSet.map((x) => {
        if (x.timein && x.timeout) {
            return{...x,timein:formatTime(x.timein),timeout:formatTime(x.timeout)}
        } else {
            return{...x}
        }
    }).filter((item)=>{
        return item['admin'] != true;
    });
    
    $('#student_record_table').DataTable( {
        dom: 'Bfrtip',      // The B is the Buttons extension and it tell DataTables where to put each element in the DOM that it creates
        data: dataSet,      //import dataset
        createdRow: function(row, data, dataIndex) {
            $(row).attr('data-id', data.user_idnumber);
        },
        columns: [
            { "data": "ip" },
            { "data": "user_idnumber" },
            { "data": "user_fname" },
            { "data": "user_lname" },
            { "data": "college" },
            { "data": "course" },
            { "data": "yearlevel" },
            { "data": "user_gender" },
            { "data": "timein" } ,
            { "data": "timein_status" },
            { "data": "timeout" },
            { "data": "timeout_status" },
            { "data": "status" }
        ],
        "columnDefs":
        [
             {   "className": "dt-center",   // align text center
                 "targets": "_all"
             },
        ],
        buttons: [
            {
                extend: 'pdfHtml5',
                orientation: 'landscape',
                pageSize: 'LEGAL'
            },
            'csv','print','colvis',
        ],
    } );
});