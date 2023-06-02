// let inputMonth = document.getElementById("start");
// let selectedMonth = inputMonth.value;
// console.log(selectedMonth)
let date = document.getElementById("time-selected");
date.addEventListener("change", function(event){
    window.location.href = "/statistic_analysis?date="+date.value;
})