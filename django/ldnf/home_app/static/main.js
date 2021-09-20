
// google.charts.setOnLoadCallback(drawChart);
var socket = new WebSocket('ws://127.0.0.1:8000/graph/upload/');
var x_list = [[0]];
var y_list = [[0]];
var table_data = [{
    x: x_list,
    y: y_list,
    mode: 'lines+markers', 
    marker: {color: '#EB89B5', size: 8},
    line: {width: 4}
}];
var layout = {
    // title: 'Der Druckwert durch das CV-Auslesen',
    font: {size: 18},
    plot_bgcolor: "rgb(245,245,240)",
};
var config = {responsive: true};
var layout = {font: {size: 18}};
var config = {responsive: true};
TESTER = document.getElementById('line-chart');
Plotly.newPlot(TESTER, table_data, layout, config);

var i = 1
 function update_data(time,pressure){
    var upd = {
        x: [[time]],
        y: [[pressure]],
    };
    Plotly.extendTraces(TESTER,upd,[0],i);
    i++;   
 }


socket.onmessage = function(json_string){
    
    received = JSON.parse(json_string.data);
    if(received["message"]=="ok"){
        $.ajax({
            type:"GET",
            url:  "http://127.0.0.1:8000/ajax/getPressure",
            success : function(response){
                data = JSON.parse(JSON.stringify(response));
                update_data(data.time,data.pressure);
            }
            
        }); 
    }    
}

