# Proyecto LangChain Agentic RRHH & IT

Este proyecto contiene herramientas y utilidades para gestión de RRHH/IT utilizando LangChain y Google Generative AI.

## Requisitos

- Python 3.8 o superior
- pip

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. (Opcional) Crea y activa un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno en un archivo `.env`. Debes agregar tu API token de Gemini (Google Generative AI) en la variable correspondiente, por ejemplo:
   ```
   GEMINI_API_KEY=tu_api_token_aqui
   ```

## Ejecución

Para iniciar el proyecto, ejecuta:

```bash
python3 -m agentic.index
```

## Estructura del proyecto

- `agentic/index.py`: Script principal del proyecto.
- `agentic/tools.py`: Herramientas y utilidades personalizadas.
- `agentic/memoria/`: Archivos de memoria y datos.
- `.env`: Variables de entorno (no incluido por seguridad).

## Notas

- Asegúrate de tener configurado el API token de Gemini (Google Generative AI) en tu archivo `.env` bajo la variable `GEMINI_API_KEY`.
- Si agregas nuevas dependencias, recuerda actualizar `requirements.txt`.

---
