function docId(name) {
    return document.getElementById(name);
}

fetch("/api/ctf/list", {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        "X-CSRFToken": csrfToken
    }
}).then((res) => res.json()).then((data) => {
    data = data["contents"];
    data.forEach((problem, i) => {
        if(docId(problem[0]) === null){
            let div = document.createElement("div");
            div.id = problem[0];
            div.className = "problemType";
            let p = document.createElement("p");
            p.className = "problemTypeText";
            p.innerText = problem[0];
            div.append(p);
            docId("panel").append(div);
        }
        let problemBox = document.createElement("div");
        problemBox.className = "problemBox";
        let problemName = document.createElement("p");
        problemName.innerText = problem[1];
        problemName.className = "problemName";
        problemBox.append(problemName);
        docId(problem[0]).append(problemBox);
        docId(problem[0])
    })
    console.log(data)

});

setInterval(function() {
    fetch("/api/ctf/list", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        }
    }).then((res) => res.json()).then((data) => {
        
    });
}, 10000);