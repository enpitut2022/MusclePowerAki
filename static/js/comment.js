function display() {
    const username = window.localStorage.getItem('username');
    const chatname = document.getElementById("chat_username");

    chatname.value = username;
}

function nameinput() {
    const username = window.localStorage.getItem('username');
    const commentname = document.getElementById("comment_username");

    commentname.value = username;
}

window.onload = function() {
    display();
}