const socket = io();

socket.on('connect', function() {
    console.log('Связь есть');
});

socket.on('person_respons', function(data) {

    const popup = document.getElementById('popup-block');
    const client_number = `<p id="ticket-number">${data}</p>`;
    popup.innerHTML = client_number;
});

$("button").on('click', function() {
    var value = $(this).val();
    var username = $("#username").val();
    var userLastname = $("#userLastname").val();
    var birthdate = $("#birthdate").val();
    var phone = $("#phone").val();
    
    if (username && birthdate && phone && userLastname) {
        console.log(value, username, userLastname, phone, birthdate);
        socket.emit('next_client', {operation: value, username: username, userLastname: userLastname,  phone: phone, birthdate: birthdate});
        
    } 
    else {
        $(document).ready(function(){
            PopUpHide();
            });
    }
});
