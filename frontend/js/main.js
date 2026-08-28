// Esperar a que cargue todo el documento
document.addEventListener('DOMContentLoaded', () => {
    
    // -------------------------------------------------------------
    // 1. Accesibilidad: Mostrar / Ocultar Contraseñas
    // -------------------------------------------------------------
    function setupPasswordToggle(btnId, inputId, iconId) {
        const btn = document.getElementById(btnId);
        const input = document.getElementById(inputId);
        const icon = document.getElementById(iconId);

        if (btn && input && icon) {
            btn.addEventListener('click', () => {
                const esPassword = input.getAttribute('type') === 'password';
                if (esPassword) {
                    input.setAttribute('type', 'text');
                    icon.classList.replace('bi-eye-fill', 'bi-eye-slash-fill');
                } else {
                    input.setAttribute('type', 'password');
                    icon.classList.replace('bi-eye-slash-fill', 'bi-eye-fill');
                }
            });
        }
    }

    setupPasswordToggle('btnTogglePassword', 'password', 'iconoOjo');
    setupPasswordToggle('btnToggleRegPassword', 'regPassword', 'iconoRegOjo');


    // -------------------------------------------------------------
    // 2. Manejo de Registro de Usuario
    // -------------------------------------------------------------
    const registroForm = document.getElementById('registroForm');
    if (registroForm) {
        registroForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const nombre = document.getElementById('nombre').value.trim();
            const apellido = document.getElementById('apellido').value.trim();
            const correo = document.getElementById('correo').value.trim();
            const password = document.getElementById('regPassword').value.trim();

            if (!nombre || !apellido || !correo || !password) {
                alert('Por favor, completa todos los campos requeridos.');
                return;
            }

            const datosUsuario = { nombre, apellido, correo, password };

            try {
                const respuesta = await fetch('http://127.0.0.1:5000/api/registro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datosUsuario)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok) {
                    alert('¡Registro exitoso! Ahora puedes iniciar sesión con tu cuenta.');
                    window.location.href = 'login.html';
                } else {
                    alert('Atención: ' + (resultado.mensaje || 'No se pudo completar el registro.'));
                }
            } catch (error) {
                console.error('Error al conectar con el backend:', error);
                alert('No se pudo conectar con el servidor. Verifica que Flask esté encendido.');
            }
        });
    }


    // -------------------------------------------------------------
    // 3. Manejo de Inicio de Sesión (Login)
    // -------------------------------------------------------------
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const correo = document.getElementById('correo').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!correo || !password) {
                alert('Por favor ingresa tu correo y contraseña.');
                return;
            }

            const credenciales = { correo, password };

            try {
                const respuesta = await fetch('http://127.0.0.1:5000/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credenciales)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok) {
                    // Guardar nombre y sesión de forma local
                    localStorage.setItem('usuario_nombre', resultado.nombre || 'Estudiante');
                    localStorage.setItem('usuario_id', resultado.id_usuario || '');

                    window.location.href = 'dashboard.html';
                } else {
                    alert('Error: ' + (resultado.mensaje || 'Correo o contraseña incorrectos.'));
                }
            } catch (error) {
                console.error('Error al conectar con el backend:', error);
                alert('No se pudo conectar con el servidor. Verifica que Flask esté encendido.');
            }
        });
    }


    // -------------------------------------------------------------
    // 4. Personalización del Dashboard
    // -------------------------------------------------------------
    const nombreUsuarioSpan = document.getElementById('nombreUsuario');
    if (nombreUsuarioSpan) {
        const usuarioGuardado = localStorage.getItem('usuario_nombre');
        if (usuarioGuardado) {
            nombreUsuarioSpan.textContent = usuarioGuardado;
        }
    }

});