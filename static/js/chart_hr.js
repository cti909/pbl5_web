let frame_length = 30;
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
        url: "/predict_data",
        type: "GET",
        dataType: 'json',
        success: function (data) {
            console.log(data)
            
            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            for(i=0; i<frame_length; i++) {
                chart.data.labels.splice(i, 1, i);
                chart.data.datasets[0].data.splice(i, 1, data.data[i]);
                
            }
            chart.update(); 
            let start_time = document.getElementById("time-start")
            let time_end = document.getElementById("time-end")
            let result = document.getElementById("result")
            start_time.innerHTML = data.time_start;
            time_end.innerHTML = data.time_end;
            result.innerHTML = data.label_predict;
            setTimeout(updateChart, 5000);
            time = time + 1;
        },
        complete: function () {
            
        }
    });
}
updateChart();


