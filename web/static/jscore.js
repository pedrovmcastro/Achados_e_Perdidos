$(() => {
    update_curso()

    $('select[name="fatec"]').on('change', update_curso());
})

function update_curso() {
    let fatec = $('select[name="fatec"]').find("option:selected").val();

    if (fatec) {
        $.getJSON('/_cursos', {fatec: fatec}, (cursos) => {
            let html = "";

            $.each(cursos, (i, curso) => {
                html += `<option value="${curso.id}">${curso.nome}</option>`;
            });

            $('select[name="curso"]').html(html)
        });
    };
}
