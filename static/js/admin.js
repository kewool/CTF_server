function $(name) {
    return document.getElementById(name);
}

let problem = $("problem");
let users = $("users");
let notice = $("notice");
let solved = $("solved");
let log = $("log");

function problemList() {
    problem.style.display = "block";
    users.style.display = "none";
    notice.style.display = "none";
    solved.style.display = "none";
    log.style.display = "none";
}

function userList() {
    problem.style.display = "none";
    users.style.display = "block";
    notice.style.display = "none";
    solved.style.display = "none";
    log.style.display = "none";
}

function noticeList() {
    problem.style.display = "none";
    users.style.display = "none";
    notice.style.display = "block";
    solved.style.display = "none";
    log.style.display = "none";
}

function solvedList() {
    problem.style.display = "none";
    users.style.display = "none";
    notice.style.display = "none";
    solved.style.display = "block";
    log.style.display = "none";
}

function logList() {
    problem.style.display = "none";
    users.style.display = "none";
    notice.style.display = "none";
    solved.style.display = "none";
    log.style.display = "block";
}

function isClick() {
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
    }).then((res) => res.json()).then((data) => {
        $("userId").value = id;
        $("userName").value = name;
        $("userEmail").value = data["ctf_user_email"];
        $("userSchool").value = data["ctf_user_school"];
        $("userScore").innerText = data["ctf_user_score"];
        $("userSolved").innerText = data["ctf_user_solved"];
        $("userTry").innerText = data["ctf_user_try"];
        $("userVisible").checked = data["ctf_user_visible"] ? true : false;
        $("userRegisterDate").innerText = data["ctf_user_register_date"];
        $("userForm").style.display = "block";
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
    }).then((res) => res.json()).then((data) => {
        $("result").innerText = "";
        $("problemName").readOnly = true;
        $("problemName").value = name;
        $("problemFlag").value = data["ctf_problem_flag"];
        let problemType = [];
        for (var i of document.getElementsByName("problemType")) problemType.push(i.value);
        problemType.map((item) => {
            if (data["ctf_problem_type"] === item) $(item).checked = true;
        })
        $("problemContents").value = data["ctf_problem_contents"];
        $("problemFile").value = data["ctf_problem_file"];
        $("problemVisible").checked = data["ctf_problem_visible"] ? true : false;
        $("problemSubmit").value = "update";
        $("problemSubmit").setAttribute("onclick", `updateProblem("${formURL}", "${csrfToken}")`);
        $("problemDelete").style.display = "inline-block";
        $("problemForm").style.display = "block";
    });
}

function updateProblem(url, csrfToken) {
    let type, visible;
    for (var i of document.getElementsByName("problemType")) if (i.checked === true) type = i.value;
    if ($("problemVisible").checked === true) visible = "visible";
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${$("problemName").value}&problemFlag=${$("problemFlag").value}&problemType=${type}&problemContents=${$("problemContents").value}&problemFile=${$("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data) => {
        $("result").innerText = data["result"];
    })
}

function addProblemForm(formURL, csrfToken, getURL, updateURL) {
    $("result").innerText = "";
    $("problemName").readOnly = false;
    $("problemName").value = "";
    $("problemFlag").value = "";
    for (var i of document.getElementsByName("problemType")) i.checked = false;
    $("problemContents").value = "";
    $("problemFile").value = "";
    $("problemVisible").checked = true;
    $("problemSubmit").setAttribute("onclick", `addProblem("${formURL}", "${csrfToken}", "${getURL}", "${updateURL}")`);
    $("problemSubmit").value = "add";
    $("problemDelete").style.display = "none";
    $("problemForm").style.display = "block";
}

function addProblem(url, csrfToken, getURL, updateURL) {
    let type, visible;
    for (var i of document.getElementsByName("problemType")) if (i.checked === true) type = i.value;
    if ($("problemVisible").checked === true) visible = "visible";
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${$("problemName").value}&problemFlag=${$("problemFlag").value}&problemType=${type}&problemContents=${$("problemContents").value}&problemFile=${$("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data) => {
        let div = document.createElement("div");
        div.className = "problemNameBox";
        div.setAttribute("onclick", `updateProblemGet("${getURL}", "${data["result"]}", "${csrfToken}", "${updateURL}")`);
        div.innerText = data["result"];
        div.id = $("problemName").value;
        $("problem").prepend(div);
        $("problemSubmit").value = "update";
        $("problemSubmit").setAttribute("onclick", `updateProblem("${updateURL}", "${csrfToken}")`);
    })
}

function deleteProblem(url, csrfToken) {
    let problemName = $("problemName").value;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${problemName}`
    }).then((res) => res.json()).then((data) => {
        $(problemName).remove();
        $("problemForm").style.display = "none";
        $("result").innerText = data["result"];
    })
}