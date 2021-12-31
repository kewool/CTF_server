function docId(name) {
    return document.getElementById(name);
}

let problem = docId("problem");
let users = docId("users");
let notice = docId("notice");
let solved = docId("solved");
let log = docId("log");

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

docId("userPwChange").addEventListener("click", ()=>{
    docId("userPwChange").style.display = "none";
    docId("userPwChangeForm").style.display = "block";
})

function getUser(url, id, name) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${id}`
    }).then((res) => res.json()).then((data) => {
        docId("userPwChange").style.display = "block";
        docId("userPwChangeForm").style.display = "none";
        docId("userResult").innerText = "";
        docId("userId").value = id;
        docId("userName").value = name;
        docId("userEmail").value = data["ctf_user_email"];
        docId("userSchool").value = data["ctf_user_school"];
        docId("userScore").innerText = data["ctf_user_score"];
        docId("userSolved").innerText = data["ctf_user_solved"];
        docId("userTry").innerText = data["ctf_user_try"];
        docId("userVisible").checked = data["ctf_user_visible"] ? true : false;
        docId("userAdmin").checked = data["ctf_user_admin"] ? true : false;
        docId("userRegisterDate").innerText = data["ctf_user_register_date"];
        docId("lastSolvedDate").innerText = data["ctf_user_last_solved_date"];
        docId("userForm").style.display = "block";
    });
}

function updateUser(url) {
    let visible, admin;
    if (docId("userVisible").checked === true) visible = "visible";
    if (docId("userAdmin").checked === true) admin = "admin";
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${docId("userId").value}&userName=${docId("userName").value}&userEmail=${docId("userEmail").value}&userSchool=${docId("userSchool").value}&userVisible=${visible}&userAdmin=${admin}`
    }).then((res) => res.json()).then((data) => {
        docId("userResult").innerText = data["result"];
    })
}

function changePassword(url){
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${docId("userId").value}&userPw=${docId("userPw").value}`
    }).then((res) => res.json()).then((data) => {
        docId("userResult").innerText = data["result"];
    })
}

function deleteUser(url){
    fetch(url, {
        method:'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `userId=${docId("userId").value}`
    }).then((res) => res.json()).then((data) => {
        docId(docId("userId").value).remove();
        docId("userForm").style.display = "none";
    })
}

function getProblem(url, name, formURL) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${name}`
    }).then((res) => res.json()).then((data) => {
        docId("problemResult").innerText = "";
        docId("problemName").readOnly = true;
        docId("problemName").value = name;
        docId("problemFlag").value = data["ctf_problem_flag"];
        let problemType = [];
        for (var i of document.getElementsByName("problemType")) problemType.push(i.value);
        problemType.map((item) => {
            if (data["ctf_problem_type"] === item) docId(item).checked = true;
        })
        docId("problemContents").value = data["ctf_problem_contents"];
        docId("problemFile").value = data["ctf_problem_file"];
        docId("problemVisible").checked = data["ctf_problem_visible"] ? true : false;
        docId("problemSubmit").value = "update";
        docId("problemSubmit").setAttribute("onclick", `updateProblem("${formURL}")`);
        docId("problemDelete").style.display = "inline-block";
        docId("problemForm").style.display = "block";
    });
}

function updateProblem(url) {
    let type, visible;
    for (var i of document.getElementsByName("problemType")) if (i.checked === true) type = i.value;
    if (docId("problemVisible").checked === true) visible = "visible";
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${docId("problemName").value}&problemFlag=${docId("problemFlag").value}&problemType=${type}&problemContents=${docId("problemContents").value}&problemFile=${docId("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data) => {
        docId("problemResult").innerText = data["result"];
    })
}

function addProblemForm(formURL, getURL, updateURL) {
    docId("problemResult").innerText = "";
    docId("problemName").readOnly = false;
    docId("problemName").value = "";
    docId("problemFlag").value = "";
    for (var i of document.getElementsByName("problemType")) i.checked = false;
    docId("problemContents").value = "";
    docId("problemFile").value = "";
    docId("problemVisible").checked = true;
    docId("problemSubmit").setAttribute("onclick", `addProblem("${formURL}", "${getURL}", "${updateURL}")`);
    docId("problemSubmit").value = "add";
    docId("problemDelete").style.display = "none";
    docId("problemForm").style.display = "block";
}

function addProblem(url, getURL, updateURL) {
    let type, visible;
    for (var i of document.getElementsByName("problemType")) if (i.checked === true) type = i.value;
    if(docId("problemName").value === null || docId("problemFlag").value === null || type === undefined){
        return docId("problemResult").innerText = "required problemName, problemFlag, problemType";
    }
    if (docId("problemVisible").checked === true) visible = "visible";
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${docId("problemName").value}&problemFlag=${docId("problemFlag").value}&problemType=${type}&problemContents=${docId("problemContents").value}&problemFile=${docId("problemFile").value}&problemVisible=${visible}`
    }).then((res) => res.json()).then((data) => {
        if(data["result"] !== "error"){let div = document.createElement("div");
        div.className = "problemNameBox";
        div.setAttribute("onclick", `getProblem("${getURL}", "${data["problemName"]}", "${updateURL}")`);
        div.innerText = data["problemName"];
        div.id = docId("problemName").value;
        docId("problem").prepend(div);
        docId("problemSubmit").value = "update";
        docId("problemSubmit").setAttribute("onclick", `updateProblem("${updateURL}")`);
        docId("problemDelete").style.display = "inline-block";}
        docId("problemResult").innerText = data["result"];
    })
}

function deleteProblem(url) {
    let problemName = docId("problemName").value;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${problemName}`
    }).then((res) => res.json()).then((data) => {
        docId(problemName).remove();
        docId("problemForm").style.display = "none";
        docId("problemResult").innerText = data["result"];
    })
}

function addNoticeForm(formURL, getURL, updateURL) {
    docId("noticeIdx").innerText = "";
    docId("noticeResult").innerText = "";
    docId("noticeTitle").value = "";
    docId("noticeContents").value = "";
    docId("noticeSubmit").setAttribute("onclick", `addNotice("${formURL}", "${getURL}", "${updateURL}")`);
    docId("noticeSubmit").value = "add";
    docId("noticeForm").style.display = "block";
}

function addNotice(url, getURL, updateURL) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `noticeTitle=${docId("noticeTitle").value}&noticeContents=${docId("noticeContents").value}`
    }).then((res) => res.json()).then((data) => {
        let div = document.createElement("div");
        div.className = "problemNameBox";
        div.setAttribute("onclick", `getNotice("${getURL}", "${data["noticeIdx"]}", "${docId("noticeTitle").value}", "${updateURL}")`);
        div.innerText = docId("noticeTitle").value;
        div.id = data["noticeIdx"];
        docId("notice").prepend(div);
        docId("noticeSubmit").value = "update";
        docId("noticeSubmit").setAttribute("onclick", `updateNotice("${updateURL}")`);
        docId("noticeDelete").style.display = "none";
        docId("noticeResult").innerText = data["result"];
    })
}

function getNotice(url, idx, title, updateURL) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `noticeIdx=${idx}`
    }).then((res) => res.json()).then((data) => {
        docId("noticeIdx").innerText = idx;
        docId("noticeTitle").value = title;
        docId("noticeContents").value = data["contents"];
        docId("noticeSubmit").value = "update";
        docId("noticeSubmit").setAttribute("onclick", `updateNotice("${updateURL}", ${idx})`);
        docId("noticeDelete").style.display = "inline-block";
        docId("noticeForm").style.display = "block";
    });
}

function deleteNotice(url, idx) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `noticeIdx=${idx}`
    }).then((res) => res.json()).then((data) => {
        docId(idx).remove();
        docId("noticeForm").style.display = "none";
        docId("noticeResult").innerText = data["result"];
    })
}

function updateNotice(url, idx) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `noticeIdx=${idx}&noticeTitle=${docId("noticeTitle").value}&noticeContents=${docId("noticeContents").value}`
    }).then((res) => res.json()).then((data) => {
        docId(idx).innerText = docId("noticeTitle").value
        docId("noticeResult").innerText = data["result"];
    })
}