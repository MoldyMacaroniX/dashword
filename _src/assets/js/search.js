// This is used to lookup our template defined in partials/articles.njk
let contentMap = null;
async function getContentMap() {

    if (contentMap) {
        return contentMap;
    }

    const response = await fetch("/content.json");
    contentMap = await response.json();

    return contentMap;
}

// This is used to select the above search form.
const form = document.querySelector("#search-form");

// This defines how many results are visible per page
const perPage = 12;

// Used to track current page vs total pages
let currentPage = 1;
let totalPages = 1;

// This is called whenever a search using the above form takes place.
async function search(event) {
    // If relevant, prevent default form behavior
    try {
        event.preventDefault();
    } catch(e) {}

    // This defines the container the search results will populate
    const resultContainer = document.querySelector("#search-results");
    resultContainer.replaceChildren();

    // Initialize Pagefind
    const pagefind = await import("/pagefind/pagefind.js");
    pagefind.init();

    // This is the exact input in the form the search is stored in
    const query = document.querySelector("#search-input").value;

    // Call Pagefind to get search results
    const search = await pagefind.search(query);

    // Get total results and pages
    const totalResults = search.results.length;
    totalPages = Math.ceil(totalResults / perPage);

    // Figure out the start and end indexes for the articles to show on this page
    const start = (currentPage - 1) * perPage;
    const end = start + perPage;

    // Use this information and slice the search results
    const results = await Promise.all(
        search.results.slice(start, end)
    );

    // For each result, display it
    for (const result of results) {
        const data = await result.data();

        const div = document.createElement("div");
        div.style = "height: 100%;";
        // div.innerHTML = `
        //     <div>
        //         <p>
        //             <strong>
        //                 <a href="${data.url}">
        //                     ${data.meta.title}
        //                 </a>
        //             </strong>
        //         </p>
        //         <p>${data.excerpt}</p>
        //     </div>
        // `;

        // Add template defined in content.json
        // Or you can comment out the bottom two lines and define the template above (see commented out code)
        const contentMap = await getContentMap();
        if (!contentMap[data.url]) {
            // This is useful for debugging, but we hope it always go to ELSE case!
            div.innerHTML = data.meta.title + data.url;
        } else {
            div.innerHTML = contentMap[data.url];
        }

        resultContainer.append(...div.childNodes);
    }

    if (results.length == 0) {
        resultContainer.innerHTML = `<div class="panel panel-center"><p><strong>No results found...</strong></p></div>`;
    }

    // Now we need to render the pagination
    renderPagination(query);
}

// This is called whenever we need to render the pagination buttons,
// which we need to for every search / page change
function renderPagination(query) {

    // The container we will insert pagination to
    const container = document.querySelector("#search-pagination");
    if (!container) return;

    // Clear its contents
    container.innerHTML = "";

    // If there is only a single page, we can exit here
    // if (totalPages <= 1) return;

    // If we are not on the first page, add a previous link
    if (currentPage > 1) {
        container.innerHTML += `
            <a href="?search=${query}&page=${currentPage - 1}" class="btn">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M7.82843 10.9999H20V12.9999H7.82843L13.1924 18.3638L11.7782 19.778L4 11.9999L11.7782 4.22168L13.1924 5.63589L7.82843 10.9999Z"></path></svg>
                <span>Previous</span>
            </a>
        `;
    } else {
        // If we are on the first page:
        container.innerHTML += `
            <div class="btn disabled">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M7.82843 10.9999H20V12.9999H7.82843L13.1924 18.3638L11.7782 19.778L4 11.9999L11.7782 4.22168L13.1924 5.63589L7.82843 10.9999Z"></path></svg>
                <span>Previous</span>
            </div>
        `;
    }

    // If you're brave, you can try using this...
    // for (let i = 1; i <= totalPages; i++) {
    //    container.innerHTML += `
    //        <a href="?search=${query}&page=${i}"
    //        ${i === currentPage ? 'aria-current="page"' : ""}>
    //            ${i}
    //        </a>
    //    `;
    // }

    // If we are not on the last page, add a next link
    if (currentPage < totalPages) {
        container.innerHTML += `
            <a href="?search=${query}&page=${currentPage + 1}" class="btn">
                <span>Next</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"></path></svg>
            </a>
        `;
    } else {
        // If we are on the last page:
        container.innerHTML += `
            <div class="btn disabled">
                <span>Next</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"></path></svg>
            </div>
        `;
    }
}

// Call the search function whenever the search form is submitted
try {
    form.addEventListener("submit", (e) => {
        currentPage = 1;
        search(e);
    });
} catch {
    // No error means no search form on this page
}

// URL handling
// Grab params from URL
const params = new URLSearchParams(window.location.search);

// Get the values for search and page
const value = params.get("search");
const page = parseInt(params.get("page")) || 1;

// Set the current page to whatever page we are on
currentPage = page;

// Call the search function
if (value != null) {
    document.querySelector("#search-input").value = value;
    search(null);
}

// Call this function to search from the input in the navigation bar
function searchFromNav() {
    // The input you want to search using
    var term = document.querySelector("#search-nav").value;
    // Go to search page
    if (term != '') {
        window.location.href = "/search/?search=" + term;
    } else {
        window.location.href = "/search/";
    }
    // Prevent default form behavior
    return false;
}

function searchFromForm(form) {

    event.preventDefault();

    const input = form.querySelector('input[type="search"]');

    if (!input) return;

    const term = input.value.trim();

    if (!term) return;

    window.location.href =
        `/search/?search=${encodeURIComponent(term)}`;

}