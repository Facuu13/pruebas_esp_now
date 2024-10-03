// Función para manejar el login
function handleLogin() {
    const loginButton = document.getElementById('login-btn');
    loginButton.addEventListener('click', function() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === 'facu' && password === 'wentux') {
            // Ocultar la sección de login y mostrar la página principal
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-page').classList.remove('hidden');

            // Cargar los datos inmediatamente después de iniciar sesión correctamente
            cargarDatos();

            // Iniciar la actualización automática cada 5 segundos
            setInterval(() => {
                cargarDatos();
            }, 5000);
        } else {
            // Mostrar mensaje de error
            document.getElementById('error-msg').style.display = 'block';
        }
    });
}

// Función para cargar los datos de los sensores
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
            const timestamp = new Date().toLocaleString(); // Generar el timestamp
            // Crear switch para sensor/rele/state
            if (topic.includes("sensor/rele/state")) {
              const card = `
                        <div class="sensor-card">
                            <p><strong>Sensor: ${mac.split("/")[0]}</strong></p>
                            <p>Topic: ${topic}</p>
                            <label class="switch">
                            <input type="checkbox" ${isChecked} onclick="toggleRelay('${mac}', '${topic}', this)">
                                <span class="slider round"></span>
                            </label>
                            <p><span class="timestamp">Último Estado: ${timestamp}</span></p>
                        </div>`;
              releDataContainer.innerHTML += card;
            } else {
              // Para otros tipos de sensores, simplemente mostrar el valor
              const card = `
                        <div class="sensor-card">
                            <p><strong>Sensor: ${mac.split("/")[0]}</strong></p>
                            <p>Topic: ${topic}</p>
                            <p><span class="sensor-value">Valor: ${value}</span></p>
                            <p><span class="timestamp">Última Medición: ${hora}</span></p>
                            <p><span class="modelo">Modelo sensor: ${modelo}</span></p>
                        </div>`;
              sensorDataContainer.innerHTML += card;
            }
          });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

function toggleRelay(mac, topic, element) {
    const newState = element.checked ? "True" : "False";
    console.log(`Cambiando estado del relé. MAC: ${mac}, Topic: ${topic}, Nuevo estado: ${newState}`);

    // Crear el objeto de datos para enviar en el formato correcto
    const data = {
        mac: mac,
        topic: topic,
        state: newState
    };

    // Enviar la solicitud POST al servidor
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
        // Mostrar la sección de login y ocultar la página principal
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('main-page').classList.add('hidden');

        // Limpiar los campos de login
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';

        // Opcional: detener la actualización automática si es necesario
        // Si es necesario detener el setInterval, guardar su ID y usar clearInterval aquí.
    });
}

// Función para mostrar u ocultar la contraseña
function togglePasswordVisibility() {
    const passwordField = document.getElementById('password');
    const toggleCheckbox = document.getElementById('toggle-password');

    toggleCheckbox.addEventListener('change', function() {
        if (this.checked) {
            passwordField.type = 'text'; // Mostrar contraseña
        } else {
            passwordField.type = 'password'; // Ocultar contraseña
        }
    });
}

// Ejecutar la función para manejar la visibilidad de la contraseña
togglePasswordVisibility();

// Iniciar manejo de login y logout
handleLogin();
handleLogout();
