function profile() {
    const username = window.localStorage.getItem('username');
    const pro_username = document.getElementById("profile_username");
    const edit_profile = document.getElementById("edit_profile");

    if (username != pro_username.innerHTML){
        edit_profile.style.display = "none";
    }
}

window.onload = function() {
    profile();
}