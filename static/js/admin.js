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

function editUser(url, id, csrfToken) {
    addProblemHide()
    fetch(url, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${id}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("updateProblemName").value = id;
        document.getElementById("updateProblemFlag").value = data["ctf_problem_flag"];
        let problemType = [];
        for(var i of document.getElementsByName("updateProblemType")) problemType.push(i.value);
        problemType.map((item) => {
            item = item.charAt(0).toUpperCase() + item.slice(1);
            if(data["ctf_problem_type"].charAt(0).toUpperCase() + data["ctf_problem_type"].slice(1) === item) document.getElementById(`updateProblemType${item}`).checked = true;
        })
        document.getElementById("updateProblemContents").innerText = data["ctf_problem_contents"];
        document.getElementById("updateProblemFile").value = data["ctf_problem_file"];
        if(data["ctf_problem_visible"] === 1) document.getElementById("updateProblemVisible").checked = true;
        else if(data["ctf_problem_visible"] === 0) document.getElementById("updateProblemVisible").checked = false;
        document.getElementById("submit").value = "update";
        document.getElementById("problemEdit").style.display = "block";
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
        if(data["ctf_problem_visible"] === 1) document.getElementById("problemVisible").checked = true;
        else if(data["ctf_problem_visible"] === 0) document.getElementById("problemVisible").checked = false;
        document.getElementById("problemForm").action = formURL;
        document.getElementById("submit").value = "add";
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