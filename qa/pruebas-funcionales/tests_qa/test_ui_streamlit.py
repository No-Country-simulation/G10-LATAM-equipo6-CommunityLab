import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as T

@pytest.fixture(scope="module")
def driver_navegador():
    """
    Fixture de Pytest para configurar y levantar el navegador Chrome 
    de forma automatizada para las pruebas de UI.
    """
    options = Options()
    # Descomenta la siguiente línea si quieres que corra oculto (Headless) en pipelines de CI/CD:
    # options.add_argument("--headless=new")
    
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    # Inicializamos el driver usando WebDriver Manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    yield driver
    
    driver.quit()

def test_streamlit_panel_carga_correctamente(driver_navegador):
    """
    Prueba UI de Humo (Smoke Test): Verifica que la interfaz de Streamlit 
    en el puerto 8501 responda y cargue el título principal del proyecto CommunityLab.
    """
    # 1. Navegar a la aplicación local de Streamlit
    url_streamlit = "http://localhost:8501"
    driver_navegador.get(url_streamlit)

    # 2. Espera inteligente (Explicit Wait): Esperamos a que Streamlit renderice el DOM (máx. 10 segundos)
    wait = WebDriverWait(driver_navegador, 10)
    
    try:
        #elementos visuales esenciales
        elemento_titulo = wait.until(
            T.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # 3. Validaciones de QA (Assertions)
        assert elemento_titulo is not None, "El panel de Streamlit no renderizó el título principal (h1)."
        print(f"\n[QA UI Success] Panel detectado con éxito. Título encontrado: {elemento_titulo.text}")

    except Exception as e:
        pytest.fail(f"La interfaz de Streamlit no cargó correctamente o el servidor no está activo en {url_streamlit}. Error: {str(e)}")

def test_elementos_interactivos_ui(driver_navegador):
    """
    Prueba UI de Integración: Verifica la presencia de botones de control 
    o selectores de motor en el panel de curaduría.
    """
    driver_navegador.get("http://localhost:8501")
    time.sleep(2) # Breve pausa para estabilización de componentes dinámicos de Streamlit

    # botones generados por st.button o st.selectbox
    botones = driver_navegador.find_elements(By.TAG_NAME, "button")
    
    # Validamos que la interfaz contenga elementos interactivos para el usuario
    assert len(botones) > 0, "No se encontraron botones interactivos en la interfaz de usuario."