
# Recomendador de Películas

Este proyecto es una aplicación web creada con Python y Django que utiliza la API de Ollama y The Movie Database (TMDb) para ofrecer recomendaciones de películas. La aplicación permite a los usuarios buscar películas y obtener detalles sobre ellas, así como recibir recomendaciones aleatorias.

## Tecnologías Utilizadas

- **Django:** Framework web para el backend.
- **Python:** Lenguaje de programación utilizado para el desarrollo del backend.
- **Ollama API:** Proporciona acceso a los modelos Llama3, Gemma2 y Mistral para la generación de contenido y traducción.
- **The Movie Database (TMDb) API:** Fuente de datos para obtener información detallada de películas.
- **Bootstrap:** Framework de CSS utilizado para el diseño responsivo de la interfaz.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- Django 3.0 o superior
- MySQL o MariaDB
- Aplicación [Ollama](https://ollama.com/)
- Clave API de [TMDb](https://developer.themoviedb.org/)

## Instalación

1. **Clonar el Repositorio**

   ```bash
   git clone https://github.com/TheHexenjagd/Recomendador-de-Peliculas.git
   cd recomendador-de-peliculas
   ```

2. **Crear y Activar un Entorno Virtual**

   ```bash
   python3 -m venv env
   source env/bin/activate  # En Windows usa `env\Scripts\activate`
   ```

3. **Instalar las Dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la Base de Datos**

   Edita el archivo `settings.py` para configurar la conexión a tu base de datos MySQL o MariaDB:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'app_peliculas',
           'USER': 'user',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

5. **Migrar la Base de Datos**

   ```bash
   python manage.py migrate
   ```

6. **Iniciar el Servidor de Desarrollo**

   ```bash
   python manage.py runserver
   ```

## Uso

Accede a la aplicación en tu navegador web en `http://localhost:8000`.

### Funcionalidades

- **Buscar Películas:** Ingresa una consulta en la caja de búsqueda y selecciona el modelo de lenguaje a utilizar (Llama3, Gemma2 o Mistral).
- **Buscar Película Aleatoria:** Haz clic en el botón para obtener detalles de una película aleatoria.
- **Seleccionar Idioma:** Elige el idioma en que deseas ver los resultados (Español o Inglés).

## Estructura del Proyecto

- **index.html:** Plantilla principal para la interfaz de usuario.
- **views.py:** Vistas de Django que manejan las solicitudes y respuestas.
- **styles.css:** Archivo de estilos para la interfaz de usuario.
- **scripts.js:** Archivo JavaScript para manejar la lógica del frontend.
- **settings.py:** Configuración del proyecto Django.

## Configuración de las Claves de API

Asegúrate de tener configuradas las claves de API necesarias en tu entorno o directamente en el código.

- **Ollama API:** La URL base debe estar configurada en el código.
- **TMDb API:** La clave de API debe estar configurada en `views.py`.

## Ejemplo de Configuración de Claves

```python
# views.py

api_key = 'TU_CLAVE_API_TMDB'
ollama_url = 'http://localhost:11434/api/generate'
```

## Contribuir

Si deseas contribuir a este proyecto, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios necesarios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube los cambios a tu repositorio (`git push origin feature/nueva-funcionalidad`).
5. Crea un Pull Request.

# Ramas

- La rama old_versions incluye versiones beta de prueba del desarollo y su avance.
- La rama limite_peliculas incluye funcionalidad para limitar la cantidad de películas mostradas por búsqueda (Es un poco inestable).

## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).
