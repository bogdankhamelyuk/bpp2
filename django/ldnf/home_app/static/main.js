
// google.charts.setOnLoadCallback(drawChart);
var socket = new WebSocket('ws://127.0.0.1:8000/graph/upload/');

var options = {
    chart: {
      type: 'line',
      height: 800 ,
      zoom: {
        enabled: true,
        type: 'x',
        resetIcon: {
                offsetX: -10,
                offsetY: 0,
                fillColor: '#fff',
                strokeColor: '#37474F'
            },
            selection: {
                background: '#90CAF9',
                border: '#0D47A1'
            }    
        }
    },
    series: [{
        name: 'Druck [ba]'
    }],
    title: {
        text: 'Druckwerte durch das CV-Auslesen des Manometers',
        style:{
            fontsize:'100px'
        }
    },
    stroke: {
        curve: 'smooth',
    },
    xaxis:{
        title: {
            text:"Zeit in Sekunden",
            style: {
                fontSize :'15'
            }
            
        }
    },
    legend: {
        position: 'top',
        show: true,
    },
    zoom: {
        enabled: true,
        type: 'x',  
        autoScaleYaxis: false,  
        zoomedArea: {
          fill: {
            color: '#90CAF9',
            opacity: 0.4
          },
          stroke: {
            color: '#0D47A1',
            opacity: 0.4,
            width: 1
          }
        }
    },
    fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          type: "vertical",
          shadeIntensity: 1,
          gradientToColors: ['#fd3535'], // optional, if not defined - uses the shades of same color in series
          inverseColors: true,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100, 100, 100],
          colorStops: []
        }
      }
    
}

var chart = new ApexCharts(document.querySelector("#line-chart"), options);
var x_list = []
var y_list = []
chart.render();

socket.onmessage = function(json_string){
    
    received = JSON.parse(json_string.data);
    if(received["message"]=="ok"){
        $.ajax({
            type:"GET",
            url:  "http://127.0.0.1:8000/ajax/getPressure",
            success : function(response){
                response_data = JSON.parse(JSON.stringify(response));
                x_list.push(response_data.time);
                y_list.push(response_data.pressure);
                chart.updateSeries([{
                    data : y_list
                    // data: response_data.
                  }])
                chart.updateOptions({
                    xaxis: {
                        categories: x_list 
                    }
                })
            }
            
        }); 
    }    
}

