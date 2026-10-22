import pytest
import os
import sys

def ejecutar_pruebas_qa():
    """
    Orquestador avanzado de QA para el proyecto G10-LATAM-equipo6-CommunityLab.
    Ejecuta la suite completa de pruebas unitarias e integrales, generando 
    reportes automáticos visuales (HTML) y técnicos (XML) para la integración continua.
    """
    print("🚀 Iniciando suite de pruebas de QA & Integración para G10-LATAM-equipo6-CommunityLab...")
    print(f"📂 Directorio de trabajo actual: {os.getcwd()}")
    
    # Validar si existe la carpeta tests antes de ejecutar
    if not os.path.exists("tests"):
        print("❌ Error crítico: No se encuentra la carpeta 'tests/'. Asegúrate de ejecutar este script desde la raíz del repositorio.")
        sys.exit(1)

    # Argumentos optimizados para Pytest integrando plugins de reportes profesionales
    argumentos = [
        "tests/",                  # Directorio de pruebas detectado en la arquitectura
        "-v",                      # Modo detallado (Verbose)
        "--html=reporte_qa.html",    # Generación de reporte visual navegable
        "--self-contained-html",   # Auto-contenido para facilitar compartirlo con el equipo
        "--junitxml=reporte_qa.xml"  # Reporte estructurado compatible con pipelines CI/CD
    ]

    print("⚙️ Ejecutando pruebas modulares (AI Engine, OCI Storage, Ingestion, Pipeline y UI Services)...")
    exit_code = pytest.main(argumentos)

    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ ¡Todas las pruebas de integración pasaron exitosamente (100% Verdes)! El sistema es funcional.")
    elif exit_code == 5:
        print("⚠️ Advertencia: No se recolectaron pruebas para ejecutar en la ruta especificada.")
    else:
        print(f"❌ La suite de pruebas finalizó con fallos o errores (Código de salida: {exit_code}).")
        print("💡 Sugerencia: Revisa los logs en la carpeta 'logs/' o el reporte HTML para aislar el fallo.")

    print("📊 Reportes de auditoría generados en la raíz del proyecto:")
    print("   🔗 HTML visual interactivo : 'reporte_qa.html'")
    print("   🔗 XML técnico estructurado : 'reporte_qa.xml'")
    print("="*60)

if __name__ == "__main__":
    ejecutar_pruebas_qa()