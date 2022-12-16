function display() {
    const username = window.localStorage.getItem('username');
    const chatname = document.getElementById("chat_username");

    chatname.value = username;
}

window.onload = function() {
    display();
}