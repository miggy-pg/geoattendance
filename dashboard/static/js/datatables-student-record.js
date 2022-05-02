$(document).ready(async function() {

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
        searching: false,       //hide search bar
        data: dataSet,      //import dataset
        createdRow: function(row, data, dataIndex) {
            $(row).attr('data-id', data.user_idnumber);
        },
        columns: [
            { "data": "user_idnumber" },
            { "data": "user_lname" },
            { "data": "user_fname" },
            { "data": "email" },
            { "data": "college" },
            { "data": "course" },
            { "data": "yearlevel" },
            { "data": "user_gender" },
            { "data": "yearlevel" },
            { "data": "yearlevel" },
        ],
        buttons: [
        ],
        "columnDefs":
           [
               {
                   "targets": [3],      //remove college column
                   "visible": false,
                   "searchable": false,
               },
               {
                    "targets": [6],     //remove gender column
                    "visible": false,
                    "searchable": false,
                },
                {
                    "targets":[10],
                    "defaultContent": "<a href='#'>A</a>"
                },
                {
                    "targets":[11],
                    "defaultContent": "<a href='#'>B</a>"
                },
                {   "className": "dt-center",   // align text center
                    "targets": "_all"
                },
           ],
           buttons: [
            'excel', 'pdf','csv','print','colvis'
        ],
    } );
});