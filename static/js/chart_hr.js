let frame_length = 60;
let ctx = document.getElementById('myChart').getContext('2d');
let xValues = new Array(frame_length).fill(0);
let yValues = new Array(frame_length).fill(0);
let chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: xValues,
        datasets: [{
            label: 'hr',
            data: yValues,
            borderColor: 'RGB(100,100,100)',
            fill: false,
        }]
    },
    options: {
        legend: { display: false },
        scales: {
            y: {
                suggestedMin: 0,
                suggestedMax: 200
            }
        }
    }
});

let time = 0;
let updateChart = () => {
    $.ajax({
        url: "/get_heart_rate",
        type: "GET",
        dataType: 'json',
        success: function (data) {
            console.log(data)
            
            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            for(i=0; i<frame_length; i++) {
                chart.data.labels.splice(i, 1, i);
                chart.data.datasets[0].data.splice(i, 1, data.heart_rate_data[i]);                
            }
            chart.update(); 
            let posting_time = document.getElementById("posting-time");
            let heart_rate_mean = document.getElementById("heart-rate-mean");
            let result = document.getElementById("result");

            posting_time.innerHTML = data.posting_time;
            heart_rate_mean.innerHTML = data.heart_rate_mean;
            result.innerHTML = data.result;
            setTimeout(updateChart, 5000);
            time = time + 1;
        },
        complete: function () {
            
        }
    });
}
updateChart();


