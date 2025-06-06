document.addEventListener("DOMContentLoaded", () => {
    const tabela = document.querySelector("#tabela-objetos");
    const headers = tabela.querySelectorAll("thead th");
    const tbody = tabela.querySelector("tbody");

    let currentColumn = null;
    let isAscending = true;

    headers.forEach((header, index) => {
        header.classList.add('sortable');
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => handleHeaderClick(index));
    });


    function handleHeaderClick(columnIndex) {
        if (currentColumn === columnIndex) {
            isAscending = !isAscending;
        } else {
            currentColumn = columnIndex;
            isAscending = true;
        }

        sortTable(columnIndex, isAscending);
        updateHeaderIndicators(columnIndex, isAscending);
    }


    function sortTable(columnIndex, ascending) {
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isDateColumn = headers[columnIndex].textContent === 'Data Encontrado';

        rows.sort((a, b) => {
            const aVal = a.children[columnIndex].textContent.trim();
            const bVal = b.children[columnIndex].textContent.trim();

            if (isDateColumn) {
                return compareDates(aVal, bVal, ascending);
            }
            return compareStrings(aVal, bVal, ascending);
        });

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }


    function compareDates(a, b, ascending) {
        const dateA = parseDate(a);
        const dateB = parseDate(b);
        return ascending ? dateA - dateB : dateB - dateA;
    }


    function parseDate(dateString) {
        const [day, month, year] = dateString.split('/');
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }

    
    function compareStrings(a, b, ascending) {
        const comparison = a.localeCompare(b, 'pt-BR', { sensitivity: 'base' });  
        return ascending ? comparison : -comparison;
    }


    function updateHeaderIndicators(activeColumn, ascending) {
        headers.forEach((header, index) => {
            // Remove todas as classes de ordenação
            header.classList.remove('asc', 'desc');

            if (index === activeColumn) {
                header.classList.add(ascending ? 'asc' : 'desc');
            }
        });
    }

    document.querySelector("#btnLimpar").addEventListener('click', () => {
        window.location.reload();
    });

    document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            pesquisar(objetosJSON, categoriasJSON);
        }
    });

});


