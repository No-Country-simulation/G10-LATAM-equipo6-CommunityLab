# Guía Práctica de Instalación y Configuración de ngrok

Esta guía detalla el paso a paso para instalar, autenticar y ejecutar **ngrok** en tu equipo local (Windows), permitiendo exponer el puerto local de **n8n** (`5678`) mediante un túnel seguro **HTTPS** para recibir Webhooks de Telegram, Discord y Slack.

---

## 1. ¿Qué es ngrok y por qué lo necesita el equipo?

En desarrollo local, aplicaciones como **n8n** corren en `http://localhost:5678`.

Sin embargo, las plataformas de mensajería (Telegram, Discord, Slack) se encuentran en internet público y **no pueden enviar datos a tu `localhost`**. Además, exigen obligatoriamente una dirección con **certificado SSL/HTTPS válido**.

**ngrok resuelve esto:**

1. Crea un túnel cifrado entre tu computadora e internet.
2. Te asigna una URL pública segura (ejemplo: `https://a1b2-c3d4.ngrok-free.app`).
3. Todo mensaje enviado a esa URL pública se redirige instantáneamente a tu `localhost:5678`.

```
[Telegram / Slack / Discord]
            │
            ▼ (HTTP POST Webhook público)
  [https://xxxx.ngrok-free.app]
            │
            ▼ (Túnel cifrado ngrok)
   [Tu PC: localhost:5678 (n8n)]
```

---

## 2. Paso 1: Crear Cuenta Gratuita y Obtener Authtoken

ngrok es gratuito para uso de desarrollo personal.

1. Ingresa a **[dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)**.
2. Crea tu cuenta (puedes registrarte en 1 clic con tu cuenta de GitHub o Google).
3. Una vez dentro del Dashboard de ngrok:
   - Ve a la sección **"Your Authtoken"** en el menú izquierdo (o ingresa a [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)).
   - Copia tu **Authtoken** personal (es una cadena alfanumérica larga, ej: `2abc1234XYZ...`).

> [!CAUTION]
> **Importante:** Tu authtoken es personal. **No** lo compartas ni lo subas a repositorios de GitHub.

---

## 3. Paso 2: Instalación de ngrok en Windows

Elige **uno** de los siguientes métodos según tu preferencia:

### Método A: Mediante Winget (Recomendado / El más rápido)

Abre **PowerShell** como usuario normal (o Administrador) y ejecuta:

```powershell
winget install ngrok.ngrok
```

_Reinicia tu terminal de PowerShell tras completar la instalación._

---

### Método B: Mediante Chocolatey o Scoop (Si ya los usas)

- Con Chocolatey:
  ```powershell
  choco install ngrok
  ```
- Con Scoop:
  ```powershell
  scoop install ngrok
  ```

---

### Método C: Descarga Manual Portable (Sin instaladores ni permisos de admin)

1. Ve a **[ngrok.com/download](https://ngrok.com/download)** y descarga la versión para **Windows (64-bit)** en archivo `.zip`.
2. Descomprime el archivo `.zip`. Obtendrás un único ejecutable: `ngrok.exe`.
3. Mueve `ngrok.exe` a una carpeta de tu preferencia (ej. `C:\tools\ngrok\` o directamente en tu carpeta de trabajo).
4. _(Opcional)_ Agrega esa carpeta a tus Variables de Entorno (`PATH`) para poder invocar `ngrok` desde cualquier terminal.

---

## 4. Paso 3: Configurar tu Authtoken (Se realiza una sola vez)

Abre una terminal de PowerShell o CMD y ejecuta el siguiente comando, reemplazando `<TU_AUTHTOKEN>` con el valor obtenido en el Paso 1:

```powershell
ngrok config add-authtoken <TU_AUTHTOKEN>
```

**Ejemplo:**

```powershell
ngrok config add-authtoken 2abc987654321_MiTokenSecreto
```

**Salida esperada:**

```text
Authtoken saved to configuration file: C:\Users\TuUsuario\AppData\Local\ngrok\ngrok.yml
```

---

## 5. Paso 4: Iniciar el Túnel para n8n

1. Asegúrate de que **n8n esté iniciado** en tu máquina (en el puerto `5678`).
2. En una nueva terminal de PowerShell, ejecuta:

   ```powershell
   ngrok http 5678
   ```

3. Verás una pantalla en la terminal similar a esta:

```text
ngrok                                                               (Ctrl+C to quit)

Session Status                online
Account                       Tu Nombre (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://3a1b-181-66-10-5.ngrok-free.app -> http://localhost:5678

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 📌 Datos clave de la pantalla:

- **`Forwarding`**: La URL pública HTTPS generada:
  `https://3a1b-181-66-10-5.ngrok-free.app` ➡️ Esta es la URL que debes copiar para los Webhooks.
- **`Web Interface` (`http://127.0.0.1:4040`)**: Panel web local donde puedes ver en tiempo real cada petición HTTP que entra, sus headers, cuerpo JSON y estado de respuesta. ¡Excelente para depuración!
- **Para detener ngrok:** Presiona `Ctrl + C`.

---

## 6. Paso 5: Indicarle a n8n cuál es tu URL Pública

Para que n8n sepa construir correctamente las URLs de los Webhooks (como en el nodo Telegram Trigger):

### Si ejecutas n8n mediante Docker:

Pasa la variable de entorno `WEBHOOK_URL` con tu enlace ngrok:

```bash
docker run -it --rm --name n8n   -p 5678:5678   -e WEBHOOK_URL=https://3a1b-181-66-10-5.ngrok-free.app/   -v n8n_data:/home/node/.n8n   docker.n8n.io/n8nio/n8n
```

### Si ejecutas n8n localmente con npm / npx:

En la terminal de PowerShell donde levantas n8n, define la variable antes de ejecutarlo:

```powershell
$env:WEBHOOK_URL="https://3a1b-181-66-10-5.ngrok-free.app/"
npx n8n
```

---

## 7. 💡 Tip Pro: Dominio Estático Gratuito (Para no cambiar la URL al reiniciar)

Por defecto, cada vez que cierras y abres ngrok, la URL cambia. Sin embargo, **la cuenta gratuita de ngrok incluye 1 Dominio Estático permanente gratis**.

### Cómo activarlo:

1. En el Dashboard de ngrok, ve a **Cloud Edge** ➡️ **Domains** ([dashboard.ngrok.com/cloud-edge/domains](https://dashboard.ngrok.com/cloud-edge/domains)).
2. Haz clic en **"Create Domain"**.
3. Se generará un dominio fijo para ti (por ejemplo: `mi-equipo-lab.ngrok-free.app`).
4. Para iniciar ngrok siempre con ese dominio fijo, ejecuta:
   ```powershell
   ngrok http 5678 --domain=mi-equipo-lab.ngrok-free.app
   ```
   _¡Con esto tu URL nunca cambiará y no tendrás que actualizar tus webhooks cada día!_

---

## 8. Diagnóstico y Preguntas Frecuentes

### ¿Qué hago si sale el error `ERR_NGROK_4018`?

Significa que no has configurado el authtoken. Repite el **Paso 3**:
`ngrok config add-authtoken <TU_TOKEN>`.

### ¿Qué hago si al abrir la URL en el navegador sale una pantalla de aviso de ngrok?

ngrok muestra una página intermedia de aviso (_"You are about to visit..."_) cuando alguien abre la URL en un navegador web.

- **Para Webhooks automáticos (Telegram, Discord, Slack):** No te preocupes, las peticiones POST de los bots la atraviesan automáticamente sin problema.
- **Si pruebas manualmente con Postman / curl:** Agrega el encabezado HTTP:
  `ngrok-skip-browser-warning: true`

### ¿Debo dejar la ventana de ngrok abierta?

**Sí.** Mientras estés realizando pruebas de n8n con Telegram, Discord o Slack, la ventana de ngrok debe permanecer abierta. Si cierras la terminal, el túnel se interrumpe.
