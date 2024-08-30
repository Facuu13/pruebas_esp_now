function cargarDatos() {
    fetch('/data')
        .then(response => response.text())
        .then(data => {
            const sensorDataContainer = document.getElementById('sensor-data');
            sensorDataContainer.innerHTML = ''; // Limpiar contenido previo
            
            const sensors = data.trim().split("\n\n"); // Separar cada conjunto de datos

            sensors.forEach(sensor => {
                const [mac, topic, value] = sensor.split("\n");
                const card = `
                    <div class="sensor-card">
                        <p><strong>${mac}</strong></p>
                        <p>${topic}</p>
                        <p><span class="sensor-value">${value}</span></p>
                    </div>`;
                sensorDataContainer.innerHTML += card;
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

// Cargar datos al inicio
cargarDatos();

// Actualizar datos cada 5 segundos
setInterval(cargarDatos, 5000);
