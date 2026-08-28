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

// -------------------------------------------------------------
    // 5. Accesibilidad: Aumentar / Disminuir tamaño de fuente
    // -------------------------------------------------------------
    const btnAumentar = document.getElementById('btnAumentarTexto');
    const btnDisminuir = document.getElementById('btnDisminuirTexto');
    const contenedorTexto = document.getElementById('contenidoLeccion');

    if (btnAumentar && btnDisminuir && contenedorTexto) {
        let nivelZoom = 1.0; // Escala base 100%

        btnAumentar.addEventListener('click', () => {
            if (nivelZoom < 1.35) {
                nivelZoom += 0.1;
                aplicarEscalaTexto();
            }
        });

        btnDisminuir.addEventListener('click', () => {
            if (nivelZoom > 0.9) {
                nivelZoom -= 0.1;
                aplicarEscalaTexto();
            }
        });

        function aplicarEscalaTexto() {
            // Selecciona todos los textos dentro de la lección
            const elementosTexto = contenedorTexto.querySelectorAll('h1, h2, h3, h4, p, li, strong, span');
            elementosTexto.forEach(el => {
                // Si no tiene guardado su tamaño original, lo guardamos
                if (!el.dataset.baseSize) {
                    const estilo = window.getComputedStyle(el);
                    el.dataset.baseSize = parseFloat(estilo.fontSize);
                }
                const tamanoOriginal = parseFloat(el.dataset.baseSize);
                el.style.fontSize = `${tamanoOriginal * nivelZoom}px`;
            });
        }
    }

    // -------------------------------------------------------------
    // 6. Lógica interactiva de Ejercicios y Retroalimentación
    // -------------------------------------------------------------
    const botonesOpcion = document.querySelectorAll('.opcion-btn');
    const cajaRetro = document.getElementById('cajaRetroalimentacion');
    const tituloRetro = document.getElementById('tituloRetro');
    const mensajeRetro = document.getElementById('mensajeRetro');
    const iconoRetro = document.getElementById('iconoRetro');
    const botonesFinal = document.getElementById('botonesAccionFinal');

    if (botonesOpcion.length > 0 && cajaRetro) {
        botonesOpcion.forEach(boton => {
            boton.addEventListener('click', () => {
                const esCorrecta = boton.getAttribute('data-correcta') === 'true';

                // Deshabilitar las opciones para evitar múltiples clics
                botonesOpcion.forEach(b => b.classList.add('disabled'));

                cajaRetro.classList.remove('d-none', 'alert-success', 'alert-danger', 'bg-success-subtle', 'bg-danger-subtle', 'text-success-emphasis', 'text-danger-emphasis');

                if (esCorrecta) {
                    boton.classList.remove('btn-outline-primary');
                    boton.classList.add('btn-success');

                    cajaRetro.classList.add('bg-success-subtle', 'text-success-emphasis', 'border', 'border-success');
                    iconoRetro.className = 'bi bi-check-circle-fill text-success fs-1 me-3';
                    tituloRetro.textContent = '¡Excelente! Respuesta Correcta';
                    mensajeRetro.textContent = 'El botón izquierdo es el principal y se utiliza para seleccionar elementos, abrir archivos y pulsar botones.';
                } else {
                    boton.classList.remove('btn-outline-primary');
                    boton.classList.add('btn-danger');

                    cajaRetro.classList.add('bg-danger-subtle', 'text-danger-emphasis', 'border', 'border-danger');
                    iconoRetro.className = 'bi bi-exclamation-triangle-fill text-danger fs-1 me-3';
                    tituloRetro.textContent = '¡Casi lo logras! Vamos a repasar';
                    mensajeRetro.textContent = 'Recuerda que el botón principal es el izquierdo. El derecho se usa para ver listas de opciones.';
                }

                // Mostrar el botón de avance final
                if (botonesFinal) {
                    botonesFinal.classList.remove('d-none');
                }
            });
        });
    }