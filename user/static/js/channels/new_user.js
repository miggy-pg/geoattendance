document.addEventListener("DOMContentLoaded",async function(event) {
    id = document.querySelector('#userid').innerHTML
    localStorage.setItem('id',id)

    res = await fetch('http://' + window.location.host +'/students/')
    students = await res.json()
    me = students.find( ({user_idnumber})=> user_idnumber===localStorage.getItem('id') )
    if(me.timein){
        document.querySelector('#checkin-out').classList.add('signedin')
        document.querySelector('#checkin-out').style.background = 'red'
    }


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
        ip = document.querySelector('#ip').value
        socket.send(JSON.stringify({
            'action':'present',
            'ip':ip,
            'id':localStorage.getItem('id')
        }))
    }
 
    socket.onerror = function (e) {
        console.log("error", e)
    }

    socket.onclose = function (e) {
        console.log("close", e)
    }

    socket.onmessage = function (e) {
        var data = JSON.parse(e.data)
        console.log("data:", data)
        id = localStorage.getItem('id')
        if(data.message && data.id == id){
            document.querySelector('#checkin-out').classList.add('signedin')
            document.querySelector('#checkin-out').style.background = 'red'
            alert(data.message)
        }
    }

    $('#checkin-out').click((e)=>{
        let action
        if(e.target.classList.contains('signedin')) {
            e.target.classList.remove('signedin')
            action = 'timeout'
            e.target.style.background = 'green'
        }
        else{
            e.target.classList.add('signedin')
            action = 'timein'
            e.target.style.background = 'red'
        }

        let time = new Date().toLocaleTimeString('en-GB')
        // console.log(formattedDate)
        socket.send(JSON.stringify({
            'action':action,
            'time': time,
            'id':localStorage.getItem('id')
        }))
    })


    document.querySelector('.logout-text-link').addEventListener('click',()=>{
        socket.send(JSON.stringify({
            'action':'unpresent',
            'id':localStorage.getItem('id')
        }))
      localStorage.removeItem('id')
      console.log(window.location.host)
      window.location.href = window.location.host + '/user/logout/'
  })
});