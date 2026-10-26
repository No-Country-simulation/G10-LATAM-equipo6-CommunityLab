# Guía: Dominio, HTTPS y proxy inverso para CommunityLab en OCI

Esta guía describe cómo exponer la aplicación **CommunityLab**, desplegada en una instancia Ubuntu de Oracle Cloud Infrastructure (OCI), mediante DuckDNS y Caddy. Caddy recibe las conexiones HTTP/HTTPS y las reenvía a Streamlit, que escucha internamente en el puerto `8501`.

## Datos del despliegue

- **Dominio:** `hackathon-g10-latam-06.duckdns.org`
- **Token:** `<TU_DUCKDNS_TOKEN>`
- **IP pública actual de OCI:** `147.15.9.116`
- **Aplicación:** CommunityLab (Streamlit)
- **Puerto interno de Streamlit:** `8501`
- **URL pública prevista:** `https://hackathon-g10-latam-06.duckdns.org/`

> **Seguridad del token:** No escribas tu token real de DuckDNS en este documento, en el repositorio, en una URL compartida ni en capturas de pantalla. Guárdalo de forma segura en las variables de entorno o gestor de secretos.

## 1. Apuntar el dominio a la instancia OCI

En DuckDNS, confirma que el subdominio `hackathon-g10-latam-06` exista y que su IPv4 apunte a `147.15.9.116`. Si la IP pública de la instancia cambia, actualiza el registro de DuckDNS o configura su actualizador periódico con el token correspondiente.

La API de DuckDNS acepta una solicitud HTTPS con los parámetros `domains`, `token` e `ip`. Ejecuta la solicitud desde un entorno seguro, sustituyendo el marcador por tu token sin guardarlo en el repositorio:

```text
https://www.duckdns.org/update?domains=hackathon-g10-latam-06&token=<TU_DUCKDNS_TOKEN>&ip=147.15.9.116
```

La respuesta esperada es `OK`. Comprueba después la resolución DNS:

```bash
nslookup hackathon-g10-latam-06.duckdns.org 8.8.8.8
```

El resultado debe incluir `147.15.9.116`. Si no coincide, espera la propagación o corrige el registro antes de solicitar el certificado.

## 2. Permitir tráfico web en los firewalls

### Reglas de ingreso de OCI

En la Security List de la subred o en el Network Security Group (NSG) asociado a la instancia, permite tráfico TCP de entrada desde `0.0.0.0/0` en:

- **80:** HTTP y validación HTTP-01 de Let's Encrypt.
- **443:** HTTPS público.

No abras el puerto `8501` a Internet. Caddy accederá a Streamlit desde la propia instancia.

### Firewall de Ubuntu

Comprueba qué firewall está activo y añade las reglas equivalentes en el mecanismo que ya use la instancia. Por ejemplo, si está habilitado UFW:

```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

No cambies la política predeterminada ni deshabilites el firewall como parte de este procedimiento. Si la instancia usa reglas `iptables` persistentes en lugar de UFW, permite TCP `80` y `443` y guarda las reglas con el mecanismo persistente ya instalado.

## 3. Confirmar que CommunityLab está disponible localmente

Antes de configurar el proxy, verifica que Streamlit esté ejecutándose en la instancia y responda en el puerto `8501`:

```bash
curl -I http://127.0.0.1:8501/
```

Si no responde, inicia o repara el servicio de CommunityLab según el método de despliegue existente. Caddy no inicia la aplicación: solo reenvía las solicitudes. No se requiere un backend FastAPI ni un servicio en el puerto `8000` para esta configuración.

Siempre que la configuración actual de Streamlit lo permita, enlaza Streamlit a `127.0.0.1` para que no acepte conexiones externas directas. Si el servicio está enlazado a `0.0.0.0`, mantén igualmente el puerto `8501` cerrado en los firewalls de OCI y Ubuntu.

## 4. Instalar Caddy

Si Caddy aún no está instalado, utiliza el repositorio oficial para Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' |
  sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' |
  sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update
sudo apt-get install -y caddy
```

## 5. Configurar el proxy inverso de Caddy

Edita `/etc/caddy/Caddyfile` y configura el dominio real. Para CommunityLab, todo el tráfico se dirige a Streamlit:

```caddy
hackathon-g10-latam-06.duckdns.org {
    reverse_proxy 127.0.0.1:8501
}
```

Caddy gestiona automáticamente el certificado TLS y el proxy de WebSocket necesario por Streamlit. Elimina cualquier configuración de ejemplo que use otro dominio o enrute rutas a FastAPI si ese backend no forma parte del despliegue actual.

Valida la configuración y recarga el servicio:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl enable caddy
sudo systemctl reload caddy
```

Si el servicio todavía no estaba iniciado, usa `sudo systemctl start caddy`. Para revisar su estado y los logs:

```bash
sudo systemctl status caddy --no-pager
sudo journalctl -u caddy -n 100 --no-pager
```

La emisión del certificado de Let's Encrypt requiere que el DNS ya apunte a esta instancia y que los puertos TCP `80` y `443` sean accesibles desde Internet. Caddy obtiene y renueva el certificado automáticamente. No declares el certificado como emitido hasta verificarlo en los logs o al abrir el sitio por HTTPS.

## 6. Validación del acceso

Desde la instancia, comprueba que el sitio HTTPS responde:

```bash
curl -I https://hackathon-g10-latam-06.duckdns.org/
```

Luego abre en un navegador:

**https://hackathon-g10-latam-06.duckdns.org/**

Si falla, revisa en este orden:

1. El dominio resuelve a la IP pública actual de la instancia.
2. CommunityLab responde localmente en `127.0.0.1:8501`.
3. Las reglas de ingreso OCI y el firewall del sistema permiten TCP `80` y `443`.
4. El Caddyfile pasa `caddy validate` y el servicio Caddy está activo.
5. Los logs de Caddy no muestran errores de DNS, conexión o emisión TLS.

## Puerto de acceso

No es necesario incluir `:8501` en la URL pública. El navegador se conecta a Caddy por el puerto estándar `443` (HTTPS), y Caddy reenvía la solicitud al puerto `8501` de Streamlit dentro de la instancia. El acceso HTTP por el puerto `80` se usa para redirigir/procesar la validación; la URL recomendada para usuarios es la dirección HTTPS indicada arriba.
