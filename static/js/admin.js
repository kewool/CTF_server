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

function editUser(url, id, name, csrfToken) {
    fetch(url, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${id}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("userId").value = id;
        document.getElementById("userPw").value = "";
        document.getElementById("userName").value = name;
        document.getElementById("userEmail").value = data["ctf_user_email"];
        document.getElementById("userSchool").value = data["ctf_user_school"];
        document.getElementById("userVisible").checked = data["ctf_user_visible"]? true:false;
        document.getElementById("userForm").style.display = "block";
    });
}

function editProblem(url, name, csrfToken, formURL) {
    fetch(url, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${name}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("problemName").readOnly = true;
        document.getElementById("problemName").value = name;
        document.getElementById("problemFlag").value = data["ctf_problem_flag"];
        let problemType = [];
        for(var i of document.getElementsByName("problemType")) problemType.push(i.value);
        problemType.map((item) => {
            if(data["ctf_problem_type"] === item) document.getElementById(item).checked = true;
        })
        document.getElementById("problemContents").innerText = data["ctf_problem_contents"];
        document.getElementById("problemFile").value = data["ctf_problem_file"];
        document.getElementById("problemVisible").checked = data["ctf_problem_visible"]? true:false;
        document.getElementById("problemForm").action = formURL;
        document.getElementById("problemSubmit").value = "add";
        document.getElementById("problemForm").style.display = "block";
    });
}

function addProblem(formURL){
    document.getElementById("problemName").readOnly = false;
    document.getElementById("problemName").value = "";
    document.getElementById("problemFlag").value = "";
    for (var i of document.getElementsByName("problemType")) i.checked = false;
    document.getElementById("problemContents").innerText = "";
    document.getElementById("problemFile").value = "";
    document.getElementById("problemVisible").checked = true;
    document.getElementById("problemForm").action = formURL;
    document.getElementById("problemForm").style.display = "block";
}