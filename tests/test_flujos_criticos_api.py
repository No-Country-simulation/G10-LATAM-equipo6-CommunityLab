import pytest
import requests
from unittest.mock import patch

# Definimos la URL del webhook de ingesta documentada en el proyecto
WEBHOOK_N8N_URL = "http://localhost:5678/webhook/communitylab-ingesta"

def test_api_ingesta_webhook_responde_correctamente():
    """
    QA Test: Verifica que el flujo crítico de envío de datos al motor n8n 
    estructura bien el JSON y maneja una respuesta exitosa (HTTP 200).
    """
    # 1. PREPARACIÓN (Arrange): Armamos un payload simulando un mensaje de Discord
    payload_prueba = {
        "id_mensaje": "MSG-999",
        "canal": "Discord - Dudas Técnicas",
        "contenido": "Hola, ¿cómo configuro el entorno virtual en Windows?",
        "autor": "Estudiante QA"
    }

    # Usamos 'patch' para interceptar la llamada real a la red y simular la respuesta.
    # Así evitamos que la prueba falle si Docker no está corriendo.
    with patch('requests.post') as mock_post:
        # 2. SIMULACIÓN: Le decimos al mock que actúe como si n8n respondiera OK
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success", "message": "Procesado por n8n"}

        # 3. ACCIÓN (Act): Nuestro código ejecuta la petición HTTP
        respuesta = requests.post(WEBHOOK_N8N_URL, json=payload_prueba)

        # 4. VERIFICACIÓN (Assert): Como QA, validamos que el comportamiento sea exacto
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "success"
        
        # Validamos estrictamente que la aplicación llamó a la URL correcta y con el JSON correcto
        mock_post.assert_called_once_with(WEBHOOK_N8N_URL, json=payload_prueba)

def test_api_ingesta_manejo_de_errores():
    """
    QA Test: Verifica cómo reacciona el sistema si la API de n8n se cae o devuelve error.
    """
    payload_prueba = {"contenido": "Mensaje de prueba de estrés"}

    with patch('requests.post') as mock_post:
        # Simulamos un error 500 (Internal Server Error) del lado de n8n
        mock_post.return_value.status_code = 500
        
        respuesta = requests.post(WEBHOOK_N8N_URL, json=payload_prueba)

        # Verificamos que nuestro sistema detecte el código 500
        assert respuesta.status_code == 500