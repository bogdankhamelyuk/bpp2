var ctx = document.getElementById("line-chart").getContext("2d");
       
    var graphData = {
        type: 'line',
        data: {
            labels: ['5','4','3','2','1'],
            datasets: [{
                label:'pressure records',
                borderColor: "#3e95cd",
                backgroundColor: "#7bb6dd",
                borderWidth: 3,
                fill: false,
                data:[0,0,0,0,0],
                backgroundColor: [
                    'rgba(73,198,230,0.7)',
                ],
                
            }]
        },
        options: {}
    }

var myChart = new Chart(ctx,graphData); 
    
var socket = new WebSocket('ws://127.0.0.1:8000/graph/upload/');

socket.onmessage = function(json_string){
    pressure = JSON.parse(json_string.data);
    console.log(pressure);
    
    var newGraphData = graphData.data.datasets[0].data;
    newGraphData.shift();
    newGraphData.push(pressure.pressure)//how???
    graphData.data.datasets[0].data = newGraphData;
    myChart.update();
}
