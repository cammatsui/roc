window.addEventListener('load', function() {
    fetch('/get-admin-chart-data').then(function(response){
        response.json().then(function(result) {
            if (result.status === 'failure') return;

            let fmtData = []
            for (let res of result.data) {
                fmtData.push({x: res[0], y: res[1]})
            }

            let chartConfig = {
                type: 'line',
                data: {
                    datasets: [{
                        data: fmtData,
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderColor: 'rgb(255, 99, 132)'
                    }] 
                },
                options: {
                    scales: {
                        x: { type: 'timeseries' },
                        y: { ticks: {suggestedMin: 0} },
                    }
                }
            };

            let chart = new Chart(document.getElementById('myChart'), chartConfig);

            chart.options.scales.x = { type: 'timeseries' }
            chart.options.scales.y = { ticks: { suggestedMin: 0 } }

        })
    })
})

