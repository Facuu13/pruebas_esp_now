function cargarDatos() {
    fetch('/data')
        .then(response => response.text())
        .then(data => {
            const sensorDataContainer = document.getElementById('sensor-data');
            sensorDataContainer.innerHTML = ''; // Limpiar contenido previo
            
            const sensors = data.trim().split("\n\n"); // Separar cada conjunto de datos

            sensors.forEach(sensor => {
                const [mac, topic, value] = sensor.split("\n");
                let isChecked = value.includes("True") ? "checked" : "";

                // Crear switch para sensor/rele/state
                if (topic.includes("sensor/rele/state")) {
                    const card = `
                        <div class="sensor-card">
                            <p><strong>${mac.split("/")[0]}</strong></p>
                            <p>${topic}</p>
                            <label class="switch">
                                <input type="checkbox" ${isChecked} disabled>
                                <span class="slider round"></span>
                            </label>
                        </div>`;
                    sensorDataContainer.innerHTML += card;
                } else {
                    // Para otros tipos de sensores, simplemente mostrar el valor
                    const card = `
                        <div class="sensor-card">
                            <p><strong>Sensor: ${mac.split("/")[0]}</strong></p>
                            <p>${topic}</p>
                            <p><span class="sensor-value">${value}</span></p>
                        </div>`;
                    sensorDataContainer.innerHTML += card;
                }
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

// Cargar datos al inicio
cargarDatos();

// Actualizar datos cada 5 segundos
setInterval(cargarDatos, 5000);
