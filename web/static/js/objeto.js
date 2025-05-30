document.addEventListener('DOMContentLoaded', () => {
      const selectCategoria = document.querySelector('#categoria');
      const camposContainer = document.querySelector('#camposContainer');

      selectCategoria.addEventListener('change', function () {
        const categoriaId = this.value;
        camposContainer.innerHTML = '';

        if (!categoriaId) {
          camposContainer.style.display = 'none';
        return;
        }

        const categoria = categoriasData.find(cat => cat._id === categoriaId);

        if (!categoria || !categoria.campos) {
          camposContainer.style.display = 'none';
          return;
        }

        categoria.campos.forEach(campo => {
          const div = document.createElement('div');
          div.className = "mb-3";

          const label = document.createElement('label');
          label.className = 'form-label';
          label.innerText = campo;
          label.setAttribute('for', campo);

          const input = document.createElement('input');
          input.type = 'text';
          input.className = 'form-control';
          input.name = `campos_valores[${campo}]`;
          input.id = campo;

          div.appendChild(label);
          div.appendChild(input);
          camposContainer.appendChild(div);
        });

        camposContainer.style.display = 'block';
      });
    });