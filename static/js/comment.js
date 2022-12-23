function nameinput() {
    const username = window.localStorage.getItem('username');
    const commentname = document.getElementById("comment_username");

    commentname.value = username;
}