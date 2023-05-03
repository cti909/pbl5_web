let selectedRadio = document.querySelector('input[name="sort"]:checked');
let sort_name = selectedRadio.value;

var sortRadios = document.querySelectorAll('input[type="radio"][name="sort"]');
sortRadios.forEach(function(radio) {
  radio.addEventListener("change", function() {
    sort_name = radio.value;
    window.location.href = "/statistic_hr?page="+window.page_current+"&sort_field="+sort_field+"&sort_name="+sort_name;
  });
});

let selectElement = document.getElementById("field");
let sort_field = selectElement.value;
selectElement.addEventListener("change", function() {
  sort_field = selectElement.value;
  window.location.href = "/statistic_hr?page="+window.page_current+"&sort_field="+sort_field+"&sort_name="+sort_name;
});
let paginationContainer = document.getElementById("pagination");
let paginationList = document.createElement("ul");
paginationList.classList.add("pagination");

let prevItem = document.createElement("li");
prevItem.classList.add("page-item");
let prevLink = document.createElement("a");
prevLink.classList.add("page-link");
prevLink.setAttribute("aria-label", "Previous");
let prevIcon = document.createElement("i");
prevIcon.classList.add("fa-solid", "fa-angle-left");
prevLink.appendChild(prevIcon);
prevItem.appendChild(prevLink);
paginationList.appendChild(prevItem);

for (let i = 1; i <= window.page_count; i++) {
  let pageItem = document.createElement("li");
  pageItem.classList.add("page-item");
  if (i === window.page_current) {
    pageItem.classList.add("active");
  }
  let pageLink = document.createElement("a");
  pageLink.classList.add("page-link");
  pageLink.setAttribute("href", "/statistic_hr?page="+i+"&sort_field="+sort_field+"&sort_name="+sort_name);
  pageLink.textContent = i;
  pageItem.appendChild(pageLink);
  paginationList.appendChild(pageItem);
}

let nextItem = document.createElement("li");
nextItem.classList.add("page-item");
let nextLink = document.createElement("a");
nextLink.classList.add("page-link");
nextLink.setAttribute("aria-label", "Next");
let nextIcon = document.createElement("i");
nextIcon.classList.add("fa-solid", "fa-angle-right");
nextLink.appendChild(nextIcon);
nextItem.appendChild(nextLink);
paginationList.appendChild(nextItem);

paginationContainer.appendChild(paginationList);

