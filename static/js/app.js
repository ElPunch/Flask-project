function confirmarEliminar() {
    return confirm("¿Seguro que deseas eliminar este registro?\nEsta acción no se puede deshacer.");
}

document.addEventListener('DOMContentLoaded', function () {
    var formularios = document.querySelectorAll('form');

    formularios.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var camposRequeridos = form.querySelectorAll('[required]');
            var hayError = false;

            camposRequeridos.forEach(function (campo) {
                campo.classList.remove('campo-error');

                if (campo.value.trim() === '') {
                    campo.classList.add('campo-error');
                    hayError = true;
                }
            });

            if (hayError) {
                event.preventDefault();
                mostrarMensaje('⚠ Por favor, completa todos los campos requeridos.');
            }
        });
    });

    document.querySelectorAll('.form-input').forEach(function (campo) {
        campo.addEventListener('input', function () {
            if (campo.value.trim() !== '') {
                campo.classList.remove('campo-error');
            }
        });
    });
});

function mostrarMensaje(texto) {
    var existente = document.getElementById('js-alert');
    if (existente) {
        existente.textContent = texto;
        return;
    }

    var alerta = document.createElement('div');
    alerta.id = 'js-alert';
    alerta.className = 'alert alert--error';
    alerta.setAttribute('role', 'alert');
    alerta.textContent = texto;

    var primerForm = document.querySelector('form');
    if (primerForm) {
        primerForm.insertBefore(alerta, primerForm.firstChild);
    }

    setTimeout(function () {
        if (alerta.parentNode) {
            alerta.parentNode.removeChild(alerta);
        }
    }, 4000);
}