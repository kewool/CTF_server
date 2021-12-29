function docId(name) {
    return document.getElementById(name);
}
docId("problemPanel").addEventListener("click", () => false);
docId("background").addEventListener("click", () => {
    docId("background").style.display = "none";
    docId("problemPanel").style.display = "none";
});

function showProblem(problemName){
    docId("background").style.display = "block";
    docId("problemPanel").style.display = "block";
    fetch("/api/ctf/get", {
        method: 'POST',
        headers:{
            'Content-Type': 'application/x-www-form-urlencoded',
            "X-CSRFToken": csrfToken
        },
        body: `problemName=${problemName}`
    }).then((res)=>res.json()).then((data)=>{
        docId("problemPanelTitle").innerText = problemName;
        docId("problemPanelScore").innerText = data[""]
    })

}

fetch("/api/ctf/list", {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        "X-CSRFToken": csrfToken
    }
}).then((res) => res.json()).then((data) => {
    let last_data = data["contents"];
    last_data.forEach((problem, i) => {
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
        problemBox.id = problem[1];
        problemBox.setAttribute("onclick", `showProblem("${problem[1]}")`);
        let problemName = document.createElement("p");
        problemName.innerText = problem[1];
        problemName.className = "problemName";
        problemBox.append(problemName);
        let problemScore = document.createElement("span");
        problemScore.innerText = problem[2];
        problemBox.append(problemScore);
        docId(problem[0]).append(problemBox);
        docId(problem[0])
    })
    data["solved"].map(i => docId(i).classList.add("solved"));
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