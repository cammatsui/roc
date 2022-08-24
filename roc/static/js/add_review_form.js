/**
 * Dynamically update the add-review form based on user input.
 * Sends internal API request to get data.
 */

let deptSelect = document.getElementById('department');
let courseSelect = document.getElementById('course');
let termSelect = document.getElementById('term');
let sectionSelect = document.getElementById('section');

/* Populate departments. */
window.onload = function() {
    let optionHTML = '<option value="none"></option>';

    fetch('/api/get-departments').then(function(response){
        response.json().then(function(data) {
            for (let dept of data.depts) {
                optionHTML += '<option value="'+dept.id+'">'+dept.name+'</option>'; 
            }
            deptSelect.innerHTML = optionHTML;
        })
    })

}

/* Populate the course selector with courses from the selected department. */
deptSelect.onchange = function() {
    let optionHTML = '<option value="none"></option>';
    dept = deptSelect.value;
    // Clear below selectors' options.
    courseSelect.innerHTML = optionHTML;
    termSelect.innerHTML = optionHTML;
    sectionSelect.innerHTML = optionHTML;

    fetch('/api/get-courses/' + dept).then(function(response){
        response.json().then(function(data) {
            for (let course of data.courses) {
                optionHTML += '<option value="'+course.id+'">'+course.name+'</option>'; 
            }
            courseSelect.innerHTML = optionHTML;
        })
    })
}

/* Populate the term selector with terms that the selected course was offered. */
courseSelect.onchange = function() {
    let optionHTML = '<option value="none"></option>';
    course = courseSelect.value;
    // Clear below selectors' options.
    termSelect.innerHTML = optionHTML;
    sectionSelect.innerHTML = optionHTML;

    fetch('/api/get-terms/' + course).then(function(response){
        response.json().then(function(data) {
            let optionHTML = '<option value="none"></option>';
            for (let term of data.terms) {
                optionHTML += '<option value="'+term+'">'+term+'</option>'; 
            }
            termSelect.innerHTML = optionHTML;
        })
    })
}

/**
 * Populate the section selector with sections for the selected course taught in the 
 *  selected term.
 */
termSelect.onchange = function() {
    let optionHTML = '<option value="none"></option>';
    term = termSelect.value;
    // Clear below selectors' options.
    sectionSelect.innerHTML = optionHTML;

    term = termSelect.value;
    course = courseSelect.value;
    fetch('/api/get-sections/' + course + '/' + term).then(function(response){
        response.json().then(function(data) {
            let optionHTML = '<option value="none"></option>';
            for (let section of data.sections) {
                optionHTML += '<option value="'+section.id+'">'+section.desc+'</option>'; 
            }
            sectionSelect.innerHTML = optionHTML;
        })
    })
}


/* Star ratings */
function getStar(starNum, inputId) {
    var starId = "star-" + starNum + "-input-" + inputId;
    return document.getElementById(starId);
}

function selectStar(starNum, inputId) {
    star = getStar(starNum, inputId);
    star.classList.remove("bi-star", "rating-star");
    star.classList.add("bi-star-fill", "rating-star-fill");
}

function deSelectStar(starNum, inputId) {
    star = getStar(starNum, inputId);
    star.classList.remove("bi-star-fill", "rating-star-fill");
    star.classList.add("bi-star", "rating-star");
}

function handleStarClick(starNum, inputId) {
    console.log("Clicked star " + starNum + " for input " + inputId);
    var hiddenInput = document.getElementById(inputId);
    hiddenInput.value = starNum;
    for (var i = 1; i <= 5; i++) {
        if (i <= starNum) {
            selectStar(i, inputId)
        } else {
            deSelectStar(i, inputId)
        }
    }
}

var inputIds = ['professor_rating', 'difficulty_rating', 'workload_rating', 'interesting_rating'];
for (let i = 0; i < inputIds.length; i++) {
    let inputId = inputIds[i];
    var hiddenInput = document.getElementById(inputId);
    hiddenInput.value = 1;
    for (let j = 1; j <= 5; j++) {
        let star = getStar(j, inputId);
        star.onclick = function () {
            let starNum = j;
            let hiddenInput = document.getElementById(inputId);
            hiddenInput.value = starNum;
            console.log("Input " + inputId + " now has value " + hiddenInput.value);
            for (let k = 1; k <= 5; k++) {
                if (k <= starNum) {
                    selectStar(k, inputId)
                } else {
                    deSelectStar(k, inputId)
                }
            }

        }
    }
}
