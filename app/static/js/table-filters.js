/**
 * Implementa filtros en todas las columnas de las tablas
 * Este script debe ser incluido en las páginas que contienen tablas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar ordenamiento a todas las tablas con clase sortable-table
    document.querySelectorAll('.sortable-table').forEach(table => {
        const headers = table.querySelectorAll('th:not(.no-sort)');
        
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const tableBody = table.querySelector('tbody');
                const rows = Array.from(tableBody.querySelectorAll('tr'));
                const index = Array.from(header.parentElement.children).indexOf(header);
                const dataType = header.getAttribute('data-type') || 'string';
                
                // Obtener el orden actual
                const currentOrder = header.getAttribute('data-order') || 'asc';
                const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                
                // Limpiar indicadores de orden en otros encabezados
                headers.forEach(h => h.removeAttribute('data-order'));
                header.setAttribute('data-order', newOrder);
                
                // Ordenar las filas
                rows.sort((a, b) => {
                    const aValue = a.children[index].textContent.trim();
                    const bValue = b.children[index].textContent.trim();
                    
                    let comparison = 0;
                    
                    switch(dataType) {
                        case 'number':
                            comparison = parseFloat(aValue) - parseFloat(bValue);
                            break;
                        case 'date':
                            const aDate = new Date(aValue);
                            const bDate = new Date(bValue);
                            comparison = aDate - bDate;
                            break;
                        default:
                            comparison = aValue.localeCompare(bValue);
                    }
                    
                    return newOrder === 'asc' ? comparison : -comparison;
                });
                
                // Reordenar las filas en la tabla
                rows.forEach(row => tableBody.appendChild(row));
            });
        });
    });
}); 