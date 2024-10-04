// Función para cargar los valores actuales en el formulario
function cargarConfiguracionActual() {
    fetch('/get_config')
        .then(response => response.json())
        .then(data => {
            // Usar un bucle para asignar valores
            const fields = ['mode', 'ssid', 'password', 'ap_ssid', 'ap_password', 'cliente_id', 'mqtt_broker', 'mqtt_user', 'mqtt_pass', 'puerto'];
            fields.forEach(field => {
                document.getElementById(field).value = data[field];
            });
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

        // Opcional: reiniciar la página después de un breve retraso
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

// Ejecutar las funciones al cargar la página
window.onload = function() {
    cargarConfiguracionActual();
};
