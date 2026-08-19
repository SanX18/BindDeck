# Manual de Usuario: MacroDeck ESP32

Bienvenido al manual de usuario de **MacroDeck**, tu teclado macro personalizado potenciado por un ESP32. Este manual detalla todas las características de tu dispositivo y cómo sacarle el máximo partido utilizando la aplicación de escritorio.

---

## 1. Características Principales del Dispositivo
Tu dispositivo MacroDeck no es solo un teclado de macros, es un asistente de escritorio interactivo.
* **8 Teclas Mecánicas (SW1 - SW8):** Totalmente personalizables para abrir programas, enviar atajos, escribir textos o controlar multimedia.
* **Potenciómetro Inteligente:** Rueda multifunción con auto-calibración dinámica para controlar el volumen del sistema, zoom, cambio de pestañas o deshacer/rehacer.
* **Pantalla OLED Integrada:** Muestra animaciones personalizadas al pulsar cada tecla, estadísticas de rendimiento de tu PC (CPU y GPU) y un modo reposo interactivo.
* **Conectividad Dual:** Se comunica con el PC mediante **USB** (para recibir configuraciones y estadísticas del sistema) y actúa como teclado virtual mediante **Bluetooth** para un control sin latencia.

---

## 2. Configuración Inicial (Primeros Pasos)

1. **Instalación del Firmware:** Antes de usar la aplicación, asegúrate de haber cargado el código en el ESP32 (mediante PlatformIO o instalando el `firmware.bin` incluido).
2. **Conexión USB:** Conecta el MacroDeck al puerto USB de tu PC. Esto alimentará el dispositivo y establecerá la conexión Serial necesaria para la telemetría.
3. **Sincronización Bluetooth:** Empareja el ESP32 en la configuración de Bluetooth de tu ordenador. Aparecerá como un teclado Bluetooth.
4. **Abrir MacroDeck App:** Inicia el ejecutable en tu ordenador. La aplicación detectará automáticamente el puerto USB (COM) al que está conectado el dispositivo. Si el indicador de conexión (arriba a la derecha) está en verde, ¡estás listo!

---

## 3. Uso de la Aplicación de Escritorio

La aplicación tiene una interfaz virtual que imita a tu hardware físico. Cualquier cambio que hagas aquí debe ser enviado al dispositivo pulsando el botón de **Sincronizar Dispositivo** (botón azul con icono de actualización).

### Personalizar las Teclas (Macros)
Haz clic en cualquier tecla (SW1 a SW8) en la aplicación virtual para editar su comportamiento. Se abrirá un menú donde podrás configurar:
* **Tipo de Acción:**
  * `Programa`: Selecciona la ruta de un ejecutable `.exe` para abrirlo al instante.
  * `Multimedia`: Controles como Play/Pausa, Siguiente, Anterior, Mutear.
  * `Atajo de teclado`: Combinaciones como `Ctrl + C`, `Alt + Tab`, etc.
  * `Texto`: Escribe un párrafo entero pulsando un solo botón.
* **Etiqueta (Texto en Pantalla):** El nombre corto que aparecerá en la pantalla OLED al pulsar el botón.
* **Animación OLED:** Elige una animación específica (Check, Rayo, Mute, Corazón, etc.) para que se reproduzca en la pantalla física y virtual simultáneamente al pulsar la tecla.

### Configurar el Potenciómetro (Rueda)
El mando analógico es tu mejor aliado. En el panel lateral derecho puedes seleccionar su modo de funcionamiento (`encMode`):
* `Volumen de Windows`: Sube y baja el volumen maestro.
* `Zoom`: Hace zoom in/out en navegadores y editores (Ctrl +/-).
* `Pestañas`: Navega entre las pestañas abiertas de tu navegador.
* `Deshacer / Rehacer`: Ideal para diseño y edición.

*Nota Técnica:* La rueda incorpora una lógica de rastreo dinámico continuo. Cada vez que enciendes el dispositivo, se ajusta milimétricamente al recorrido real de tu hardware para evitar zonas muertas. Si notas que le falta recorrido, gírala hasta los topes una vez tras encenderlo.

### Brillo y Pantalla
* Ajusta el control deslizante de **Brillo OLED** para cambiar la intensidad de la pantalla (ideal para trabajar de noche).
* Cuando el teclado detecta inactividad (sin pulsar teclas ni girar la rueda durante 20 segundos), la pantalla entrará en un modo "Reposo" para proteger el panel OLED.

---

## 4. Telemetría y Monitor de Recursos (PC Monitor)
Mientras la aplicación de escritorio esté abierta o minimizada en la bandeja del sistema (System Tray), estará leyendo en segundo plano el estado de tu ordenador utilizando *LibreHardwareMonitor*. 
En la pantalla de reposo de tu MacroDeck podrás ver en tiempo real:
* **Temperatura de la CPU y GPU** (en ºC).
* **Carga/Uso de la CPU y GPU** (en %).

Si alguna de las temperaturas supera los 85ºC, la pantalla del dispositivo te mostrará una alerta de advertencia para proteger tu equipo.

---

## 5. Solución de Problemas Frecuentes

* **El indicador está rojo y pone "Desconectado":** Asegúrate de que el cable USB soporta transmisión de datos y no solo carga. Cierra otros programas que puedan estar ocupando el puerto COM (como el monitor serie de Arduino o VSCode).
* **Pulso un botón y no hace nada en Windows:** Comprueba que el dispositivo esté correctamente emparejado por Bluetooth. El cable USB envía los ajustes, pero las teclas reales se envían por Bluetooth (actúa como un teclado inalámbrico).
* **La rueda del volumen va extraña al arrancar:** Simplemente gira la rueda una vez de un extremo al otro. El chip aprenderá sus límites físicos instantáneamente y volverá a ser 100% preciso.
* **El programa no lee las temperaturas:** Asegúrate de ejecutar la aplicación MacroDeck como **Administrador**, ya que Windows requiere permisos elevados para que *LibreHardwareMonitor* lea los sensores de la placa base y la gráfica.

---

¡Disfruta de tu MacroDeck! Si el proyecto te resulta útil, puedes apoyar al creador [invitándole a un café a través de GitHub Sponsors](https://github.com/sponsors/SanX18).
