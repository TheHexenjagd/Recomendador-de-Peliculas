from django.http import JsonResponse
from django.shortcuts import render
import requests
from .models import Movie
from datetime import datetime
import pandas as pd
import logging
import json
import random

# Configurar el registro de depuración
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def extract_titles_from_response(raw_text):
    """Extrae títulos de películas del texto crudo de la respuesta del modelo."""
    try:
        # Reemplazar secuencias de escape y normalizar saltos de línea
        cleaned_text = raw_text.replace('\\n', '\n').replace('\\u0026', '&')

        # Extraer el contenido relevante del campo 'response'
        if 'response' in cleaned_text:
            response_content = cleaned_text.split('response":"')[1].split('"done":')[0]
            response_content = response_content.replace('\\n', '\n').replace('\\u0026', '&')
            titles = [title.strip() for title in response_content.strip().split('\n') if title.strip()]
        else:
            titles = [title.strip() for title in cleaned_text.strip().split('\n') if title.strip()]

        processed_titles = [title for title in titles if title]
        logger.info(f'Títulos extraídos: {processed_titles}')
        return processed_titles
    except Exception as e:
        logger.error(f'Error al extraer títulos: {str(e)}')
        return []

def translate_text(text, target_language='es', model_name='llama3'):
    """Traduce el texto al idioma objetivo usando el modelo especificado."""
    try:
        # Llamar a la API de traducción del modelo
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': model_name,
            "stream": False,
            'prompt': f"Traduce el siguiente texto al {target_language}: '{text}'. Sin realizar opiniones ni ofrecer contexto. Traduce de forma directa sin escribir nada mas."
        })
        response.raise_for_status()
        response_json = response.json()
        translated_text = response_json.get('response', text)
        logger.info(f'Texto traducido: {translated_text}')
        return translated_text
    except Exception as e:
        logger.error(f'Error al traducir texto: {str(e)}')
        return text  # Retornar el texto original en caso de error

def search_movies(request):
    query = request.GET.get('query', '')
    language = request.GET.get('language', 'es')
    model_name = request.GET.get('model', 'llama3')
    limit = int(request.GET.get('limit', 0))  # Nuevo parámetro para limitar la búsqueda

    if not query:
        return JsonResponse({'error': 'No se proporcionó una consulta de búsqueda.', 'movies': [], 'recommendations': ''}, status=400)

    try:
        # Paso 1: Usar el modelo seleccionado para obtener una lista de títulos de películas
        llama_response = requests.post('http://localhost:11434/api/generate', json={
            'model': model_name,
            "stream": False,
            'prompt': f"Devuelve una lista de películas con títulos en inglés que corresponda a esta petición: '{query}'. Cada título debe estar en una línea separada, sin ningún otro tipo de texto o separador. Sin fechas ni otros datos."
        })
        llama_response.raise_for_status()
        raw_text = llama_response.text
        logger.info(f'Respuesta cruda del modelo: {raw_text}')

        # Extraer y procesar los títulos
        movie_titles = extract_titles_from_response(raw_text)

        if not movie_titles:
            logger.error('No se encontraron títulos válidos de películas.')
            return JsonResponse({'error': 'No se encontraron títulos válidos de películas.', 'movies': [], 'recommendations': ''}, status=400)

        # Aplicar el límite si se especifica
        if limit > 0:
            movie_titles = movie_titles[:limit]

        # Paso 2: Consultar la API de TMDb para cada título y recolectar los detalles de las películas
        api_key = '99eab6190f078a2ea8ca68681266d074'
        movie_details = []

        for title in movie_titles:
            if not title:
                continue
            url = f'https://api.themoviedb.org/3/search/movie?query={requests.utils.quote(title)}&api_key={api_key}&language=en-US'
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                logger.info(f'Respuesta cruda de TMDb para "{title}": {data}')
                results = data.get('results', [])
                if results:
                    movie = results[0]
                    movie_details.append({
                        'title': movie.get('title', ''),
                        'overview': movie.get('overview', ''),
                        'release_date': movie.get('release_date', ''),
                        'tmdb_id': movie.get('id', '')
                    })
            except requests.RequestException as e:
                logger.error(f'Error en la solicitud a la API de TMDb: {str(e)}')
                continue

        # Paso 3: Guardar temporalmente los resultados en un DataFrame
        df = pd.DataFrame(movie_details)
        logger.info(f'Detalles de películas recopilados: {df}')

        # Imprimir el DataFrame en los logs para depuración
        logger.info("DataFrame de detalles de películas:")
        logger.info(df.to_string())

        # Paso 4: Registrar en la base de datos solo las películas que no existen
        for _, row in df.iterrows():
            title = row['title']
            overview = row['overview']
            release_date = row['release_date']
            tmdb_id = row['tmdb_id']

            if release_date:
                try:
                    release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
                except ValueError:
                    release_date = None
            else:
                release_date = None

            try:
                Movie.objects.update_or_create(
                    tmdb_id=tmdb_id,
                    defaults={
                        'title': title,
                        'overview': overview,
                        'release_date': release_date
                    }
                )
            except Exception as e:
                logger.error(f'Error al guardar la película {title}: {str(e)}')

        # Paso 5: Mostrar los resultados en forma de lista
        if language == 'es':
            df['overview'] = df['overview'].apply(lambda x: translate_text(x, 'es', model_name))
            df['title_translated'] = df['title'].apply(lambda x: translate_text(x, 'es', model_name))
        else:
            df['overview'] = df['overview']
            df['title_translated'] = df['title']

        # Ordenar los resultados por fecha de estreno
        df_sorted = df.sort_values(by='release_date', ascending=True)
        
        movie_explanations = [
            f"Título: {row['title_translated']} {(' (Original: ' + row['title'] + ')') if language == 'es' else ''}\nDescripción: {row['overview']}\nFecha de estreno: {row['release_date']}\n"
            for _, row in df_sorted.iterrows()
        ]

        return JsonResponse({
            'movies': movie_explanations,
            'recommendations': ''
        })

    except Exception as e:
        logger.error(f'Error inesperado: {str(e)}')
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}',
            'movies': [],
            'recommendations': ''
        }, status=500)

def search_random_movie(request):
    language = request.GET.get('language', 'es')
    model_name = request.GET.get('model', 'llama3')

    try:
        # Paso 1: Generar un ID de película aleatorio
        random_movie_id = random.randint(1, 10000)  # Usar un rango amplio de IDs
        api_key = '99eab6190f078a2ea8ca68681266d074'
        url = f'https://api.themoviedb.org/3/movie/{random_movie_id}?api_key={api_key}&language=en-US'
        
        # Consultar la API de TMDb para obtener detalles de la película aleatoria
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f'Respuesta cruda de TMDb para película aleatoria (ID: {random_movie_id}): {data}')

        # Extraer detalles de la película
        movie_details = {
            'title': data.get('title', ''),
            'overview': data.get('overview', ''),
            'release_date': data.get('release_date', ''),
            'tmdb_id': data.get('id', '')
        }

        # Paso 2: Guardar temporalmente el resultado en un DataFrame
        df = pd.DataFrame([movie_details])
        logger.info(f'Detalle de película aleatoria recopilado: {df}')

        # Imprimir el DataFrame en los logs para depuración
        logger.info("DataFrame de detalle de película aleatoria:")
        logger.info(df.to_string())

        # Paso 3: Registrar en la base de datos solo la película si no existe
        title = movie_details['title']
        overview = movie_details['overview']
        release_date = movie_details['release_date']
        tmdb_id = movie_details['tmdb_id']

        if release_date:
            try:
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            except ValueError:
                release_date = None
        else:
            release_date = None

        try:
            Movie.objects.update_or_create(
                tmdb_id=tmdb_id,
                defaults={
                    'title': title,
                    'overview': overview,
                    'release_date': release_date
                }
            )
        except Exception as e:
            logger.error(f'Error al guardar la película {title}: {str(e)}')

        # Paso 4: Mostrar el resultado
        if language == 'es':
            overview_translated = translate_text(movie_details['overview'], 'es', model_name)
            title_translated = translate_text(movie_details['title'], 'es', model_name)
        else:
            overview_translated = movie_details['overview']
            title_translated = movie_details['title']

        movie_explanation = (
            f"Título: {title_translated} {(' (Original: ' + movie_details['title'] + ')') if language == 'es' else ''}\n"
            f"Descripción: {overview_translated}\n"
            f"Fecha de estreno: {movie_details['release_date']}\n"
        )

        return JsonResponse({
            'movies': [movie_explanation],
            'recommendations': ''
        })

    except Exception as e:
        logger.error(f'Error inesperado: {str(e)}')
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}',
            'movies': [],
            'recommendations': ''
        }, status=500)