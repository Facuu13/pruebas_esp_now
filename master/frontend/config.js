// Función para cargar los valores actuales en el formulario
function cargarConfiguracionActual() {
    fetch('/get_config')
        .then(response => response.json())
        .then(data => {
            document.getElementById('mode').value = data.mode;
            document.getElementById('ssid').value = data.ssid;
            document.getElementById('password').value = data.password;
            document.getElementById('ap_ssid').value = data.ap_ssid;
            document.getElementById('ap_password').value = data.ap_password;
            document.getElementById('cliente_id').value = data.cliente_id;
            document.getElementById('mqtt_broker').value = data.mqtt_broker;
            document.getElementById('mqtt_user').value = data.mqtt_user;
            document.getElementById('mqtt_pass').value = data.mqtt_pass;
            document.getElementById('puerto').value = data.puerto;
        })
        .catch(error => {
            console.error('Error al cargar la configuración actual:', error);
        });
}

// Función para manejar el envío del formulario
document.getElementById('config-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el comportamiento por defecto del formulario

    const config = {
        mode: document.getElementById('mode').value,
        ssid: document.getElementById('ssid').value,
        password: document.getElementById('password').value,
        ap_ssid: document.getElementById('ap_ssid').value,
        ap_password: document.getElementById('ap_password').value,
        cliente_id: document.getElementById('cliente_id').value,
        mqtt_broker: document.getElementById('mqtt_broker').value,
        mqtt_user: document.getElementById('mqtt_user').value,
        mqtt_pass: document.getElementById('mqtt_pass').value,
        puerto: parseInt(document.getElementById('puerto').value)
    };

    // Validaciones básicas
    if (!config.ssid || !config.password || !config.ap_ssid || !config.ap_password || 
        !config.cliente_id || !config.mqtt_broker || !config.mqtt_user || 
        !config.mqtt_pass || isNaN(config.puerto)) {
        alert('Por favor, completa todos los campos correctamente.');
        return;
    }

    // Enviar los datos al servidor
    fetch('/update_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        const msg = document.getElementById('response-msg');
        if (data.status === 'success') {
            msg.style.color = 'green';
            msg.textContent = 'Configuración actualizada exitosamente.';
            msg.style.display = 'block';
            // Opcional: reiniciar la página después de un breve retraso
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            msg.style.color = 'red';
            msg.textContent = 'Error al actualizar la configuración: ' + data.message;
            msg.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error al enviar la configuración:', error);
        const msg = document.getElementById('response-msg');
        msg.style.color = 'red';
        msg.textContent = 'Error al enviar la configuración.';
        msg.style.display = 'block';
    });
});

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

// Ejecutar las funciones al cargar la página
window.onload = function() {
    cargarConfiguracionActual();
    togglePasswordVisibility();
    handleLogout();
};
