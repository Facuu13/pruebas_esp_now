// Función para cargar los valores actuales en el formulario
function cargarConfiguracionActual() {
    fetch('/get_config')
        .then(response => response.json())
        .then(data => {
            document.getElementById('mode').value = data['mode'];
            document.getElementById('ssid').value = data['ssid'];
            document.getElementById('password').value = data['password'];
            document.getElementById('ap_ssid').value = data['ap_ssid'];
            document.getElementById('ap_password').value = data['ap_password'];
            document.getElementById('cliente_id').value = data['cliente_id'];
            document.getElementById('mqtt_broker').value = data['mqtt_broker'];
            document.getElementById('mqtt_user').value = data['mqtt_user'];
            document.getElementById('mqtt_pass').value = data['mqtt_pass'];
            document.getElementById('puerto').value = data['puerto'];

            // Combina los valores de fecha y hora
            document.getElementById('fecha').value = `${data['year']}-${String(data['month']).padStart(2, '0')}-${String(data['day']).padStart(2, '0')}`;
            document.getElementById('hora').value = `${String(data['hour']).padStart(2, '0')}:${String(data['minute']).padStart(2, '0')}`;

            // Llama a la función para verificar el modo
            verificarModo(data['mode']);
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
        puerto: parseInt(document.getElementById('puerto').value),

        // Enviar valores nulos si los campos están deshabilitados
        year: document.getElementById('fecha').disabled ? null : parseInt(document.getElementById('fecha').value.split('-')[0]),
        month: document.getElementById('fecha').disabled ? null : parseInt(document.getElementById('fecha').value.split('-')[1]),
        day: document.getElementById('fecha').disabled ? null : parseInt(document.getElementById('fecha').value.split('-')[2]),
        hour: document.getElementById('hora').disabled ? null : parseInt(document.getElementById('hora').value.split(':')[0]),
        minute: document.getElementById('hora').disabled ? null : parseInt(document.getElementById('hora').value.split(':')[1]),
        second: 0 // O agregar opción de segundos si es necesario
    };

    // Validaciones básicas
    const requiredFields = ['ssid', 'password', 'ap_ssid', 'ap_password', 'cliente_id', 'mqtt_broker', 'mqtt_user', 'mqtt_pass', 'puerto'];
    const isValid = requiredFields.every(field => config[field] && (field !== 'puerto' || !isNaN(config.puerto)));

    if (!isValid) {
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
        msg.style.color = data.status === 'success' ? 'green' : 'red';
        msg.textContent = data.status === 'success' ? 'Configuración actualizada exitosamente.' : `Error al actualizar la configuración: ${data.message}`;
        msg.style.display = 'block';

        // Opcional: reiniciar la página después de un breve retraso si la actualización fue exitosa
        if (data.status === 'success') {
            setTimeout(() => {
                location.reload();
            }, 2000);
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


// Función para verificar el modo y deshabilitar/permitir los campos de fecha y hora
function verificarModo(mode) {
    const fechaField = document.getElementById('fecha');
    const horaField = document.getElementById('hora');

    if (mode === 'CL') {
        fechaField.disabled = true;
        horaField.disabled = true;
    } else {
        fechaField.disabled = false;
        horaField.disabled = false;
    }
}

// Detectar cambio de modo en el formulario y ajustar la interfaz
document.getElementById('mode').addEventListener('change', function() {
    verificarModo(this.value);
});

// Ejecutar las funciones al cargar la página
window.onload = function() {
    cargarConfiguracionActual();
};
