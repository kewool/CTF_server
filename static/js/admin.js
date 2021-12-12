let problem = document.getElementById("problem");
let users = document.getElementById("users");
let solved = document.getElementById("solved");
let log = document.getElementById("log");

function problemList(){
    problem.style.display = "block";
    users.style.display = "none";
    solved.style.display = "none";
    log.style.display = "none";
}

function userList(){
    problem.style.display = "none";
    users.style.display = "block";
    solved.style.display = "none";
    log.style.display = "none";
}

function solvedList(){
    problem.style.display = "none";
    users.style.display = "none";
    solved.style.display = "block";
    log.style.display = "none";
}

function logList(){
    problem.style.display = "none";
    users.style.display = "none";
    solved.style.display = "none";
    log.style.display = "block";
}

function isClick(){
    this.className += "clicked"
}

function updateUserGet(url, id, name, csrfToken) {
    fetch(url, {
        method: 'POST',
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
        document.getElementById("userScore").innerText = data["ctf_user_score"];
        document.getElementById("userSolved").innerText = data["ctf_user_solved"];
        document.getElementById("userTry").innerText = data["ctf_user_try"];
        document.getElementById("userVisible").checked = data["ctf_user_visible"]? true:false;
        document.getElementById("userRegisterDate").innerText = data["ctf_user_register_date"];
        document.getElementById("userForm").style.display = "block";
    });
}

function updateProblemGet(url, name, csrfToken, formURL) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${name}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("result").innerText = "";
        document.getElementById("problemName").readOnly = true;
        document.getElementById("problemName").value = name;
        document.getElementById("problemFlag").value = data["ctf_problem_flag"];
        let problemType = [];
        for(var i of document.getElementsByName("problemType")) problemType.push(i.value);
        problemType.map((item) => {
            if(data["ctf_problem_type"] === item) document.getElementById(item).checked = true;
        })
        document.getElementById("problemContents").value = data["ctf_problem_contents"];
        document.getElementById("problemFile").value = data["ctf_problem_file"];
        document.getElementById("problemVisible").checked = data["ctf_problem_visible"]? true:false;
        document.getElementById("problemSubmit").value = "update";
        document.getElementById("problemSubmit").setAttribute("onclick",`updateProblem("${formURL}", "${csrfToken}")`);
        document.getElementById("problemDelete").style.display = "inline-block";
        document.getElementById("problemForm").style.display = "block";
    });
}

function updateProblem(url, csrfToken){
    let type, visible;
    for(var i of document.getElementsByName("problemType")) if(i.checked === true) type = i.value;
    if(document.getElementById("problemVisible").checked === true) visible = "visible";
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body:`problemName=${document.getElementById("problemName").value}&problemFlag=${document.getElementById("problemFlag").value}&problemType=${type}&problemContents=${document.getElementById("problemContents").value}&problemFile=${document.getElementById("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("result").innerText = data["result"];
    })
}

function addProblemForm(formURL, csrfToken, getURL, updateURL){
    document.getElementById("result").innerText = "";
    document.getElementById("problemName").readOnly = false;
    document.getElementById("problemName").value = "";
    document.getElementById("problemFlag").value = "";
    for (var i of document.getElementsByName("problemType")) i.checked = false;
    document.getElementById("problemContents").value = "";
    document.getElementById("problemFile").value = "";
    document.getElementById("problemVisible").checked = true;
    document.getElementById("problemSubmit").setAttribute("onclick",`addProblem("${formURL}", "${csrfToken}", "${getURL}", "${updateURL}")`);
    document.getElementById("problemSubmit").value = "add";
    document.getElementById("problemDelete").style.display = "none";
    document.getElementById("problemForm").style.display = "block";
}

function addProblem(url, csrfToken, getURL, updateURL){
    let type, visible;
    for(var i of document.getElementsByName("problemType")) if(i.checked === true) type = i.value;
    if(document.getElementById("problemVisible").checked === true) visible = "visible";
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body:`problemName=${document.getElementById("problemName").value}&problemFlag=${document.getElementById("problemFlag").value}&problemType=${type}&problemContents=${document.getElementById("problemContents").value}&problemFile=${document.getElementById("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data)=>{
        let div = document.createElement("div");
        div.className = "problemNameBox";
        div.setAttribute("onclick", `updateProblemGet("${getURL}", "${data["result"]}", "${csrfToken}", "${updateURL}")`);
        div.innerText = data["result"];
        document.getElementsByClassName("problemNameBox")[0].before(div);
        document.getElementById("problemSubmit").value = "update";
        document.getElementById("problemSubmit").setAttribute("onclick",`updateProblem("${updateURL}", "${csrfToken}")`);
    })
}

function deleteProblem(url, csrfToken){
    let problemName = document.getElementById("problemName").value;
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body:`problemName=${problemName}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById(problemName).remove();
        document.getElementById("problemForm").style.display = "none";
        document.getElementById("result").innerText = data["result"];
    })
}