$(document).ready(async function() {

    const formatTime = (time) =>{
        time = time.split(':')
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
        if (x.timein && x.timeout) {
            return{...x,timein:formatTime(x.timein),timeout:formatTime(x.timeout)}
        } else {
            return{...x}
        }
    }).filter((item)=>{
        return item['admin'] != true;
    });
    
    var countTotal = dataSet.filter((item)=>{
        return item['admin'] != true;
    }).length
    // console.log(countdataSet);
    var earlyToday= dataSet.filter((item)=>{
        return item['timein_status'] == 'Early';
    }).length
    // console.log(earlyToday);

    var lateToday= dataSet.filter((item)=>{
        return item['timein_status'] == 'Late';
    }).length

    var signoutEarly= dataSet.filter((item)=>{
        return item['timeout_status'] == 'Early';
    }).length


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
            { "data": "email" },
            { "data": "college" },
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
                {   "className": "dt-center",   // align text center
                    "targets": "_all"
                },
           ]
    } );
    // display number of students
    document.getElementById("total_students").textContent = JSON.stringify(countTotal, undefined, 1)
    document.getElementById("early_today").textContent = JSON.stringify(earlyToday, undefined, 1)
    document.getElementById("late_today").textContent = JSON.stringify(lateToday, undefined, 1)
    document.getElementById("timeout_early").textContent = JSON.stringify(signoutEarly, undefined, 1)
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