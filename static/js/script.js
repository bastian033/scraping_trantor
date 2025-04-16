document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const razonSocial = document.getElementById('razon_social').value;

    // Llamar al backend para buscar la empresa
    const response = await fetch(`/buscar?razon_social=${encodeURIComponent(razonSocial)}`);
    const data = await response.json();

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (data.error) {
        resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
    } else if (data.message) {
        resultsDiv.innerHTML = `<p>${data.message}</p>`;
    } else {
        // Crear una tabla para mostrar los resultados
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        // Encabezados de la tabla
        thead.innerHTML = `
            <tr>
                <th>RUT</th>
                <th>Razón Social</th>
                <th>Fecha de Actuación</th>
                <th>Fecha de Registro</th>
                <th>Fecha de Aprobación</th>
                <th>Comuna Tributaria</th>
                <th>Región Tributaria</th>
                <th>Capital</th>
            </tr>
        `;

        // Filas de la tabla
        data.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${result['RUT']}</td>
                <td>${result['Razon Social']}</td>
                <td>${result['Fecha de actuacion (1era firma)']}</td>
                <td>${result['Fecha de registro (ultima firma)']}</td>
                <td>${result['Fecha de aprobacion x SII']}</td>
                <td>${result['Comuna Tributaria']}</td>
                <td>${result['Region Tributaria']}</td>
                <td>${result['Capital']}</td>
            `;
            tbody.appendChild(row);
        });

        table.appendChild(thead);
        table.appendChild(tbody);
        resultsDiv.appendChild(table);
    }
});