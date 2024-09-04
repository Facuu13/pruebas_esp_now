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

// Iniciar manejo de login y logout
handleLogin();
handleLogout();
