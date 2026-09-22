# -*- coding: utf-8 -*-
"""
CommunityLab - Script Integral de Diagnóstico OCI (Red, Puertos y Object Storage)
================================================================================
Este script ejecuta de manera automatizada las pruebas de:
  1. Conectividad y escaneo de puertos de la Máquina Virtual (147.15.9.116).
  2. Diagnóstico de configuración de credenciales OCI (.env).
  3. Verificación y validación de disponibilidad del Bucket en OCI Object Storage.

Uso:
  python diagnostico_oci_completo.py
"""

import os
import sys
import socket

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Cargar variables desde .env (búsqueda en directorio actual y directorios superiores)
def cargar_variables_env():
    posibles_env = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(r"d:\DevNoCountry\WORKSPACE-G10\G10-LATAM-equipo6-CommunityLab\.env"),
    ]
    
    env_dict = {}
    for ruta in posibles_env:
        if ruta.exists():
            try:
                from dotenv import dotenv_values
                env_dict = dotenv_values(ruta)
                if env_dict:
                    return env_dict, ruta
            except ImportError:
                # Lectura manual si no está instalado python-dotenv
                with open(ruta, "r", encoding="utf-8") as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and not linea.startswith("#") and "=" in linea:
                            k, v = linea.split("=", 1)
                            env_dict[k.strip()] = v.strip().strip('"').strip("'")
                return env_dict, ruta
    return {}, None

ENV_VARS, ENV_PATH_LOADED = cargar_variables_env()

def get_config(key, default=None):
    return ENV_VARS.get(key) or os.getenv(key, default)

VM_HOST = "147.15.9.116"
PORTS_TO_CHECK = {
    22: "SSH (Acceso Remoto / Terminal MobaXterm)",
    5678: "n8n (Orquestador Visual Webhook)",
    8501: "Streamlit UI (Panel de Curaduría Oficial)",
    8500: "Streamlit (Puerto Alternativo OCI)",
    80: "HTTP (Web estándar)",
    443: "HTTPS (Web segura / SSL)"
}

def imprimir_titulo(titulo):
    ancho = 75
    print("\n" + "=" * ancho)
    print(f"  {titulo.upper()}")
    print("=" * ancho)

# -----------------------------------------------------------------------------
# 1. DIAGNÓSTICO DE CONECTIVIDAD DE PUERTOS
# -----------------------------------------------------------------------------
def diagnostico_conectividad_puertos():
    imprimir_titulo("1. Diagnóstico de Conectividad y Escaneo de Puertos")
    print(f"Host Destino: {VM_HOST}")
    print(f"Timeout por puerto: 2.0 segundos\n")
    
    resultados = {}
    for puerto, descripcion in PORTS_TO_CHECK.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        codigo = sock.connect_ex((VM_HOST, puerto))
        sock.close()
        
        abierto = (codigo == 0)
        resultados[puerto] = abierto
        estado = "[ABIERTO / ALCANZABLE]" if abierto else "[BLOQUEADO / FILTRADO]"
        color = "[92m" if abierto else "[91m"
        reset = "[0m"
        
        print(f"  Puerto {puerto:<5} ({descripcion:<45}) -> {color}{estado}{reset}")
        
    print("\n>> Conclusión del Análisis de Red:")
    if resultados.get(22):
        print("   [OK] El puerto 22 (SSH) está ABIERTO: La VM está activa y disponible para conexión.")
    else:
        print("   [X] El puerto 22 (SSH) está INACCESIBLE. Revisa si la instancia está encendida en OCI.")
        
    if resultados.get(5678):
        print("   [OK] El puerto 5678 (n8n) está ABIERTO: El webhook y dashboard pueden recibir peticiones.")
        
    if not resultados.get(8501) and not resultados.get(8500):
        print("   [!] Los puertos 8501 y 8500 están CERRADOS en el firewall exterior (VCN Security List).")
        print("       -> Solución recomendada: Usar el 'Túnel SSH' en MobaXterm (redirección localhost:8501).")
    elif resultados.get(8501):
        print("   [OK] El puerto 8501 está ABIERTO públicamente: Puedes acceder vía http://147.15.9.116:8501")

# -----------------------------------------------------------------------------
# 2. DIAGNÓSTICO DE CONFIGURACIÓN DEL BUCKET EN .ENV
# -----------------------------------------------------------------------------
def diagnostico_configuracion_bucket():
    imprimir_titulo("2. Diagnóstico de Configuración OCI Object Storage (.env)")
    if ENV_PATH_LOADED:
        print(f"Archivo .env cargado desde: {ENV_PATH_LOADED}\n")
    else:
        print("[!] Aviso: No se encontró archivo .env local, leyendo variables de entorno del sistema.\n")

    user_ocid = get_config("OCI_USER_OCID")
    tenancy_ocid = get_config("OCI_TENANCY_OCID")
    fingerprint = get_config("OCI_FINGERPRINT")
    key_file = get_config("OCI_KEY_FILE", "~/.oci/oci_api_key.pem")
    region = get_config("OCI_REGION", "us-ashburn-1")
    namespace = get_config("OCI_NAMESPACE")
    bucket_name = get_config("OCI_BUCKET_NAME")

    print(f"  - OCI_TENANCY_OCID: {tenancy_ocid[:30]}... ({len(tenancy_ocid)} chars)" if tenancy_ocid else "  - OCI_TENANCY_OCID: [FALTA]")
    print(f"  - OCI_USER_OCID:    {user_ocid[:30]}... ({len(user_ocid)} chars)" if user_ocid else "  - OCI_USER_OCID:    [FALTA]")
    print(f"  - OCI_FINGERPRINT:  {fingerprint if fingerprint else '[FALTA]'}")
    print(f"  - OCI_REGION:       {region}")
    print(f"  - OCI_NAMESPACE:    {namespace if namespace else '[FALTA]'}")
    print(f"  - OCI_BUCKET_NAME:  {bucket_name if bucket_name else '[FALTA]'}")
    print(f"  - OCI_KEY_FILE:     {key_file}")

    return {
        "user": user_ocid,
        "tenancy": tenancy_ocid,
        "fingerprint": fingerprint,
        "key_file": key_file,
        "region": region,
        "namespace": namespace,
        "bucket_name": bucket_name
    }

# -----------------------------------------------------------------------------
# 3. VERIFICAR Y VALIDAR DISPONIBILIDAD DEL BUCKET
# -----------------------------------------------------------------------------
def verificar_disponibilidad_bucket(cfg):
    imprimir_titulo("3. Validación de Disponibilidad del Bucket en OCI")
    
    key_str = cfg["key_file"]
    key_path = Path(key_str).expanduser()
    
    # Búsqueda de alternativas si la ruta indicada no existe
    posibles_rutas_key = [
        key_path,
        Path(r"D:\DevNoCountry\OCI-SERVER") / Path(key_str).name,
        Path.home() / ".oci" / "oci_api_key.pem",
        Path.home() / ".oci" / Path(key_str).name,
        Path(r"D:\DevNoCountry\OCI-SERVER\key-hackathon-g10.key")
    ]
    
    clave_encontrada = None
    for p in posibles_rutas_key:
        if p.exists():
            clave_encontrada = p
            break
            
    if not clave_encontrada:
        print(f"  [AVISO] No se encontró el archivo de clave API en: {key_path}")
        print("\n  >> Explicación Técnica:")
        print("     1. La clave 'key-hackathon-g10.key' que te dio el PM es la clave SSH (para entrar por MobaXterm).")
        print("     2. La clave 'oci_api_key.pem' (con fingerprint 34:2f:6f:...) es la clave de API de Oracle Cloud,")
        print("        y está almacenada adentro de la máquina virtual en '/home/ubuntu/.oci/oci_api_key.pem'.")
        print("\n  >> Opciones para validar el Bucket:")
        print("     A) Ejecutar este script adentro de la VM por MobaXterm:")
        print("        python3 diagnostico_oci_completo.py")
        print("     B) Descargar '/home/ubuntu/.oci/oci_api_key.pem' a tu PC mediante el panel SFTP de MobaXterm")
        print("        y guardarlo en: C:\\Users\\Max\\.oci\\oci_api_key.pem")
        return

    print(f"  [OK] Clave privada localizada: {clave_encontrada}")
    
    try:
        import oci
    except ImportError:
        print("  [ERROR] El paquete 'oci' no está instalado en este entorno de Python.")
        print("  -> Ejecuta: pip install oci")
        return

    try:
        oci_config = {
            "user": cfg["user"],
            "fingerprint": cfg["fingerprint"],
            "tenancy": cfg["tenancy"],
            "region": cfg["region"],
            "key_file": str(clave_encontrada)
        }
        
        print("\n  -> Validando estructura del diccionario de configuración OCI...")
        oci.config.validate_config(oci_config)
        print("     [OK] Parámetros validados correctamente.")

        print("  -> Conectando con ObjectStorageClient...")
        client = oci.object_storage.ObjectStorageClient(oci_config)
        
        print("  -> Verificando autenticación y namespace en Oracle Cloud...")
        ns_remoto = client.get_namespace().data
        print(f"     [OK] Autenticación Exitosa. Namespace de la cuenta: '{ns_remoto}'")
        
        ns_usar = cfg["namespace"] or ns_remoto
        bucket_name = cfg["bucket_name"]
        
        print(f"\n  -> Consultando estado del Bucket '{bucket_name}'...")
        bucket_data = client.get_bucket(namespace_name=ns_usar, bucket_name=bucket_name).data
        
        print(f"\n  =======================================================")
        print(f"  ¡EL BUCKET ESTÁ DISPONIBLE Y OPERATIVO EN OCI!")
        print(f"  =======================================================")
        print(f"  * Nombre del Bucket:      {bucket_data.name}")
        print(f"  * Compartment OCID:       {bucket_data.compartment_id[:30]}...")
        print(f"  * Fecha de Creación:      {bucket_data.time_created}")
        print(f"  * Tipo de Almacenamiento: {bucket_data.storage_tier}")
        print(f"  * Tipo de Acceso Público: {bucket_data.public_access_type}")
        print(f"  * ETag:                   {bucket_data.etag}")
        
        print(f"\n  -> Explorando objetos almacenados en el bucket...")
        lista_obj = client.list_objects(namespace_name=ns_usar, bucket_name=bucket_name, limit=15).data.objects
        print(f"     Total de objetos encontrados (muestra hasta 15): {len(lista_obj)}")
        if lista_obj:
            for idx, obj in enumerate(lista_obj, 1):
                print(f"     [{idx}] {obj.name} (Tamaño: {obj.size:,} bytes | Modificado: {obj.time_modified})")
        else:
            print("     (El bucket está actualmente vacío, listo para recibir nuevos paquetes)")
            
    except oci.exceptions.ServiceError as se:
        print(f"\n  [ERROR OCI] Respuesta del servicio de Oracle Cloud:")
        print(f"     Status: {se.status}")
        print(f"     Code:   {se.code}")
        print(f"     Mensaje: {se.message}")
        if se.status == 404:
            print("     -> El bucket no fue encontrado con ese nombre o namespace.")
        elif se.status == 401:
            print("     -> Error de autenticación: la clave privada no coincide con la huella digital (fingerprint).")
    except Exception as ex:
        print(f"\n  [ERROR INESPERADO] {type(ex).__name__}: {ex}")

if __name__ == "__main__":
    diagnostico_conectividad_puertos()
    configuracion = diagnostico_configuracion_bucket()
    verificar_disponibilidad_bucket(configuracion)
    print("\n" + "=" * 75)
    print("  FIN DEL DIAGNÓSTICO")
    print("=" * 75 + "\n")
