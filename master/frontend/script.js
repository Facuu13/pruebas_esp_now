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
            const releDataContainer = document.getElementById("rele-data");

            sensorDataContainer.innerHTML = ""; // Limpiar contenido previo
            releDataContainer.innerHTML = ""; // Limpiar contenido previo

            // Si no hay datos recibidos, mostrar mensajes de "no hay datos"
            if (!data.trim()) {
                sensorDataContainer.innerHTML = "<p>No hay sensores cargados.</p>";
                releDataContainer.innerHTML = "<p>No hay relés cargados.</p>";
                return; // Salir de la función
            }

            const sensors = data.trim().split("\n\n"); // Separar cada conjunto de datos

            let sensorCount = 0;
            let releCount = 0;

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
                    releCount++;
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

                    const card = `
                        <div class="sensor-card">
                            <p><strong>Nodo: ${mac.split("/")[0]}</strong></p>
                            <p>Topic: ${topic}</p>
                            <p><span class="sensor-value">Valor: ${value} ${unidad}</span></p>
                            <p><span class="timestamp">Última Medición: ${hora}</span></p>
                            <p><span class="modelo">Modelo sensor: ${modelo}</span></p>
                        </div>`;
                    sensorDataContainer.innerHTML += card;
                    sensorCount++;
                }
            });

            // Mostrar mensaje si no hay sensores cargados
            if (sensorCount === 0) {
                sensorDataContainer.innerHTML = "<p>No hay sensores cargados.</p>";
            }

            // Mostrar mensaje si no hay relés cargados
            if (releCount === 0) {
                releDataContainer.innerHTML = "<p>No hay relés cargados.</p>";
            }
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}


// Función para verificar si el usuario está autenticado
function checkAuthentication() {
    const username = localStorage.getItem('username');
    const password = localStorage.getItem('password');

    if (!username || !password) {
        // Redirigir a la página de login si no hay usuario y contraseña en localStorage
        window.location.href = '/';
        window.alert("No tiene autorizacion para ingresar a esta pantalla")
    }
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
        // Eliminar usuario y contraseña del localStorage
        localStorage.removeItem('username');
        localStorage.removeItem('password');
        // Redirigir a la página de login
        window.location.href = '/';
    });
}

// Verificar autenticación al cargar la página
checkAuthentication();

// Ejecutar la función de cargar datos después de iniciar sesión correctamente
cargarDatos();

// Iniciar la actualización automática de los datos cada 5 segundos
setInterval(() => {
    cargarDatos();
}, 5000);

// Iniciar el manejo de logout
handleLogout();
