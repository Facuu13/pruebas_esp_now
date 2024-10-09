// Función para manejar el login
function handleLogin() {
    const loginButton = document.getElementById('login-btn');
    loginButton.addEventListener('click', function() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === 'facu' && password === 'wentux') {
            // Redirigir a la página principal
            window.location.href = '/home';
        } else {
            // Mostrar mensaje de error
            document.getElementById('error-msg').style.display = 'block';
        }
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

// Ejecutar las funciones de manejo de login y visibilidad de contraseña
handleLogin();
togglePasswordVisibility();
