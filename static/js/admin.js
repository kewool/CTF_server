let problem = document.getElementById("problem");
let users = document.getElementById("users");

function problemList(){
    problem.style.display = "block";
    users.style.display = "none";
}

function userList(){
    problem.style.display = "none";
    users.style.display = "block";
}

function addProblem(){
    let problemEdit = document.getElementById("problemEdit");
    let addCtfForm = document.getElementById("addProblemForm");
    problemEdit.innerHTML = "";
    addCtfForm.style.display = "block";
}

function addProblemHide(){
    let addCtfForm = document.getElementById("addProblemForm");
    addCtfForm.style.display = "none";
}