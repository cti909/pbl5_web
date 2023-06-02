date = document.getElementById("dateInput").value;
console.log(date)
let form_search = document.getElementById("form_search");
form_search.addEventListener("submit", function(event){
  event.preventDefault();
  date = document.getElementById("dateInput").value;
  window.location.href = "/statistic_location?page=1&date="+date;
})

let paginationContainer = document.getElementById("pagination");
let paginationList = document.createElement("ul");
paginationList.classList.add("pagination");

let prevItem = document.createElement("li");
prevItem.classList.add("page-item");
let prevLink = document.createElement("a");
prevLink.classList.add("page-link");
prevLink.setAttribute("aria-label", "Previous");
prevLink.setAttribute("href", "/statistic_location?page="+(window.page_current-1)+"&date="+date);
let prevIcon = document.createElement("i");
prevIcon.classList.add("fa-solid", "fa-angle-left");
prevLink.appendChild(prevIcon);
prevItem.appendChild(prevLink);
paginationList.appendChild(prevItem);
if (window.page_current == 1) prevItem.classList.add("disabled");
else prevItem.classList.remove("disabled");

for (let i = 1; i <= window.page_count; i++) {
  let pageItem = document.createElement("li");
  pageItem.classList.add("page-item");
  if (i === window.page_current) {
    pageItem.classList.add("active");
  }
  let pageLink = document.createElement("a");
  pageLink.classList.add("page-link");
  pageLink.setAttribute("href", "/statistic_location?page="+i+"&date="+date);
  pageLink.textContent = i;
  pageItem.appendChild(pageLink);
  paginationList.appendChild(pageItem);
}

let nextItem = document.createElement("li");
nextItem.classList.add("page-item");
let nextLink = document.createElement("a");
nextLink.classList.add("page-link");
nextLink.setAttribute("href", "/statistic_location?page="+(window.page_current+1)+"&date="+date);
nextLink.setAttribute("aria-label", "Next");
let nextIcon = document.createElement("i");
nextIcon.classList.add("fa-solid", "fa-angle-right");
nextLink.appendChild(nextIcon);
nextItem.appendChild(nextLink);
paginationList.appendChild(nextItem);
if (window.page_current == window.page_count) nextItem.classList.add("disabled");
else nextItem.classList.remove("disabled");

paginationContainer.appendChild(paginationList);

