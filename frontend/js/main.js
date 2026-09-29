// Esperar a que cargue todo el documento
document.addEventListener('DOMContentLoaded', () => {

    const API_BASE = 'http://127.0.0.1:5000';
    const API_URL = API_BASE;
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

            const nombre = document.getElementById('nombre')?.value.trim() || '';
            const apellido = document.getElementById('apellido')?.value.trim() || '';
            const correo = document.getElementById('correo')?.value.trim() || '';
            const telefono = document.getElementById('telefono')?.value.trim() || '';
            const password = document.getElementById('regPassword')?.value.trim() || '';

            if (!nombre || !password || (!correo && !telefono)) {
                alert('Por favor, completa tu nombre, contraseña y al menos un correo o teléfono.');
                return;
            }

            const datosUsuario = { nombre, apellido, correo, telefono, password };

            try {
                const respuesta = await fetch(`${API_BASE}/registro`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datosUsuario)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok) {
                    alert('¡Registro exitoso! Ahora puedes iniciar sesión con tu cuenta.');
                    window.location.href = 'login.html';
                } else {
                    alert('Atención: ' + (resultado.mensaje || resultado.error || 'No se pudo completar el registro.'));
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

            // Acepta campo 'correo', 'telefono' o 'identificador' según el HTML que tengas
            const inputIdentificador = document.getElementById('correo') || document.getElementById('telefono') || document.getElementById('identificador');
            const identificador = inputIdentificador ? inputIdentificador.value.trim() : '';
            const password = document.getElementById('password')?.value.trim() || '';

            if (!identificador || !password) {
                alert('Por favor ingresa tu usuario (correo o teléfono) y tu contraseña.');
                return;
            }

            const credenciales = { correo: identificador, telefono: identificador, password };

            try {
                const respuesta = await fetch(`${API_BASE}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(credenciales)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok) {
                    // Guardar token JWT y datos de sesión
                    if (resultado.access_token) {
                        localStorage.setItem('token', resultado.access_token);
                    }
                    localStorage.setItem('usuario_nombre', resultado.nombre || 'Estudiante');
                    localStorage.setItem('usuario_id', resultado.id_usuario || '');

                    window.location.href = 'dashboard.html';
                } else {
                    alert('Error: ' + (resultado.mensaje || resultado.error || 'Credenciales incorrectas.'));
                }
            } catch (error) {
                console.error('Error al conectar con el backend:', error);
                alert('No se pudo conectar con el servidor. Verifica que Flask esté encendido.');
            }
        });
    }


   // -------------------------------------------------------------
    // 4. Lógica Dinámica del Dashboard (Usuario, Progreso y Módulos)
    // -------------------------------------------------------------
    const contenedorModulos = document.getElementById('contenedorModulos');
    const token = localStorage.getItem('token');

    if (contenedorModulos) {
        // Redirigir a login si no hay sesión iniciada
        if (!token) {
            window.location.href = 'login.html';
            return;
        }

        // Pintar nombre guardado inmediatamente
        const nombreGuardado = localStorage.getItem('usuario_nombre');
        const nombreSpan = document.getElementById('nombreUsuario');
        if (nombreSpan && nombreGuardado) {
            nombreSpan.textContent = nombreGuardado;
        }

        // Cargar datos y módulos del backend
        cargarDashboard();
    }

    async function cargarDashboard() {
        try {
            // 1. Obtener los módulos creados en la base de datos
            const resEstudios = await fetch(`${API_URL}/estudios`);
            const estudios = await resEstudios.json();

            // 2. Obtener el progreso del usuario y filtrar duplicados con new Set()
            let completadosIds = [];
            try {
                const resProgreso = await fetch(`${API_URL}/progreso`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (resProgreso.ok) {
                    const progresos = await resProgreso.json();
                    if (Array.isArray(progresos)) {
                        // [...new Set(...)] elimina IDs repetidos aunque se hayan enviado varias veces
                        completadosIds = [...new Set(progresos.map(p => p.estudio_id))];
                    }
                } else if (resProgreso.status === 401) {
                    localStorage.clear();
                    window.location.href = 'login.html';
                    return;
                }
            } catch (errProgreso) {
                console.warn('Progreso no disponible:', errProgreso);
            }

            // 3. Actualizar la barra de progreso (calculado sobre el total real de módulos)
            const total = estudios.length > 0 ? estudios.length : 7;
            const completados = completadosIds.length;
            // Tope estricto en 100%
            const porcentaje = Math.min(Math.round((completados / total) * 100), 100);

            const porcentajeTexto = document.getElementById('porcentajeTotal');
            const barraProgreso = document.getElementById('barraProgreso');

            if (porcentajeTexto) porcentajeTexto.textContent = `${porcentaje}%`;
            if (barraProgreso) {
                barraProgreso.style.width = `${porcentaje}%`;
                barraProgreso.setAttribute('aria-valuenow', porcentaje);
            }

            // 4. Configuraciones de estilo para los 7 módulos
            const configuracionTarjetas = [
                { colorBg: 'bg-primary text-white', icono: 'bi-display' },
                { colorBg: 'bg-success text-white', icono: 'bi-globe2' },
                { colorBg: 'bg-warning text-dark', icono: 'bi-shield-lock-fill' },
                { colorBg: 'bg-info text-dark', icono: 'bi-card-checklist' },
                { colorBg: 'bg-success text-white', icono: 'bi-chat-dots-fill' },
                { colorBg: 'bg-primary text-white', icono: 'bi-wallet2' },
                { colorBg: 'bg-secondary text-white', icono: 'bi-shield-check' }
            ];

            contenedorModulos.innerHTML = '';

            estudios.forEach((modulo, index) => {
                const config = configuracionTarjetas[index % configuracionTarjetas.length];
                const estaCompletado = completadosIds.includes(modulo.id);

                const cardHTML = `
                    <div class="col-12 col-md-6">
                        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 d-flex flex-column justify-content-between bg-white">
                            <div>
                                <div class="d-flex align-items-center mb-3">
                                    <div class="${config.colorBg} rounded-circle p-3 d-inline-flex align-items-center justify-content-center me-3" style="width: 60px; height: 60px;">
                                        <i class="bi ${config.icono} fs-2"></i>
                                    </div>
                                    <div>
                                        <span class="badge ${estaCompletado ? 'bg-success' : 'bg-primary'} fs-6 px-3 py-1 rounded-pill">
                                            Módulo ${index + 1}
                                        </span>
                                        <div class="${estaCompletado ? 'text-success' : 'text-muted'} fw-bold fs-6 mt-1">
                                            <i class="bi ${estaCompletado ? 'bi-check-circle-fill' : 'bi-clock'}"></i> 
                                            ${estaCompletado ? 'Completado' : 'Pendiente'}
                                        </div>
                                    </div>
                                </div>
                                <h3 class="h4 fw-bold text-dark">${modulo.titulo}</h3>
                                <p class="fs-5 text-muted">${modulo.descripcion}</p>
                            </div>
                            <div class="mt-3">
                                <a href="leccion.html?id=${modulo.id}" class="btn ${estaCompletado ? 'btn-outline-success' : 'btn-primary'} btn-lg w-100 py-3 fs-5 fw-semibold rounded-pill">
                                    <i class="bi ${estaCompletado ? 'bi-arrow-clockwise' : 'bi-play-circle-fill'} me-2"></i> 
                                    ${estaCompletado ? 'Repasar Módulo' : 'Empezar Módulo'}
                                </a>
                            </div>
                        </div>
                    </div>
                `;
                contenedorModulos.innerHTML += cardHTML;
            });

        } catch (error) {
            console.error('Error al cargar datos del dashboard:', error);
        }
    }

    // Botón Salir
    const btnSalir = document.getElementById('btnCerrarSesion');
    if (btnSalir) {
        btnSalir.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }


    // -------------------------------------------------------------
    // 5. Accesibilidad: Aumentar / Disminuir tamaño de fuente
    // -------------------------------------------------------------
    const btnAumentar = document.getElementById('btnAumentarTexto');
    const btnDisminuir = document.getElementById('btnDisminuirTexto');
    const contenedorTexto = document.getElementById('contenidoLeccion');

    if (btnAumentar && btnDisminuir && contenedorTexto) {
        let nivelZoom = 1.0;

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
            const elementosTexto = contenedorTexto.querySelectorAll('h1, h2, h3, h4, p, li, strong, span');
            elementosTexto.forEach(el => {
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

                if (botonesFinal) {
                    botonesFinal.classList.remove('d-none');
                }
            });
// -------------------------------------------------------------
    // 7. Carga Dinámica de Contenido según Módulo (?id=)
    // -------------------------------------------------------------
    const cuerpoDinamico = document.getElementById('cuerpoDinamicoLeccion');
    const badgeModulo = document.getElementById('badgeModulo');
    const tituloLeccion = document.getElementById('tituloLeccion');
    const descripcionLeccion = document.getElementById('descripcionLeccion');
    const btnIrAPractica = document.getElementById('btnIrAPractica');

    if (cuerpoDinamico && tituloLeccion) {
        // Obtener el ID de la URL (por ejemplo: leccion.html?id=2)
        const params = new URLSearchParams(window.location.search);
        const moduloId = parseInt(params.get('id')) || 1;

        if (btnIrAPractica) {
            btnIrAPractica.href = `ejercicio.html?id=${moduloId}`;
        }

        // Si es el módulo 1, dejamos el HTML original del mouse y teclado
        if (moduloId === 2) {
            badgeModulo.textContent = 'Módulo 2: Internet y Comunicación';
            tituloLeccion.textContent = '2. Navegación Web y Correo Electrónico';
            descripcionLeccion.textContent = 'Aprende a buscar información en internet y cómo comunicarte con familiares y amigos sin complicaciones.';
            
            cuerpoDinamico.innerHTML = `
                <section class="mb-5">
                    <h2 class="h3 fw-bold text-success mb-3">
                        <i class="bi bi-globe2 me-2"></i>La Ventana al Mundo: El Navegador
                    </h2>
                    <div class="card bg-white border-2 border-success-subtle p-4 mb-4 rounded-4 shadow-sm">
                        <p class="fs-5 text-muted mb-2">Un <strong>navegador</strong> es el programa que usas para entrar a internet (como Google Chrome o Edge).</p>
                        <div class="p-3 bg-light rounded-3 border">
                            <h4 class="fw-bold fs-5 text-dark mb-1"><i class="bi bi-search me-2 text-primary"></i>La Barra de Búsqueda</h4>
                            <p class="fs-5 mb-0">Escribe palabras sencillas, por ejemplo: <em>"clima de hoy"</em> o <em>"noticias del día"</em> y presiona la tecla <strong>ENTER</strong>.</p>
                        </div>
                    </div>
                </section>

                <section class="mb-4">
                    <h2 class="h3 fw-bold text-success mb-3">
                        <i class="bi bi-envelope-check-fill me-2"></i>El Correo Electrónico
                    </h2>
                    <div class="row g-4 my-2">
                        <div class="col-12 col-md-6">
                            <div class="p-4 bg-success-subtle text-success-emphasis rounded-4 border border-2 border-success h-100">
                                <h3 class="h4 fw-bold mb-2">Bandeja de Entrada</h3>
                                <p class="fs-5 mb-0">Es como el buzón de tu casa: allí llegan los mensajes nuevos que te envían.</p>
                            </div>
                        </div>
                        <div class="col-12 col-md-6">
                            <div class="p-4 bg-light rounded-4 border border-2 border-secondary h-100">
                                <h3 class="h4 fw-bold text-dark mb-2">Redactar Mensaje</h3>
                                <p class="fs-5 text-muted mb-0">El botón que usas cuando deseas escribirle una carta o recado a alguien.</p>
                            </div>
                        </div>
                    </div>
                </section>

                <div class="alert alert-success border-0 rounded-4 p-4 mt-4 d-flex align-items-center">
                    <i class="bi bi-lightbulb-fill display-4 text-success-emphasis me-3"></i>
                    <div>
                        <h4 class="alert-heading fw-bold mb-1">¡Consejo Útil!</h4>
                        <p class="fs-5 mb-0">No compartas cadenas de mensajes ni abras enlaces que te lleguen de personas que no conozcas.</p>
                    </div>
                </div>
            `;
        } else if (moduloId === 3) {
            badgeModulo.textContent = 'Módulo 3: Seguridad Digital';
            tituloLeccion.textContent = '3. Protección Personal y Contraseñas Seguras';
            descripcionLeccion.textContent = 'Aprende a reconocer engaños, proteger tus datos personales y navegar con total tranquilidad.';
            
            cuerpoDinamico.innerHTML = `
                <section class="mb-5">
                    <h2 class="h3 fw-bold text-warning-emphasis mb-3">
                        <i class="bi bi-shield-lock-fill me-2"></i>¿Cómo crear una contraseña segura?
                    </h2>
                    <div class="card bg-white border-2 border-warning-subtle p-4 mb-4 rounded-4 shadow-sm">
                        <p class="fs-5 text-muted mb-2">Una contraseña es la llave digital de tus cuentas personales.</p>
                        <ul class="list-group list-group-flush fs-5">
                            <li class="list-group-item py-3 px-0">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>Usa una combinación de palabras, números y símbolos.
                            </li>
                            <li class="list-group-item py-3 px-0">
                                <i class="bi bi-x-circle-fill text-danger me-2"></i><strong>Evita</strong> usar fechas de cumpleaños, tu número de documento o "123456".
                            </li>
                        </ul>
                    </div>
                </section>

                <div class="alert alert-danger border-0 rounded-4 p-4 mt-4 d-flex align-items-center">
                    <i class="bi bi-exclamation-triangle-fill display-4 text-danger me-3"></i>
                    <div>
                        <h4 class="alert-heading fw-bold mb-1">¡Regla de Oro de Seguridad!</h4>
                        <p class="fs-5 mb-0">Ningún banco ni entidad pública te llamará ni te enviará mensajes pidiéndote tu contraseña. Nunca la compartas con nadie.</p>
                    </div>
                </div>
            `;
        } else if (moduloId === 4) {
            badgeModulo.textContent = 'Módulo 4: Servicios Digitales Cotidianos';
            tituloLeccion.textContent = '4. Trámites, Citas Médicas y Servicios en Línea';
            descripcionLeccion.textContent = 'Descubre cómo consultar trámites del gobierno, turnos de salud y facturas de servicios sin salir de casa.';
            
            cuerpoDinamico.innerHTML = `
                <section class="mb-5">
                    <h2 class="h3 fw-bold text-info-emphasis mb-3">
                        <i class="bi bi-card-checklist me-2"></i>Pasos para Trámites en Línea
                    </h2>
                    <div class="card bg-white border-2 border-info-subtle p-4 mb-4 rounded-4 shadow-sm">
                        <div class="row g-3 fs-5">
                            <div class="col-12 col-md-4">
                                <div class="p-3 bg-light rounded-3 text-center border h-100">
                                    <div class="display-6 fw-bold text-primary mb-2">1</div>
                                    <strong>Documento a la mano:</strong> Ten listo tu número de identificación.
                                </div>
                            </div>
                            <div class="col-12 col-md-4">
                                <div class="p-3 bg-light rounded-3 text-center border h-100">
                                    <div class="display-6 fw-bold text-primary mb-2">2</div>
                                    <strong>Datos de contacto:</strong> Asegúrate de saber tu número de celular o correo.
                                </div>
                            </div>
                            <div class="col-12 col-md-4">
                                <div class="p-3 bg-light rounded-3 text-center border h-100">
                                    <div class="display-6 fw-bold text-primary mb-2">3</div>
                                    <strong>Guardar soporte:</strong> Toma nota o captura del número de turno o radicado.
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <div class="alert alert-info border-0 rounded-4 p-4 mt-4 d-flex align-items-center">
                    <i class="bi bi-lightbulb-fill display-4 text-info-emphasis me-3"></i>
                    <div>
                        <h4 class="alert-heading fw-bold mb-1">¡Consejo Útil!</h4>
                        <p class="fs-5 mb-0">Revisa siempre que las direcciones web de trámites oficiales terminen en <strong>.gov.co</strong> para estar seguro de su autenticidad.</p>
                    </div>
                </div>
            `;
        }
    }
        });
    }

});