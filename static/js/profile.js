function updateProfile(url, csrfToken){
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body:`userName=${document.getElementById("userName").value}&userPw=${document.getElementById("userPw").value}&userEmail=${document.getElementById("userEmail").value}&userSchool=${document.getElementById("userSchool").value}`
    }).then((res) => res.json()).then((data)=>{
        document.getElementById("result").innerText = data["result"];
    })
}