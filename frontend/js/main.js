document.addEventListener('DOMContentLoaded', () => {
    
    // Función reutilizable para mostrar/ocultar contraseñas
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

    // Activar en login
    setupPasswordToggle('btnTogglePassword', 'password', 'iconoOjo');

    // Activar en registro
    setupPasswordToggle('btnToggleRegPassword', 'regPassword', 'iconoRegOjo');

});