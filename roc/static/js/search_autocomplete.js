var desktopSearchInput = document.getElementById('search-input');
var mobileSearchInput = document.getElementById('mobile-search-input');
console.log

/**
 * Get the courses and professors matching the search query in the input and populate the
 * autocomplete with them. First clears the options, then gets matches via internal API
 * request, then adds these to autocomplete.
 */
function search(searchList, query) {
    clearOptions(searchList);
    if (query.length == 0) return;
    fetch('/api/search/' + query).then(function(response) {
        response.json().then(function(data) {
            if (data.status != 'failure') {
                let resultsHTML = '';
                for (let res of data.results) {
                    resultsHTML += '<a href="/reviews/' + res.type + '/' + res.id + '"><li class="search-option">' 
                    resultsHTML += '(' + res.reviews + ') ' + res.name + '</li></a>';
                }
                searchList.innerHTML = resultsHTML;
                if (!searchList.classList.contains("bordered")) {
                    searchList.classList.toggle("bordered")
                }
            }
        })
    })
}

function clearOptions(searchList) {
    while (searchList.firstChild) {
        searchList.removeChild(searchList.firstChild);
    }
    if (searchList.classList.contains("bordered")) {
        searchList.classList.toggle("bordered")
    }
}

// Only search when hitting enter.
desktopSearchInput.addEventListener("keyup", function(event) {
    searchList = document.getElementById('search-list');
    if (event.key === "Enter") {
        search(searchList, desktopSearchInput.value)
    }
});

mobileSearchInput.addEventListener("keyup", function(event) {
    searchList = document.getElementById('mobile-search-list');
    if (event.key === "Enter") {
        search(searchList, mobileSearchInput.value)
    }
});

// Clear options when clicking off.
document.addEventListener('click', function(event) {
    var desktopSearchList = document.getElementById('search-list');
    var mobileSearchList = document.getElementById('mobile-search-list');
    if (!desktopSearchList.contains(event.target)) {
        clearOptions(desktopSearchList); 
    }
    if (!mobileSearchList.contains(event.target)) {
        clearOptions(mobileSearchList); 
    }
});

