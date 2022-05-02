const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const tableUsers = document.querySelector(".table-users");
const paginationContainer = document.querySelector(".pagination");
const tBody = document.querySelector(".table-body");
const noResults = document.querySelector(".no-results")
tableOutput.style.display='none';

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;    

    if(searchValue.trim().length > 0){
        paginationContainer.style.display = "none";
        tBody.innerHTML = "";
        console.log("length",searchValue.trim().length );

        fetch('/search-students', {
            body: JSON.stringify({ searchText: searchValue}),
            method: 'POST',
        })
        .then((res) => res.json())
        .then((data) => {
        tableUsers.style.display="none";
        tableOutput.style.display="block";
        if(data.length === 0){
            console.log("data",data.length);
            tableOutput.innerHTML = "No Results Found.";
        } else {    
            data.forEach((item) => {
                tBody.innerHTML += `
                <tr> 
                <td>${item.user_idnumber}</td>
                <td>${item.user_lname}</td>
                <td>${item.user_fname}</td>
                <td>${item.college}</td>
                <td>${item.course}</td>
                <td>${item.yearlevel}</td>
                <td>${item.user_gender}</td>              
                <td></td>              
                <td></td>              
                </tr>`;
            });
        }
    });
    } else {
        tableOutput.style.display = "none";
        tableUsers.style.display="block";
        paginationContainer.style.display = "block";
    }
});