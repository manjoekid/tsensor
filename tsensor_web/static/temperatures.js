

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
    general_limit: true, // Geral (true) ou individual (false)
    upper : [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],            //index 32 é o valor geral
    lower : [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
    enabled : [true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,
               true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,true],
    time : 7
};


document.addEventListener('DOMContentLoaded', function () {

    const bufferSize = 180;
    const initialValue = 0.0; // initial value for the buffer
    const floatArraySize = 35;
    const circularBuffer = new CircularBuffer(bufferSize, new Array(floatArraySize).fill(initialValue));

    var tempChart;
    var timeChart;
    // Função para obter dados de temperatura via AJAX
    function obterDadosTemperatura() {
        fetch('/dados_temperatura')
            .then(response => response.json())
            .then(data => {
                atualizarGrafico(data.temperaturas,data.media,data.upper_limit,data.lower_limit,data.time,data.general_limit,data.enabled_sensor);
                atualizarModo(data.modo);
                atualizarEstado(data.estado,data.estado_ga);
            })
            .catch(error => console.error('Erro ao obter dados de temperatura:', error));
    }

    function obterNovosDadosTemperatura() {
        fetch('/dados_temperatura')
            .then(response => response.json())
            .then(data => {
                            atualizaDadosGrafico(data.temperaturas,data.media,data.upper_limit,data.lower_limit,data.time,data.general_limit,data.enabled_sensor);
                            atualizarModo(data.modo);
                            atualizarEstado(data.estado,data.estado_ga);
                          })
            .catch(error => console.error('Erro ao obter dados de temperatura:', error));
    }
    // Função para atualizar o gráfico com os novos dados
    function atualizarGrafico(temperaturas,media,upper,lower,time,general_limit,enabled_sensor) {
        var ctx = document.getElementById('temperatureChart').getContext('2d');
        configData.upper = upper;
        configData.lower = lower;
        configData.time = time;
        configData.general_limit = general_limit;
        configData.enabled = enabled_sensor;
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
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media+configData.upper[32]),
                        },
                        {
                            type: 'line',
                            label: 'Temperatura Média',
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media),
                        },
                        {
                            type: 'line',
                            label: 'Limite Inferior de Temperatura',
                            data: Array.from({length: temperaturas.real.length}, (_, i) => media-configData.lower[32]),
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

    function atualizaDadosGrafico(temperaturas,media,upper,lower,time,general_limit,enabled_sensor)
    {
        configData.upper = upper;
        configData.lower = lower;
        configData.time = time;
        configData.general_limit = general_limit;
        configData.enabled = enabled_sensor;

        var newFloatArray = temperaturas.real.slice(); 
        newFloatArray.push(media);
        newFloatArray.push(media+configData.upper[32]);
        newFloatArray.push(media-configData.lower[32]);
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
        tempChart.data.datasets[4].data = Array.from({length: temperaturas.real.length}, (_, i) => media)
        if (configData.general_limit){
            tempChart.data.datasets[3].data = Array.from({length: temperaturas.real.length}, (_, i) => media+configData.upper[32])
            tempChart.data.datasets[5].data = Array.from({length: temperaturas.real.length}, (_, i) => media-configData.lower[32])
        }else{
            tempChart.data.datasets[3].data = Array.from({length: temperaturas.real.length}, (_, i) => media+configData.upper[i])
            tempChart.data.datasets[5].data = Array.from({length: temperaturas.real.length}, (_, i) => media-configData.lower[i])
        }
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


    document.getElementById("button_config").addEventListener("click", function(){
        // Get form values
        configData.general_limit = document.getElementsByName("inlineRadioOptions")[0].checked;
        var sensor_selected = parseInt(document.getElementById("sensor_select").value);
        var upper = document.getElementById("upper_temp").value;
        var lower = document.getElementById("lower_temp").value;
        var time = document.getElementById("time").value;
        // Perform validation or other operations as needed
        if(upper.trim() === "" || lower.trim() === "" || time.trim() === "") {
          alert("Por favor preencha todos os campos.");
          return; // Prevent further execution
        }
    
        // If validation passes, proceed with form submission
        // For example, you can submit the form using AJAX or redirect to another page
        // Here, we'll just log the values to the console
        
        configData.upper[sensor_selected] = parseFloat(upper);
        configData.lower[sensor_selected] = parseFloat(lower);
        configData.time = parseInt(time);
        if (sensor_selected < 32 ){
            configData.enabled[sensor_selected] = document.getElementById('sensorCheckbox').checked;
        }

        enviaConfig();

      });

      document.getElementById("botao_modal").addEventListener("click", function(){
        // Get form values
        document.getElementById("time").value = configData.time;
        document.getElementById("upper_temp").value = configData.upper[32];
        document.getElementById("lower_temp").value = configData.lower[32];
        document.getElementById("sensor_select").value = "32"
        if (configData.general_limit){
            document.getElementsByName("inlineRadioOptions")[0].checked = true;
            document.getElementById("sensor_select").disabled = true;
            document.getElementById("sensorCheckbox").disabled = true;
        }else{
            document.getElementsByName("inlineRadioOptions")[1].checked = true;
            document.getElementById("sensor_select").disabled = false;
            document.getElementById("sensorCheckbox").disabled = false;
        }
    });

      document.getElementById('inlineRadio1').addEventListener('change', function () {
        if (document.getElementsByName("inlineRadioOptions")[0].checked){
            document.getElementById("sensor_select").disabled = true;
            document.getElementById("sensorCheckbox").disabled = true;
            document.getElementById("sensor_select").value = "32"
        }else{
            document.getElementById("sensor_select").disabled = false;
            document.getElementById("sensorCheckbox").disabled = false;
        }
        var sensor_selected = parseInt(document.getElementById("sensor_select").value);
        document.getElementById("upper_temp").value = configData.upper[sensor_selected];
        document.getElementById("lower_temp").value = configData.lower[sensor_selected];

      });

      document.getElementById('inlineRadio2').addEventListener('change', function () {
        if (document.getElementsByName("inlineRadioOptions")[0].checked){
            document.getElementById("sensor_select").disabled = true;
            document.getElementById("sensorCheckbox").disabled = true;
            document.getElementById("sensor_select").value = "32"
        }else{
            document.getElementById("sensor_select").disabled = false;
            document.getElementById("sensorCheckbox").disabled = false;
        }
        var sensor_selected = parseInt(document.getElementById("sensor_select").value);
        document.getElementById("upper_temp").value = configData.upper[sensor_selected];
        document.getElementById("lower_temp").value = configData.lower[sensor_selected];
      });

      document.getElementById('sensor_select').addEventListener('change', function () {

        var sensor_selected = parseInt(document.getElementById("sensor_select").value);
        document.getElementById("upper_temp").value = configData.upper[sensor_selected];
        document.getElementById("lower_temp").value = configData.lower[sensor_selected];
        document.getElementById("sensorCheckbox").checked = configData.enabled[sensor_selected];

    });

      document.getElementById('time').addEventListener('input', function () {
        var currentValue = parseInt(this.value);
        document.getElementById("form_info").textContent = "";
        // Check if the current value is less than 1
        if (currentValue < 1) {
          // If less than 1, set the value to 1
          this.value = 1;
          document.getElementById("form_info").textContent = "Valor do tempo deve ser um número inteiro maior que 1"
        }else{
            this.value = currentValue;
        }
      });

      document.getElementById('upper_temp').addEventListener('input', function () {
        var currentValue = parseFloat(this.value);
        document.getElementById("form_info").textContent = "";
        if (isNaN(currentValue)){
            document.getElementById("form_info").textContent = "Valor do limite superior deve ser um número. Use ',' para decimais: 1,5"
        }

        // Check if the current value is less than 1
        if (currentValue <= 0) {
          // If less than 1, set the value to 1
          this.value = 1;
          document.getElementById("form_info").textContent = "Valor do limite superior deve ser um número maior que 0"
        }

      });

      document.getElementById('lower_temp').addEventListener('input', function () {
        var currentValue = parseFloat(this.value);
        document.getElementById("form_info").textContent = "";
        if (isNaN(currentValue)){
            document.getElementById("form_info").textContent = "Valor do limite inferior deve ser um número. Use ',' para decimais: 1,5"
        }

        // Check if the current value is less than 1
        if (currentValue <= 0) {
          // If less than 1, set the value to 1
          this.value = 1;
          document.getElementById("form_info").textContent = "Valor do limite inferior deve ser um número maior que 0"
        }

      });


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
        .then(files => {
            
    
            // Download filtered files
            files.forEach(function(fileName) {
                var downloadUrl = "/downloadFile/" + fileName;
                downloadFile(downloadUrl);
            });
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
