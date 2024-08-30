// script.js

function cargarDatos() {
    fetch('/data')
        .then(response => response.text())
        .then(data => {
            document.getElementById('sensor-data').innerText = data;
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

// Cargar datos al inicio
cargarDatos();
