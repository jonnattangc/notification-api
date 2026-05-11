# monitoring
Aplicación de apoyo al monitoreo

## Arquitectura de 2 capas

El proyecto fue refactorizado para separar responsabilidades en dos capas claras:

### 1. Capa de Presentación (API / Web)
Responsable de recibir las peticiones HTTP, manejar la configuración del servidor, CORS, logging de aplicación y devolver las respuestas. No contiene lógica de negocio directa; delega todo en la capa de servicio.

- `app/main.py`: Punto de entrada. Configura Flask, CORS, logging y levanta el servidor.
- `app/api/routes.py`: Define las rutas del Blueprint, recibe los `request` de Flask y construye una estructura plana que se envía al servicio. Maneja archivos estáticos (JS) y templates (web).

### 2. Capa de Servicio (Lógica de Negocio + Persistencia)
Contiene toda la lógica de negocio, acceso a datos, envío de notificaciones y utilidades (cifrado). Es totalmente independiente de Flask.

- `app/service/notification_service.py`: Orquesta el flujo completo de una notificación: validación de `x-api-key`, desencriptación opcional, lanzamiento del hilo de envío y manejo de respuestas.
- `app/service/client_repository.py`: Encapsula el acceso a la base de datos MySQL para obtener los datos del cliente según su API key.
- `app/service/email_notification.py`: Envío de correos vía SMTP (Gmail).
- `app/service/waza_message.py`: Envío de mensajes de WhatsApp via API de Meta.
- `app/service/slack_notification.py`: Envío de alertas a canales de Slack.
- `app/service/cipher.py`: Cifrado/descifrado AES.

## Ejecución

Desde la raíz del proyecto:

```bash
python -m app.main 8085
```

O directamente:

```bash
python app/main.py 8085
```

> Asegúrate de tener instaladas las dependencias necesarias: `flask`, `flask-cors`, `pymysql`, `psutil`, `pycryptodome`, `requests`.
