// Función para manejar la carga de datos de sensores
function cargarDatos() {
    console.log('Cargando datos...'); // Para verificar si se llama la función

    fetch('/data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            const sensorDataContainer = document.getElementById("sensor-data");
            sensorDataContainer.innerHTML = ""; // Limpiar contenido previo

            const releDataContainer = document.getElementById("rele-data");
            releDataContainer.innerHTML = ""; // Limpiar contenido previo

            const sensors = data.trim().split("\n\n"); // Separar cada conjunto de datos

            sensors.forEach((sensor) => {
                const [mac, topic, value, modelo, hora] = sensor.split("\n");
                let isChecked = value.includes("True") ? "checked" : "";

                // Crear switch para sensor/rele/state
                if (topic.includes("sensor/rele/state")) {
                    const card = `
                        <div class="sensor-card">
                            <p><strong>Nodo: ${mac.split("/")[0]}</strong></p>
                            <p>Topic: ${topic}</p>
                            <label class="switch">
                                <input type="checkbox" ${isChecked} onclick="toggleRelay('${mac}', '${topic}', this)">
                                <span class="slider round"></span>
                            </label>
                            <p><span class="timestamp">Último Estado: ${hora}</span></p>
                        </div>`;
                    releDataContainer.innerHTML += card;
                } else {
                    // Determinar unidad según el topic
                    let unidad = '';
                    if (topic.includes('sensor/temp')) {
                        unidad = '°C';
                    } else if (topic.includes('sensor/hum')) {
                        unidad = '%';
                    } else if (topic.includes('sensor/co2')) {
                        unidad = 'ppm';
                    }

                    // Para otros tipos de sensores, mostrar el valor con la unidad correspondiente
                    const card = `
                        <div class="sensor-card">
                            <p><strong>Nodo: ${mac.split("/")[0]}</strong></p>
                            <p>Topic: ${topic}</p>
                            <p><span class="sensor-value">Valor: ${value} ${unidad}</span></p>
                            <p><span class="timestamp">Última Medición: ${hora}</span></p>
                            <p><span class="modelo">Modelo sensor: ${modelo}</span></p>
                        </div>`;
                    sensorDataContainer.innerHTML += card;
                }
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}


// Función para cambiar el estado del relé
function toggleRelay(mac, topic, element) {
    const newState = element.checked ? "True" : "False";
    console.log(`Cambiando estado del relé. MAC: ${mac}, Topic: ${topic}, Nuevo estado: ${newState}`);

    const data = {
        mac: mac,
        topic: topic,
        state: newState
    };

    fetch('/update_relay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(responseData => {
        console.log('Respuesta del servidor:', responseData);
    })
    .catch(error => {
        console.error('Error al enviar la solicitud:', error);
    });
}

// Función para manejar el logout
function handleLogout() {
    const logoutButton = document.getElementById('logout-btn');
    logoutButton.addEventListener('click', function() {
        // Redirigir a la página de login
        window.location.href = '/';
    });
}

// Ejecutar la función de cargar datos después de iniciar sesión correctamente
cargarDatos();

// Iniciar la actualización automática de los datos cada 5 segundos
setInterval(() => {
    cargarDatos();
}, 5000);

// Iniciar el manejo de logout
handleLogout();
