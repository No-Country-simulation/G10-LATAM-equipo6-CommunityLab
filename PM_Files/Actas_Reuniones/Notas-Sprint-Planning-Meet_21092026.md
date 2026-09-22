sept 21, 2026

## **Sprint Planning Meet (Obligatorio)**

Invitado [maxcabanillassalas@gmail.com](mailto:maxcabanillassalas@gmail.com) [rauldelfin.gallardo@gmail.com](mailto:rauldelfin.gallardo@gmail.com) [enriquezariasedwingustavo@gmail.com](mailto:enriquezariasedwingustavo@gmail.com) [medinajose997@gmail.com](mailto:medinajose997@gmail.com) [César Augusto Cely Pulido](mailto:ccelypulido@gmail.com) [juanmancillaster@gmail.com](mailto:juanmancillaster@gmail.com) [rodrigo7623@gmail.com](mailto:rodrigo7623@gmail.com) [carol.huarancay@gmail.com](mailto:carol.huarancay@gmail.com)

Archivos adjuntos [Sprint Planning Meet (Obligatorio)](https://calendar.google.com/calendar/event?eid=M2hvYXN1bGJibzl0aTQza3M3dWhiOW84YWhfMjAyNjA5MjJUMDAwMDAwWiBjY2VseXB1bGlkb0Bt)

Registros de la reunión [Transcripción](https://docs.google.com/document/d/1No8FWxeM7hYfMi2hF-I1DV1CtnhhHYjnby9wPEKnspM/edit?usp=drive_web&tab=t.afp9131fwiwm)&nbsp;

&nbsp;

&nbsp;

### **Resumen**

Integración de repositorios y validación de motores mediante almacenamiento en Oracle Cloud

**Unificación de repositorios y motores**  
Consenso para unificar las líneas de trabajo utilizando la estructura del repositorio. Mantenimiento de motores funcionales en Python y N8N.

**Gestión de recursos y almacenamiento**  
Implementación de registros de actividad para mitigar limitaciones de tokens. Configuración exitosa de rutas y almacenamiento en Oracle Cloud.

**Planificación y despliegue del servidor**  
Priorización del procesamiento por lotes para el Producto Mínimo Viable. Fusión de ramas principales y actualización de servicios en el servidor.

&nbsp;

&nbsp;

### **Decisiones**

## Acordada

* **Unificación de ramas de desarrollo en \`main\`** Se acordó fusionar la rama integrada de trabajo con los flujos de Python y N8N directamente en el repositorio principal (\`main\`).

&nbsp;

&nbsp;

### **Próximos pasos**

- [ ] \[Carol Huarancay\] Crear prototipo Frontend: Generar un diseño o prototipo para mejorar la interfaz de usuario del proyecto.

- [ ] \[José\] Configurar permisos servidor: Habilitar conexiones entrantes en el puerto 8501 dentro de la infraestructura de Oracle Cloud.

- [ ] \[El grupo\] Actualizar repositorio principal: Sincronizar las ramas del código para integrar los avances unificados en la versión principal del proyecto.

- [ ] \[César Augusto Cely Pulido\] Comunicar estado rama: Informar a todos los colaboradores sobre la integración exitosa de las ramas y la actualización del repositorio principal.

- [ ] \[El grupo\] Configurar variables entorno: Establecer los valores necesarios para la conexión con el repositorio de datos de Oracle en los entornos locales de desarrollo.

&nbsp;

&nbsp;

### **Detalles**

* **Integración del proyecto y repositorios**: César Augusto Cely Pulido planteó el problema de unificar los desarrollos previos realizados con N8N, Streamlit y el repositorio en Oracle. Durante la discusión, Raul Gallardo reportó un error con la clave API de Groq ([00:01:16](?tab=t.afp9131fwiwm#heading=h.d44uwomf7ojr)), mientras que Max Ferrer Cabanillas Salas explicó que la arquitectura debía permitir alternar entre configuraciones locales de Docker y el entorno en Oracle Cloud Infrastructure (OCI) ([00:04:52](?tab=t.afp9131fwiwm#heading=h.egdg423ulxlc)). Ante dificultades de acceso al entorno virtual en OCI, César Augusto Cely Pulido creó un nuevo depósito en una cuenta personal para verificar las pruebas ([00:05:55](?tab=t.afp9131fwiwm#heading=h.mzflw68xeirp)). Como consenso, se acordó unificar las líneas de trabajo utilizando la estructura del repositorio ([00:04:52](?tab=t.afp9131fwiwm#heading=h.egdg423ulxlc)).

* **Validación de los motores de ejecución en Python y N8N**: Se evaluó la operatividad de los flujos para garantizar el funcionamiento del Producto Mínimo Viable ([00:08:34](?tab=t.afp9131fwiwm#heading=h.vpwpmrcjwqcb)). Max Ferrer Cabanillas Salas argumentó que los flujos de Python y N8N no son excluyentes y pueden coexistir, aclarando que herramientas como N8N se aplicarían para multiagentes o canales como Slack en etapas posteriores, pero que actualmente se procesan lotes de datos ([00:07:49](?tab=t.afp9131fwiwm#heading=h.esiu8hw1xxiw)). César Augusto Cely Pulido detalló que el flujo de N8N genera cuatro archivos específicos correspondientes a soporte técnico, marketing, showcase, y métricas o feedback de la comunidad ([00:08:34](?tab=t.afp9131fwiwm#heading=h.vpwpmrcjwqcb)). Se decidió mantener ambos motores funcionales ([00:06:45](?tab=t.afp9131fwiwm#heading=h.qup7w5427jjz)).

* **Gestión de limitaciones de tokens y registros de control**: Se abordó el problema del consumo de recursos en las herramientas de inteligencia artificial durante las pruebas. César Augusto Cely Pulido y Max Ferrer Cabanillas Salas señalaron que la capa gratuita de Groq a menudo se llena, obligando a cambiar de modelo o gestionar restricciones de tokens. Para mitigar esto, Max Ferrer Cabanillas Salas indicó que se crearon registros de actividad detallados para auditar las ejecuciones ([00:11:29](?tab=t.afp9131fwiwm#heading=h.no9xrt6rbylz)). Se acordó utilizar dichos registros para facilitar la identificación de errores en las pruebas con muestras de 3, 5, 7 y 15 registros ([00:10:29](?tab=t.afp9131fwiwm#heading=h.h29tfjf5cfzd)).

* **Estructura del proceso de curación y almacenamiento en OCI**: Se discutió la lógica de iteración y persistencia de los datos curados. César Augusto Cely Pulido explicó los nodos configurados en N8N para realizar bucles, formatear los datos bajo la ruta de año, mes y día, y subir cuatro archivos clasificados al depósito de OCI ([00:13:58](?tab=t.afp9131fwiwm#heading=h.iyresv286d5q)) ([00:16:00](?tab=t.afp9131fwiwm#heading=h.s5z0wol0npeg)). Asimismo, César Augusto Cely Pulido indicó que se implementó un archivo de control de curación para registrar las acciones realizadas y evitar duplicar revisiones, a menos que se elimine dicho archivo de control ([00:14:57](?tab=t.afp9131fwiwm#heading=h.olo5noruxxib)). Max Ferrer Cabanillas Salas confirmó que esta estructura permite reiniciar el proceso cuando sea necesario ([00:16:00](?tab=t.afp9131fwiwm#heading=h.s5z0wol0npeg)).

* **Planificación y definición de la interfaz de usuario**: Se revisó el avance hacia la tercera semana de la planificación relacionada con la interfaz de Streamlit. Max Ferrer Cabanillas Salas opinó que la interfaz actual cumple una función exclusiva de pruebas y que el equipo de desarrollo frontend debe encargarse de adecuarla para las personas usuarias finales ([00:17:00](?tab=t.afp9131fwiwm#heading=h.sydty2dlsgwo)). César Augusto Cely Pulido recordó que se había constituido una célula frontend que incluía a Carol Huarancay ([00:18:58](?tab=t.afp9131fwiwm#heading=h.5ao7qdid8ael)). Carol Huarancay acordó revisar las alternativas posibles para lograr un diseño amigable ([00:19:39](?tab=t.afp9131fwiwm#heading=h.ngm7fzb1xzq1)).

* **Requisitos de carga automática y despliegue del servidor**: Se evaluó el cumplimiento de los lineamientos del proyecto referentes a la ingesta de datos. Carol Huarancay recordó que la documentación estipula que la recopilación de información debe ser automática mediante canales como Slack o lotes de 15 registros en formato CSV o JSON ([00:20:53](?tab=t.afp9131fwiwm#heading=h.ixt9g19yzvqm)). Max Ferrer Cabanillas Salas y César Augusto Cely Pulido coincidieron en que el procesamiento por lotes es prioritario para el Producto Mínimo Viable, mientras que la integración con canales de mensajería se puede programar posteriormente ([00:21:57](?tab=t.afp9131fwiwm#heading=h.fy13gneda18n)). En cuanto al servidor, César Augusto Cely Pulido confirmó que las pruebas de escritura y lectura de archivos en OCI se ejecutaron satisfactoriamente ([00:20:53](?tab=t.afp9131fwiwm#heading=h.ixt9g19yzvqm)).

* **Fusión de ramas principales y configuración de acceso**: Se coordinó la consolidación del código y la distribución de credenciales para el equipo. Max Ferrer Cabanillas Salas estuvo de acuerdo en realizar la fusión de las ramas al repositorio principal ([00:26:19](?tab=t.afp9131fwiwm#heading=h.acvk0p1xerja)). César Augusto Cely Pulido ejecutó la fusión, actualizó los servicios en el servidor principal y compartió a través de Slack los datos de conexión SSH utilizando la dirección IP 147.159.116, el usuario ubuntu, el directorio G10, la clave y las variables de entorno de OCI ([00:28:30](?tab=t.afp9131fwiwm#heading=h.u5fa0ft682qb)) ([00:40:57](?tab=t.afp9131fwiwm#heading=h.jqi7j37dnshc)). César Augusto Cely Pulido indicó que se debe solicitar asistencia para habilitar los permisos de entrada al puerto 8501 ([00:35:59](?tab=t.afp9131fwiwm#heading=h.x1dw17jomub)). Finalmente, se acordó convocar a la próxima sesión de trabajo para el miércoles a las 9:00 hora de Argentina ([00:40:57](?tab=t.afp9131fwiwm#heading=h.jqi7j37dnshc)).

&nbsp;

&nbsp;

*Revisa las notas de Gemini para asegurarte de que sean precisas. [Obtén sugerencias y descubre cómo Gemini toma notas](https://support.google.com/meet/answer/14754931)*

*Cómo es la calidad de **estas notas específicas?** [Responde una breve encuesta](https://google.qualtrics.com/jfe/form/SV_5bXzKQfylMIhSXc?confid=3Uy2lcpa9Js-kBAt4a6tDxIXOBEBMgUIigIgABgBCA&detailLevel=standard&hasImages=False&entryPoint=footerMain&isGoogler=False) para darnos tu opinión; por ejemplo, cuán útiles te resultaron las notas.*