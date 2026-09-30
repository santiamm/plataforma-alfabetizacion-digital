document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. TAMAÑO DE FUENTE DINÁMICO (A+ / A-)
    // ==========================================
    const tamanos = ['fuente-sm', 'fuente-md', 'fuente-lg', 'fuente-xl'];
    let indiceActual = 1; // 'fuente-md' es el tamaño normal por defecto

    // Cargar preferencia guardada
    const tamanoGuardado = localStorage.getItem('tamanoFuente');
    if (tamanoGuardado && tamanos.includes(tamanoGuardado)) {
        indiceActual = tamanos.indexOf(tamanoGuardado);
        aplicarTamano(tamanoGuardado);
    }

    const btnAumentar = document.getElementById('btnAumentarFuente');
    const btnDisminuir = document.getElementById('btnDisminuirFuente');
    const btnRestablecer = document.getElementById('btnRestablecerFuente');

    if (btnAumentar) {
        btnAumentar.addEventListener('click', () => {
            if (indiceActual < tamanos.length - 1) {
                indiceActual++;
                guardarYAplicarTamano();
            }
        });
    }

    if (btnDisminuir) {
        btnDisminuir.addEventListener('click', () => {
            if (indiceActual > 0) {
                indiceActual--;
                guardarYAplicarTamano();
            }
        });
    }

    if (btnRestablecer) {
        btnRestablecer.addEventListener('click', () => {
            indiceActual = 1; // Normal
            guardarYAplicarTamano();
        });
    }

    function guardarYAplicarTamano() {
        const claseSeleccionada = tamanos[indiceActual];
        localStorage.setItem('tamanoFuente', claseSeleccionada);
        aplicarTamano(claseSeleccionada);
    }

    function aplicarTamano(clase) {
        tamanos.forEach(t => document.body.classList.remove(t));
        document.body.classList.add(clase);
    }

    // ==========================================
    // 2. MODO ALTO CONTRASTE (WCAG)
    // ==========================================
    const estadoContraste = localStorage.getItem('modoAltoContraste');
    if (estadoContraste === 'activo') {
        document.body.classList.add('alto-contraste');
        actualizarBotonContraste(true);
    }

    const btnContraste = document.getElementById('btnAltoContraste');
    if (btnContraste) {
        btnContraste.addEventListener('click', (e) => {
            e.preventDefault();
            const activo = document.body.classList.toggle('alto-contraste');
            localStorage.setItem('modoAltoContraste', activo ? 'activo' : 'inactivo');
            actualizarBotonContraste(activo);
        });
    }

    function actualizarBotonContraste(activo) {
        if (!btnContraste) return;
        if (activo) {
            btnContraste.innerHTML = '<i class="bi bi-circle-half me-1"></i> Modo Normal';
            btnContraste.classList.remove('btn-outline-dark');
            btnContraste.classList.add('btn-warning');
        } else {
            btnContraste.innerHTML = '<i class="bi bi-circle-half me-1"></i> Alto Contraste';
            btnContraste.classList.remove('btn-warning');
            btnContraste.classList.add('btn-outline-dark');
        }
    }
});