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

    res = await fetch('http://' + window.location.host +'/present/')
    dataSet = await res.json()
    // console.log(dataSet)
    dataSet = dataSet.map((x)=>{
        if(x.timein && x.timeout)
        return{...x,timein:formatTime(x.timein),timeout:formatTime(x.timeout)}
        else
        return{...x}
    })
    // console.log(dataSet)

    var t = $('#table').DataTable( {
        dom: 'Bfrtip',
        data: dataSet,
        createdRow: function (row, data, dataIndex) {
            $(row).attr('data-id', data.user_idnumber);
        },
        columns: [
            { "data": "user_idnumber" },
            { "data": "user_fname" },
            { "data": "user_lname" },
            { "data": "college" },
            { "data": "course" },
            { "data": "yearlevel" },
            { "data": "user_gender" },
            { "data": "timein",
                render: function ( data, type, row ) {
                    return row.timein + '(' + row.timein_status + ')';
                }
            },
            { "data": "timein_status" },
            { "data": "timeout",
                render: function ( data, type, row ) {
                    return row.timeout + '(' + row.timeout_status + ')';
                }
            },
            { "data": "timeout_status" },
            { "data": "status" }
        ],
        "columnDefs":
        [
            {
                "targets": [8],      //hide signin_status column
                "visible": false,
                "searchable": false,
            },
            {
                 "targets": [10],     //hide signout_status column
                 "visible": false,
                 "searchable": false,
             },
             {   "className": "dt-center",   // align text center
                 "targets": "_all"
             },
        ],
        buttons: [
            'excel', 'pdf','csv','print','colvis'
        ],
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

    socket.onmessage = async function (e) {
        var data = JSON.parse(e.data)
        console.log("data:", data.action)
        const isMe = (stud) => {
            return stud.user_idnumber == data.id
        }

        // to avoid variable conflict inside t.rows(function)
        var globalid = data.id

        if(data.action==='present'){
            res = await fetch('http://' + window.location.host + '/present/')
            studs = await res.json()
            me = studs.find(isMe)
            console.log('this me', me)
            const {
                user_idnumber,
                user_fname,
                user_lname,
                college,
                course,
                yearlevel,
                user_gender,
                timein,
                timein_status,
                timeout,
                timeout_status,
                status
            } = me

            var rs = t.rows( function ( idx, data, node ) {return data.user_idnumber === globalid ? true : false;} ).data();

            // only add if it does not exist
            !rs[0] && t.row.add({
                user_idnumber,
                user_fname,
                user_lname,
                college,
                course,
                yearlevel,
                user_gender,
                timein,
                timein_status,
                timeout,
                timeout_status,
                status
            }).draw(false)

            console.log(rs[0])
        }

        if(data.action==='unpresent'){
            t.row( function ( idx, data, node ) {return data.user_idnumber === globalid ? true : false;} ).remove().draw();
        }
        if(!data.action)
        return // code below won't be executed because data.action does not exist meaning timeout has been rejected
            
        const formattedTime = formatTime(data.time)
        index = data.action==='timein'? 7:9 // signin column in index 7 signout column in index 9
        console.log('here') 

        // setting the specific field in the table for timein and timeout
        $(`tr[data-id=${data.id}]`)[0].children[index].innerHTML = formattedTime
        // setting the status field to late or early
        $(`tr[data-id=${data.id}]`)[0].children[8].innerHTML = data.activity > data.activity_start_time? 'Late':'Early'
        $(`tr[data-id=${data.id}]`)[0].children[10].innerHTML = data.activity > data.activity_end_time? 'Late':'Early'

    }
} );