

class CircularBuffer {
    constructor(size, initialValue) {
      this.size = size;
      this.buffer = new Array(size).fill(initialValue);
      this.pointer = 0;
    }
  
    add(value) {
      this.buffer[this.pointer] = value;
      this.pointer = (this.pointer + 1) % this.size;
    }
  
    get() {
      return this.buffer.slice(this.pointer).concat(this.buffer.slice(0, this.pointer));
    }
  }
  
  var configData = {
    controlGeral: true, // Geral (true) ou individual (false)
    upper : [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],            //index 0 é o valor geral
    lower : [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
                                                              // base é 'a' média geral, 'f' fixo, 'm' média individual, 's' sensor de referência
    base :  ['a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a','a'],
    baseValue : [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    time : [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7]
  };


document.addEventListener('DOMContentLoaded', function () {


    // Example usage
    const bufferSize = 180;
    const initialValue = 0.0; // initial value for the buffer
    const floatArraySize = 35;
    const circularBuffer = new CircularBuffer(bufferSize, new Array(floatArraySize).fill(initialValue));
    
  
  



    var tempChart
    var timeChart
    // Função para obter dados de temperatura via AJAX
    function obterDadosTemperatura() {
        fetch('/dados_temperatura')
            .then(response => response.json())
            .then(data => {
                atualizarGrafico(data.temperaturas,data.media);
                atualizarModo(data.modo);
                atualizarEstado(data.estado,data.estado_ga);
            })
            .catch(error => console.error('Erro ao obter dados de temperatura:', error));
    }

    function obterNovosDadosTemperatura() {
        fetch('/dados_temperatura')
            .then(response => response.json())
            .then(data => {
                            atualizaDadosGrafico(data.temperaturas,data.media);
                            atualizarModo(data.modo);
                            atualizarEstado(data.estado,data.estado_ga);
                          })
            .catch(error => console.error('Erro ao obter dados de temperatura:', error));
    }
    // Função para atualizar o gráfico com os novos dados
    function atualizarGrafico(temperaturas,media) {
        var ctx = document.getElementById('temperatureChart').getContext('2d');
        
        tempChart = new Chart(ctx, {
            data: {
                labels: Array.from({length: temperaturas.max.length}, (_, i) => i + 1),
                datasets: [{
                            type: 'bar',
                            label: 'max',
                            data: temperaturas.max,
                            borderColor: 'red',
                            borderWidth: 2,
                            fill: false
                        },
                        {
                            type: 'bar',
                            label: 'last',
                            data: temperaturas.real,
                            borderColor: 'green',
                            borderWidth: 2,
                            fill: false
                        },
                        {
                            type: 'bar',
                            label: 'min',
                            data: temperaturas.min,
                            borderColor: 'blue',
                            borderWidth: 2,
                            fill: false
                        }, {
                            type: 'line',
                            label: 'Limite Superior de Temperatura',
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media+7),
                        },
                        {
                            type: 'line',
                            label: 'Temperatura Média',
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media),
                        },
                        {
                            type: 'line',
                            label: 'Limite Inferior de Temperatura',
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media-7),
                        }],
                    },
            
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Sensores'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Temperatura (°C)'
                        }
                    }
                }
            }
        });
    }

    function atualizaDadosGrafico(temperaturas,media)
    {
        var newFloatArray = temperaturas.real; // Generating random float array
        newFloatArray.push(media);
        newFloatArray.push(media+7);
        newFloatArray.push(media-7);
        circularBuffer.add(newFloatArray);

        var timestamp = new Date().toLocaleTimeString();
        updateChart(newFloatArray);
        timeChart.data.labels.shift();
        timeChart.data.labels.push(timestamp);
        timeChart.update();

        var check_max = document.getElementById("check_max").checked;
        var check_real = document.getElementById("check_real").checked;
        var check_min = document.getElementById("check_min").checked;
        if (check_max) {
            tempChart.show(0);
            tempChart.data.datasets[0].data = temperaturas.max; 
        }else{
            tempChart.hide(0);
            //tempChart.data.datasets[0].data = Array.from({length: temperaturas.max.length}, (_, i) => 0)
        }

        if (check_real) {
            tempChart.show(1);
            tempChart.data.datasets[1].data = temperaturas.real; 
        }else{
            tempChart.hide(1);
            //tempChart.data.datasets[1].data = Array.from({length: temperaturas.max.length}, (_, i) => 0)
        }

        if (check_min) {
            tempChart.show(2);
            tempChart.data.datasets[2].data = temperaturas.min; 
        }else{
            tempChart.hide(2);
            //tempChart.data.datasets[2].data = Array.from({length: temperaturas.max.length}, (_, i) => 0)
        }
        tempChart.data.datasets[3].data = Array.from({length: temperaturas.real.length}, (_, i) => media+7)
        tempChart.data.datasets[4].data = Array.from({length: temperaturas.real.length}, (_, i) => media)
        tempChart.data.datasets[5].data = Array.from({length: temperaturas.real.length}, (_, i) => media-7)

        tempChart.update(); 
    }


    function atualizarEstado(estado,estado_ga) {
        var botao = document.getElementById("botao_estado_alarme");
        if (estado) {
            botao.innerText  = "Ligado";
            botao.classList.add("btn-danger");
            botao.classList.remove("btn-success");
        }else{
            botao.innerText  = "Desligado";
            botao.classList.add("btn-success");
            botao.classList.remove("btn-danger");
        }
        var botao_GA = document.getElementById("botao_estado_ga");
        if (estado_ga) {
            botao_GA.innerText  = "Ligado";
            botao_GA.classList.add("btn-success");
            botao_GA.classList.remove("btn-danger");
        }else{
            botao_GA.innerText  = "Desligado";
            botao_GA.classList.add("btn-danger");
            botao_GA.classList.remove("btn-success");
        }
    }


    function atualizarModo(modo) {
        document.getElementById('modoSelecao').value = modo;
    }

 
    document.getElementById('modoSelecao').addEventListener('change', function () {
        var novoModo = this.value;
        fetch('/alterar_modo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ modo: novoModo })
        })
        .then(response => response.json())
        .then(data => console.log('Modo alterado:', data))
        .catch(error => console.error('Erro ao alterar modo:', error));
    });

    function enviaConfig(){
        fetch('/alterar_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        })
        .then(response => response.json())
        .then(data => console.log('Config alterada:', data))
        .catch(error => console.error('Erro ao alterar configuração:', error));
    }


    document.getElementById('timeSelecao').addEventListener('change', function () {
        var novoTime = this.value;
        timeChart.destroy();
        initiateTimeChart(novoTime);
    });

        // Function to generate random RGB color values
    function generateRandomColor() {
        return 'rgb(' + Math.floor(Math.random() * 256) + ',' + Math.floor(Math.random() * 256) + ',' + Math.floor(Math.random() * 256) + ')';
    }

    // Function to update the chart with new temperature data
    function updateChart(newData) {
        for (var i = 0; i < 35; i++) {
                timeChart.data.datasets[i].data.shift();
                timeChart.data.datasets[i].data.push(newData[i]);
        }
        timeChart.update();        
    }


    function initiateTimeChart(timeSize){
        // Initialize the chart
        var ctx = document.getElementById('timeChart').getContext('2d');
        
        timeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                // scales: {
                //     yAxes: [{
                //         ticks: {
                //             beginAtZero: true
                //         }
                //     }]
                // }
                //parsing: false,
                animations: false
            }
        });
        //timeChart.options.animation = false;
        // Add datasets for 32 sensors + average
        for (var i = 0; i < 32; i++) {
            var randomColor = generateRandomColor();
            timeChart.data.datasets.push({
                label: 'T' + (i + 1),
                borderColor: randomColor,
                borderWidth: 1,
                fill: false,
                data: [],
                hidden: false // Initially hidden
            });
        }
        
        timeChart.data.datasets.push({
            label: 'Média',
            borderColor: 'black',
            borderWidth: 3,
            fill: false,
            data: [],
            hidden: false, // Initially not hidden
            drawActiveElementsOnTop: true
        });
        timeChart.data.datasets.push({
            label: 'Limite Superior',
            borderColor: 'red',
            borderWidth: 3,
            fill: false,
            data: [],
            hidden: false, // Initially not hidden
            drawActiveElementsOnTop: true
        });
        timeChart.data.datasets.push({
            label: 'Limite Inferior',
            borderColor: 'red',
            borderWidth: 3,
            fill: false,
            data: [],
            hidden: false, // Initially not hidden
            drawActiveElementsOnTop: true
        });

        const last180Values = circularBuffer.get();
        const startCount = 180 - timeSize;
        for (var x = startCount; x < 180; x++)
        {
            for (var i = 0; i < 35; i++) {
                timeChart.data.datasets[i].data.push(last180Values[x][i]);
            }
        }

        timeChart.data.labels = Array.from({length: timeSize}, (_, i) => ' ');;
        timeChart.update();
    }

      function searchAndDownload() {
        var startTime = document.getElementById("start-time").value;
        var stopTime = document.getElementById("stop-time").value;
    
        // Make an AJAX request using fetch to the Flask server to search for files
        fetch('/searchFiles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ startTime: startTime, stopTime: stopTime })
        })
        .then(response => response.json())
        .then(file => {
            var downloadUrl = "/downloadFile/" + file;
    
            // Download filtered files
            //downloadUrls.forEach(function(url) {
                downloadFile(downloadUrl);
            //});
        })
        .catch(error => console.error('Error searching files:', error));
    }

      function downloadFile(url) {
        // Create a temporary anchor element to initiate download
        var link = document.createElement("a");
        link.href = url;
        link.download = url.split("/").pop(); // Extract filename
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    
      
      document.getElementById("search-btn").addEventListener("click", searchAndDownload);


    // Chamar a função para obter dados de temperatura a cada 1 segundo
    setInterval(obterNovosDadosTemperatura, 1000);

    // Chamar a função para obter dados de temperatura ao carregar a página
    obterDadosTemperatura();
    initiateTimeChart(30);

    
    

});
