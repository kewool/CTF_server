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

function editProblem(name){
    console.log(name)
    fetch('/admin/ctf/get', {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `problemName=${name}`
    }).then(function(response){
        console.log(response.data)
        return response.json()
    }).then((data) => {
        console.log(data);
    });
}