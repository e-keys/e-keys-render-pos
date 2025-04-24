// Función para copiar texto al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copiado al portapapeles');
    }).catch(function(err) {
        console.error('Error al copiar: ', err);
    });
}

// Función para mostrar un toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function () {
        document.body.removeChild(toast);
    });
}

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

// Función para confirmar eliminación
function confirmDelete(message = '¿Está seguro de que desea eliminar este elemento?') {
    return confirm(message);
}

// Inicialización de tooltips y popovers
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y popovers
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Inicializar gráficas
    initializeCharts();
});

function initializeCharts() {
    // Verificar si estamos en la página del dashboard
    if (!document.getElementById('historicoChart')) {
        return;
    }

    // Gráfica de histórico de ventas
    const historicoCtx = document.getElementById('historicoChart');
    if (historicoCtx) {
        console.log('Inicializando gráfica de histórico');
        console.log('Meses:', window.meses);
        console.log('Ingresos:', window.ingresos_mensuales);
        console.log('Ganancias:', window.ganancias_mensuales);
        
        new Chart(historicoCtx, {
            type: 'line',
            data: {
                labels: window.meses || [],
                datasets: [{
                    label: 'Ingresos',
                    data: window.ingresos_mensuales || [],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    fill: true
                }, {
                    label: 'Ganancias',
                    data: window.ganancias_mensuales || [],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    // Gráfica de productos más vendidos
    const productosVendidosCtx = document.getElementById('productosVendidosChart');
    if (productosVendidosCtx) {
        console.log('Inicializando gráfica de productos más vendidos');
        console.log('Labels:', window.productos_labels);
        console.log('Data:', window.productos_data);
        
        new Chart(productosVendidosCtx, {
            type: 'doughnut',
            data: {
                labels: window.productos_labels || [],
                datasets: [{
                    data: window.productos_data || [],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Gráfica de canales de venta
    const canalesVentaCtx = document.getElementById('canalesVentaChart');
    if (canalesVentaCtx) {
        console.log('Inicializando gráfica de canales de venta');
        console.log('Labels:', window.canales_labels);
        console.log('Data:', window.canales_data);
        
        new Chart(canalesVentaCtx, {
            type: 'pie',
            data: {
                labels: window.canales_labels || [],
                datasets: [{
                    data: window.canales_data || [],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Gráfica de productos disponibles
    const productosDisponiblesCtx = document.getElementById('productosDisponiblesChart');
    if (productosDisponiblesCtx) {
        console.log('Inicializando gráfica de productos disponibles');
        console.log('Labels:', window.productos_disp_labels);
        console.log('Data:', window.productos_disp_data);
        
        new Chart(productosDisponiblesCtx, {
            type: 'bar',
            data: {
                labels: window.productos_disp_labels || [],
                datasets: [{
                    label: 'Stock Disponible',
                    data: window.productos_disp_data || [],
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
} 