document.getElementById('query').addEventListener('input', function() {
    const query = document.getElementById('query').value;
    document.getElementById('searchButton').disabled = !query.trim();
});

function buscarPeliculas() {
    const query = document.getElementById('query').value;
    const language = document.getElementById('languageSelect').value;
    const model = document.getElementById('modelSelect').value;
    const limit = document.getElementById('limitInput').value;
    const resultadosDiv = document.getElementById('resultados');

    resultadosDiv.innerHTML = 'Buscando...';

    fetch(`/search/?query=${encodeURIComponent(query)}&language=${encodeURIComponent(language)}&model=${encodeURIComponent(model)}&limit=${encodeURIComponent(limit)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                resultadosDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            } else {
                const movies = data.movies;
                const recommendations = data.recommendations;

                let output = '<h2>Película(s) encontradas:</h2>';
                if (movies && movies.length > 0) {
                    movies.forEach(movie => {
                        output += `<p>${movie.replace(/\n/g, '<br>')}</p>`;
                    });
                } else {
                    output += '<p>No se encontraron películas.</p>';
                }

                if (recommendations) {
                    output += '<h2>Recomendaciones del modelo:</h2>';
                    output += `<p>${recommendations.replace(/\n/g, '<br>')}</p>`;
                }

                resultadosDiv.innerHTML = output;
            }
        })
        .catch(error => {
            resultadosDiv.innerHTML = `<p>Error al comunicarse con el servidor: ${error.message}</p>`;
        });
}

function buscarPeliculasAleatorias() {
    const language = document.getElementById('languageSelect').value;
    const model = document.getElementById('modelSelect').value;
    const resultadosDiv = document.getElementById('resultados');

    resultadosDiv.innerHTML = 'Buscando película aleatoria...';

    fetch(`/search/random/?language=${encodeURIComponent(language)}&model=${encodeURIComponent(model)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                resultadosDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            } else {
                const movies = data.movies;
                const recommendations = data.recommendations;

                let output = '<h2>Películas encontradas:</h2>';
                if (movies && movies.length > 0) {
                    movies.forEach(movie => {
                        output += `<p>${movie.replace(/\n/g, '<br>')}</p>`;
                    });
                } else {
                    output += '<p>No se encontraron películas.</p>';
                }

                if (recommendations) {
                    output += '<h2>Recomendaciones del modelo:</h2>';
                    output += `<p>${recommendations.replace(/\n/g, '<br>')}</p>`;
                }
                resultadosDiv.innerHTML = output;
            }
        })
        .catch(error => {
            resultadosDiv.innerHTML = `<p>Error al comunicarse con el servidor: ${error.message}</p>`;
        });
}
