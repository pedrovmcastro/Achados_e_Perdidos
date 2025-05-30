document.addEventListener("DOMContentLoaded", () => {
    
    const tabela = document.querySelector("#tabela-objetos");
    const headers = tabela.querySelectorAll("thead th");
    const tbody = tabela.querySelector("tbody");

    let currentColumn = null;
    let isAscending = true;

    // Adiciona classe sortable e event listeners aos cabeçalhos
    headers.forEach((header, index) => {
        header.classList.add('sortable');
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => handleHeaderClick(index));
    });


    function handleHeaderClick(columnIndex) {
        // Verifica se é a mesma coluna para alternar direção
        if (currentColumn === columnIndex) {
            isAscending = !isAscending;
        } else {
            currentColumn = columnIndex;
            isAscending = true;
        }

        // Ordena a tabela
        sortTable(columnIndex, isAscending);

        // Atualiza indicadores visuais
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

        // Remove as linhas atuais e adiciona as ordenadas
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
        // sensitivity: 'base' -> Ignora case e acentos. É importante colocar o 'pt-BR' pra reconhecer as strings com acentos
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

    // Evento de clique: limpar formulário
    document.querySelector("#btnLimpar").addEventListener('click', () => {
        window.location.reload();
    });

    // Evento de pressionar o Enter = botão de pesquisa
    document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            pesquisar(objetosJSON, categoriasJSON);
        }
    });

});

 // Funcão relativa ao formulário de pesquisa
function pesquisar(objetos, categorias) {
    const dataField = document.querySelector('#busca_data_encontrado').value;
    const categoriaField = document.querySelector('#busca_categoria').value;
    const identificacaoField = document.querySelector('#busca_identificacao').value;
    const localField = document.querySelector('#busca_local_encontrado').value;

    console.log('Data:', dataField, '\nCategoria:', categoriaField, '\nIdentificação:', identificacaoField, '\nLocal:', localField);
    console.log('Categorias:', categorias);

    console.log(objetos);

    const matches = [];

    objetos.forEach(objeto => {
        console.log(objeto);

        // Reaproveitamento de código: função pesquisar é usada tanto em objeto.html quanto index.html
        const matchCategoria = categoriaField !== '' &&
        (
            typeof objeto.categoria === 'object'
            ? objeto.categoria.nome === categoriaField
            : objeto.categoria === categoriaField
        );

        const matchIdentificacao = identificacaoField !== '' && objeto['identificacao'] === identificacaoField;
        const matchData = dataField !== '' && objeto['data_encontrado'] === dataField;
        const matchLocal = localField !== '' && objeto['local_encontrado'] === localField;

        // Se algum campo preenchido bate, adiciona ao resultado
        if (matchCategoria || matchIdentificacao || matchData || matchLocal) {
            matches.push(objeto);
        }

    });

    const tbody = document.querySelector("tbody");
    tbody.innerHTML = "";

    console.log(matches);
    matches.forEach(match => {
        const row = document.createElement('tr');

        ['data_encontrado', 'categoria', 'identificacao', 'local_encontrado'].forEach(key => {
            const td = document.createElement('td');

            if (key === 'data_encontrado') {
                const [ano, mes, dia] = match[key].split('-');
                td.textContent = `${dia}/${mes}/${ano}`;
            } else {
                td.textContent = match[key];
            }
            row.appendChild(td);
        });

        tbody.appendChild(row);

    });

}


