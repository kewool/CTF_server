function docId(name) {
    return document.getElementById(name);
}

function updateProfile(url, csrfToken){
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body:`userName=${docId("userName").value}&userPw=${docId("userPw").value}&userEmail=${docId("userEmail").value}&userSchool=${docId("userSchool").value}&userIntroduce=${docId("userIntroduce").value}`
    }).then((res) => res.json()).then((data)=>{
        docId("result").innerText = data["result"];
    })
}