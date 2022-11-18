
function save() {
    const username = document.getElementById("username");

    window.localStorage.setItem('username', username.value);
}

function display() {
    const username = window.localStorage.getItem('username');
    const textarea = document.getElementById("username");

    textarea.value = username;
}

window.onload = function() {
    display();
}