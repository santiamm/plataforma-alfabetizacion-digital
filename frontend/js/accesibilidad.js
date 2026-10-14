(function () {
    const CLAVE_TAMANO = 'tamanoFuente';
    const CLAVE_CONTRASTE = 'modoAltoContraste';
    const tamanos = ['fuente-sm', 'fuente-md', 'fuente-lg', 'fuente-xl'];
    const INDICE_NORMAL = 1;
    const raiz = document.documentElement;

    function leer(clave) {
        try {
            return localStorage.getItem(clave);
        } catch (error) {
            return null;
        }
    }

    function guardar(clave, valor) {
        try {
            localStorage.setItem(clave, valor);
        } catch (error) {
            return;
        }
    }

    let indice = tamanos.indexOf(leer(CLAVE_TAMANO));
    if (indice === -1) indice = INDICE_NORMAL;
    let contrasteActivo = leer(CLAVE_CONTRASTE) === 'activo';

    function aplicarTamano() {
        tamanos.forEach(t => raiz.classList.remove(t));
        raiz.classList.add(tamanos[indice]);
    }

    function aplicarContraste() {
        raiz.classList.toggle('alto-contraste', contrasteActivo);
    }

    aplicarTamano();
    aplicarContraste();

    function crearBarra() {
        const barra = document.createElement('div');
        barra.className = 'barra-accesibilidad bg-white border-bottom py-2 no-print';
        barra.setAttribute('role', 'region');
        barra.setAttribute('aria-label', 'Opciones de accesibilidad');
        barra.innerHTML =
            '<div class="container d-flex flex-wrap justify-content-center justify-content-md-end align-items-center gap-2">' +
                '<div class="btn-group shadow-sm" role="group" aria-label="Tamaño del texto">' +
                    '<button type="button" id="btnDisminuirFuente" class="btn btn-outline-primary btn-lg fs-5 fw-bold" aria-label="Reducir el tamaño del texto">A-</button>' +
                    '<button type="button" id="btnRestablecerFuente" class="btn btn-outline-primary btn-lg fs-6" aria-label="Restablecer el tamaño normal del texto">Normal</button>' +
                    '<button type="button" id="btnAumentarFuente" class="btn btn-outline-primary btn-lg fs-5 fw-bold" aria-label="Aumentar el tamaño del texto">A+</button>' +
                '</div>' +
                '<button type="button" id="btnAltoContraste" class="btn btn-outline-dark btn-lg fs-5 rounded-pill shadow-sm" aria-pressed="false" aria-label="Alto contraste">' +
                    '<i class="bi bi-circle-half me-1" aria-hidden="true"></i> Alto contraste' +
                '</button>' +
            '</div>';

        const encabezado = document.querySelector('header');
        if (encabezado) {
            encabezado.insertAdjacentElement('afterend', barra);
        } else {
            document.body.insertBefore(barra, document.body.firstChild);
        }
        return barra;
    }

    function actualizarBotonContraste(boton) {
        boton.setAttribute('aria-pressed', contrasteActivo ? 'true' : 'false');
        boton.classList.toggle('btn-warning', contrasteActivo);
        boton.classList.toggle('btn-outline-dark', !contrasteActivo);
    }

    document.addEventListener('DOMContentLoaded', () => {
        const barra = crearBarra();
        const btnDisminuir = barra.querySelector('#btnDisminuirFuente');
        const btnRestablecer = barra.querySelector('#btnRestablecerFuente');
        const btnAumentar = barra.querySelector('#btnAumentarFuente');
        const btnContraste = barra.querySelector('#btnAltoContraste');

        function cambiarTamano(nuevoIndice) {
            indice = Math.max(0, Math.min(tamanos.length - 1, nuevoIndice));
            guardar(CLAVE_TAMANO, tamanos[indice]);
            aplicarTamano();
        }

        btnDisminuir.addEventListener('click', () => cambiarTamano(indice - 1));
        btnAumentar.addEventListener('click', () => cambiarTamano(indice + 1));
        btnRestablecer.addEventListener('click', () => cambiarTamano(INDICE_NORMAL));

        btnContraste.addEventListener('click', () => {
            contrasteActivo = !contrasteActivo;
            guardar(CLAVE_CONTRASTE, contrasteActivo ? 'activo' : 'inactivo');
            aplicarContraste();
            actualizarBotonContraste(btnContraste);
        });

        actualizarBotonContraste(btnContraste);
    });
})();
