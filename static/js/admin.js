let ctf = document.getElementById("ctf");
let users = document.getElementById("users");

function ctfList(){
    ctf.style.display = "block";
    users.style.display = "none";
}

function userList(){
    ctf.style.display = "none";
    users.style.display = "block";
}

function addCtf(){
    let addCtfForm = document.getElementById("addCtfForm");
    addCtfForm.style.display = "block";
}