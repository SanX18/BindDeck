# User Manual: BindDeck ESP32

Welcome to the **BindDeck** user manual, your custom macro keyboard powered by an ESP32. This manual details all the features of your device and how to get the most out of it using the desktop application.

---

## 1. Main Device Features
Your BindDeck device is not just a macro keyboard, it is an interactive desktop assistant.
* **8 Mechanical Keys (SW1 - SW8):** Fully customizable to open programs, send shortcuts, type text, or control media.
* **Smart Potentiometer:** Multifunction wheel with dynamic auto-calibration to control system volume, zoom, tab switching, or undo/redo.
* **Integrated OLED Screen:** Displays custom animations when each key is pressed, PC performance statistics (CPU and GPU), and an interactive sleep mode.
* **Dual Connectivity:** Communicates with the PC via **USB** (to receive settings and system statistics) and acts as a virtual keyboard via **Bluetooth** for latency-free control.

---

## 2. Initial Setup (First Steps)

1. **Firmware Installation:** Before using the application, make sure you have loaded the code onto the ESP32 (via PlatformIO or by installing the included `firmware.bin`).
2. **USB Connection:** Connect the BindDeck to your PC's USB port. This will power the device and establish the Serial connection needed for telemetry.
3. **Bluetooth Synchronization:** Pair the ESP32 in your computer's Bluetooth settings. It will appear as a Bluetooth keyboard.
4. **Open BindDeck App:** Start the executable on your computer. The application will automatically detect the USB port (COM) the device is connected to. If the connection indicator (top right) is green, you are ready!

---

## 3. Using the Desktop Application

The application has a virtual interface that mimics your physical hardware. Any changes you make here must be sent to the device by clicking the **Sync Device** button (blue button with an update icon).

### Customize Keys (Macros)
Click on any key (SW1 to SW8) in the virtual application to edit its behavior. A menu will open where you can configure:
* **Action Type:**
  * `Programa` (Program): Select the path of a `.exe` executable to open it instantly.
  * `Multimedia`: Controls like Play/Pause, Next, Previous, Mute.
  * `Atajo de teclado` (Keyboard shortcut): Combinations like `Ctrl + C`, `Alt + Tab`, etc.
  * `Texto` (Text): Type an entire paragraph by pressing a single button.
* **Label (On-Screen Text):** The short name that will appear on the OLED screen when the button is pressed.
* **OLED Animation:** Choose a specific animation (Check, Lightning, Mute, Heart, etc.) to play on the physical and virtual screen simultaneously when the key is pressed.

### Configure the Potentiometer (Wheel)
The analog knob is your best ally. On the right side panel you can select its operating mode (`encMode`):
* `Volumen de Windows` (Windows Volume): Raises and lowers the master volume.
* `Zoom`: Zooms in/out in browsers and editors (Ctrl +/-).
* `Pestañas` (Tabs): Navigates between open tabs in your browser.
* `Deshacer / Rehacer` (Undo / Redo): Ideal for design and editing.

*Technical Note:* The wheel incorporates continuous dynamic tracking logic. Every time you turn on the device, it adjusts millimeter by millimeter to the actual travel of your hardware to avoid dead zones. If you notice it lacks travel, turn it all the way to the stops once after turning it on.

### Brightness and Screen
* Adjust the **OLED Brightness** slider to change the intensity of the screen (ideal for working at night).
* When the keyboard detects inactivity (no keys pressed or wheel turned for 20 seconds), the screen will enter a "Sleep" mode to protect the OLED panel.

---

## 4. Telemetry and Resource Monitor (PC Monitor)
As long as the desktop application is open or minimized in the System Tray, it will be reading your computer's status in the background using *LibreHardwareMonitor*. 
On your BindDeck's sleep screen you will be able to see in real-time:
* **CPU and GPU Temperature** (in ºC).
* **CPU and GPU Load/Usage** (in %).

If any of the temperatures exceeds 85ºC, the device screen will show you a warning alert to protect your equipment.

---

## 5. Frequently Asked Questions / Troubleshooting

* **The indicator is red and says "Disconnected":** Make sure the USB cable supports data transmission and not just charging. Close other programs that might be occupying the COM port (such as the Arduino Serial Monitor or VSCode).
* **I press a button and it does nothing in Windows:** Verify that the device is properly paired via Bluetooth. The USB cable sends the settings, but the actual keystrokes are sent via Bluetooth (it acts as a wireless keyboard).
* **The volume wheel acts strangely on startup:** Simply turn the wheel once from one end to the other. The chip will learn its physical limits instantly and will be 100% accurate again.
* **The program doesn't read temperatures:** Make sure to run the BindDeck application as **Administrator**, as Windows requires elevated permissions for *LibreHardwareMonitor* to read motherboard and graphics card sensors.

---

Enjoy your BindDeck! If you find the project useful, you can support the creator by [buying him a coffee through GitHub Sponsors](https://github.com/sponsors/SanX18).

---

## 🇪🇸 Versión en Español / Spanish Version

# Manual de Usuario: BindDeck ESP32

Bienvenido al manual de usuario de **BindDeck**, tu teclado macro personalizado potenciado por un ESP32. Este manual detalla todas las características de tu dispositivo y cómo sacarle el máximo partido utilizando la aplicación de escritorio.

---

## 1. Características Principales del Dispositivo
Tu dispositivo BindDeck no es solo un teclado de macros, es un asistente de escritorio interactivo.
* **8 Teclas Mecánicas (SW1 - SW8):** Totalmente personalizables para abrir programas, enviar atajos, escribir textos o controlar multimedia.
* **Potenciómetro Inteligente:** Rueda multifunción con auto-calibración dinámica para controlar el volumen del sistema, zoom, cambio de pestañas o deshacer/rehacer.
* **Pantalla OLED Integrada:** Muestra animaciones personalizadas al pulsar cada tecla, estadísticas de rendimiento de tu PC (CPU y GPU) y un modo reposo interactivo.
* **Conectividad Dual:** Se comunica con el PC mediante **USB** (para recibir configuraciones y estadísticas del sistema) y actúa como teclado virtual mediante **Bluetooth** para un control sin latencia.

---

## 2. Configuración Inicial (Primeros Pasos)

1. **Instalación del Firmware:** Antes de usar la aplicación, asegúrate de haber cargado el código en el ESP32 (mediante PlatformIO o instalando el `firmware.bin` incluido).
2. **Conexión USB:** Conecta el BindDeck al puerto USB de tu PC. Esto alimentará el dispositivo y establecerá la conexión Serial necesaria para la telemetría.
3. **Sincronización Bluetooth:** Empareja el ESP32 en la configuración de Bluetooth de tu ordenador. Aparecerá como un teclado Bluetooth.
4. **Abrir BindDeck App:** Inicia el ejecutable en tu ordenador. La aplicación detectará automáticamente el puerto USB (COM) al que está conectado el dispositivo. Si el indicador de conexión (arriba a la derecha) está en verde, ¡estás listo!

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
En la pantalla de reposo de tu BindDeck podrás ver en tiempo real:
* **Temperatura de la CPU y GPU** (en ºC).
* **Carga/Uso de la CPU y GPU** (en %).

Si alguna de las temperaturas supera los 85ºC, la pantalla del dispositivo te mostrará una alerta de advertencia para proteger tu equipo.

---

## 5. Solución de Problemas Frecuentes

* **El indicador está rojo y pone "Desconectado":** Asegúrate de que el cable USB soporta transmisión de datos y no solo carga. Cierra otros programas que puedan estar ocupando el puerto COM (como el monitor serie de Arduino o VSCode).
* **Pulso un botón y no hace nada en Windows:** Comprueba que el dispositivo esté correctamente emparejado por Bluetooth. El cable USB envía los ajustes, pero las teclas reales se envían por Bluetooth (actúa como un teclado inalámbrico).
* **La rueda del volumen va extraña al arrancar:** Simplemente gira la rueda una vez de un extremo al otro. El chip aprenderá sus límites físicos instantáneamente y volverá a ser 100% preciso.
* **El programa no lee las temperaturas:** Asegúrate de ejecutar la aplicación BindDeck como **Administrador**, ya que Windows requiere permisos elevados para que *LibreHardwareMonitor* lea los sensores de la placa base y la gráfica.

---

¡Disfruta de tu BindDeck! Si el proyecto te resulta útil, puedes apoyar al creador [invitándole a un café a través de GitHub Sponsors](https://github.com/sponsors/SanX18).
