$(document).ready(async function() {

    const formatTime = (time) =>{
        time = time.split(':')
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
    
    var countDataSet = dataSet.filter((item)=>{
        return item['admin'] != true;
    }).length
    // console.log(countdataSet);

    // display number of students
    document.getElementById("total_students").textContent = JSON.stringify(countDataSet, undefined, 1)

    $('#attendance_dashboard').DataTable( {
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
            { "data": "college" },
            { "data": "course" },
            { "data": "yearlevel" },
            { "data": "user_gender" },
            { "data": "timein" },
            { "data": "timeout" },
            { "data": "status" },            
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
                {   "className": "dt-center",   // align text center
                    "targets": "_all"
                },
           ]
    } );
    
    // $('.dataTables_filter')[0].style.textAlign = 'start'

    var ws_scheme = (window.location.protocol === 'https:' ? 'wss' : 'ws') 
    var endpoint = ws_scheme + '://' + window.location.host + '/ws/new_user/'
    console.log(endpoint)
    // 1. Use ReconnectingWebSocket (auto-reconnect upon disconnect)
    const socket = new ReconnectingWebSocket(endpoint) // 2
    // 2. Use default WebSocket
    // const socket = new WebSocket(endpoint) // 2

    // 3
    socket.onopen = function (e) {
        console.log("open", e);
    }
 
    socket.onerror = function (e) {
        console.log("error", e)
    }

    socket.onclose = function (e) {
        console.log("close", e)
    }

    socket.onmessage = function (e) {
        var data = JSON.parse(e.data)
        console.log("data:", data.action)
        if(!data.action)
        return // code below won't be executed because data.action does not exist meaning timeout has been rejected
        
        const formattedTime = formatTime(data.time)
        index = data.action==='timein'? 7:8 // signin column in index 7 signout column in index 8
        console.log('here')
        // setting the specific field in the table for timein and timeout
        $(`tr[data-id=${data.id}]`)[0].children[index].innerHTML = formattedTime
        // setting the status field to late or early
        $(`tr[data-id=${data.id}]`)[0].children[9].innerHTML = data.time > data.activity_start_time? 'late':'early'

    }
} );