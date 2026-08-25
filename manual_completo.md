# Complete User Manual: BindDeck ESP32

Welcome to the official user manual for **BindDeck**, your custom macro keyboard powered by an ESP32. This document provides all the instructions to build your device, configure it, and get the most out of it with the PC application.

---

## 1. Introduction and Features

BindDeck is a complete hardware and software ecosystem designed to boost your productivity and your setup. It turns a simple ESP32 microcontroller into a powerful custom macro keyboard, equipped with an interactive OLED display, an analog control, and mechanical buttons.

### What does BindDeck do?
* **Launcher and Shortcuts (8 Buttons):** Assign complex keyboard combinations, launch your favorite programs, or execute entire blocks of text with a single press.
* **Smart Analog Control:** Incorporates a potentiometer with dynamic auto-calibration to adjust the overall volume, zoom, navigate through tabs, or use undo/redo.
* **Hardware Monitor (Telemetry):** Its OLED screen shows animations when pressing buttons and, when idle, acts as a monitor showing your CPU and GPU temperatures and load in real time.
* **Customizable Texts:** Configure the text you want to appear on the screen for each of the 8 buttons.
* **Dual Hybrid Connectivity:** Use it via USB cable or **100% Wireless** (sends macros to the PC via **Bluetooth LE** and receives temperature data via **Wi-Fi UDP Zero-Config**).
* **Integrated PC Software (Plug & Play):** Modern, bilingual desktop application to configure everything visually.

---

## 2. Hardware Used (Bill of Materials - BOM)

To assemble your BindDeck, you will need the following inexpensive components:

1. **Microcontroller:** ESP32 (The ESP32-WROOM-32 Dev Kit model is recommended).
2. **Display:** 0.96-inch I2C OLED Display (128x64 resolution, SSD1306 controller).
3. **Switches / Buttons:** 8x Mechanical Switches (e.g. **Outemu Red** for their smooth and quiet feel).
4. **Analog Control:** 1x B10K Linear Potentiometer (10 kOhms).
5. **Case:** 3D printable (available on Makerworld).
6. **Wiring:** Dupont cables for connections (or dedicated PCB).
7. **Extras:** Keycaps and the knob for the potentiometer.

---

## 3. Wiring Diagram and Assembly

The wiring is straightforward. You do not need to install additional resistors for the buttons, as the software uses the internal resistors (INPUT_PULLUP) of the ESP32.

### OLED Display (I2C Communication)
* **VCC:** Connect to **3.3V** of the ESP32.
* **GND:** Connect to **GND** of the ESP32.
* **SDA (Data):** Connect to **GPIO 21**.
* **SCL (Clock):** Connect to **GPIO 22**.

### Analog Potentiometer
* **Left Pin:** Connect to **3.3V** of the ESP32.
* **Center Pin (Signal):** Connect to **GPIO 34**.
* **Right Pin:** Connect to **GND** of the ESP32.

### Mechanical Switches
Each mechanical switch has two pins:
1. One pin from **ALL** switches must be bridged and connected to **GND (Ground)**.
2. The remaining pin of each switch is connected to the ESP32 pins:
   * **Switch 1:** GPIO 13
   * **Switch 2:** GPIO 12
   * **Switch 3:** GPIO 14
   * **Switch 4:** GPIO 27
   * **Switch 5:** GPIO 26
   * **Switch 6:** GPIO 25
   * **Switch 7:** GPIO 33
   * **Switch 8:** GPIO 32

<div class="note">
<strong>Assembly Tip:</strong> You can solder or daisy-chain all the GND pins of the 8 switches and the potentiometer with the same wire, running a single wire to the GND pin of the ESP32.
</div>

---

## 4. First Steps and Configuration

1. **Firmware Installation:** Upload the code to your ESP32 using PlatformIO or flash the precompiled firmware.bin file.
2. **USB Connection:** Connect the BindDeck via USB to your PC. This turns on the device and enables the Serial connection for telemetry.
3. **Bluetooth Pairing:** Go to your Windows Bluetooth settings and pair the device. It will show up recognized as a **Bluetooth keyboard**.
4. **Open the BindDeck Application:** Launch the executable on your PC. The app will automatically detect the USB port (COM). If the top right indicator is green, you are already connected!
   * *Important:* Run the app as **Administrator** the first time so LibreHardwareMonitor can read the temperature sensors.

---

## 5. Application Usage Guide (PC)

The application has a virtual interface identical to your hardware. Any change you make is sent to the hardware by pressing the **Sync Device** button (blue refresh icon).

### Customize Keys (Macros)
Click on any key (SW1 to SW8) in the app to edit it:
* **Action:**
  * `Program`: Select an .exe file to launch.
  * `Multimedia`: Play/Pause, Next, Mute, etc.
  * `Shortcut`: Key combinations (Ctrl + C, Alt + Tab).
  * `Text`: Type entire phrases or paragraphs automatically.
* **Label:** The short text (max 8-10 characters) that will be shown on the OLED display.
* **OLED Animation:** Select the icon (Check, Lightning, Heart, etc.) that will appear when pressed.

### Configure the Potentiometer
Select the dial's operating mode from the right panel (encMode):
* `Volume`: Controls the Windows master volume.
* `Zoom`: Zooms in or out in browsers (Ctrl +/-).
* `Tabs`: Quickly switches between tabs.
* `Undo / Redo`: Editing control.

<div class="note">
<strong>Dynamic Tracking:</strong> The potentiometer auto-calibrates. If you notice it lacks range, turn it to the extreme limits once after turning it on. The chip will automatically learn its limits.
</div>

### Brightness and Sleep Mode
Adjust the **OLED Brightness** from the control panel. If you don't use the keyboard for 20 seconds, the screen will go into **Telemetry / Sleep** mode to protect the OLED panel and show the PC data.

---

## 6. Common Troubleshooting

* **The app indicator is red (Disconnected):**
  * Make sure to use a **data** USB cable (not just for charging).
  * Close other programs that might occupy the COM port (e.g. Arduino IDE or Cura).
* **I press a button and nothing happens:**
  * Check that BindDeck is connected via **Bluetooth**. The USB cable sends the configuration and screen data, but keyboard presses are sent via Bluetooth for greater compatibility and lower latency in games.
* **CPU/GPU temperatures read 0 or are not read:**
  * The application must have **Administrator** permissions in Windows to access system sensors.
* **Volume jumps erratically:**
  * Turn the potentiometer from one end to the other (from 0 to 100). The calibration algorithm will adjust the internal margins immediately.

---

<div class="center">
  <p><em>Thank you for downloading and assembling BindDeck.</em></p>
  <p>If you liked this project, please consider supporting the creator <strong>@SanX18</strong>.</p>
</div>

---

## 🇪🇸 Versión en Español / Spanish Version

# Manual de Usuario Completo: BindDeck ESP32

Bienvenido al manual de usuario oficial de **BindDeck**, tu teclado macro personalizado potenciado por un ESP32. Este documento proporciona todas las instrucciones para construir tu dispositivo, configurarlo y sacarle el máximo provecho con la aplicación de PC.

---

## 1. Introducción y Características

BindDeck es un ecosistema completo de hardware y software diseñado para potenciar tu productividad y tu setup. Convierte un simple microcontrolador ESP32 en un potente teclado de macros personalizado, equipado con una pantalla OLED interactiva, un control analógico y botones mecánicos.

### Qué hace BindDeck?
* **Lanzador y Atajos (8 Botones):** Asigna combinaciones complejas de teclado, lanza tus programas favoritos o ejecuta bloques enteros de texto con una sola pulsación.
* **Control Analógico Inteligente:** Incorpora un potenciómetro con auto-calibración dinámica para ajustar el volumen general, hacer zoom, navegar por pestañas o usar el deshacer/rehacer.
* **Monitor de Hardware (Telemetría):** Su pantalla OLED muestra animaciones al pulsar botones y, en reposo, actúa como un monitor mostrando las temperaturas y la carga de tu CPU y GPU en tiempo real.
* **Textos Personalizables:** Configura el texto que quieres que aparezca en la pantalla para cada uno de los 8 botones.
* **Conectividad Dual Híbrida:** Úsalo por cable USB o **100% Inalámbrico** (envía macros al PC vía **Bluetooth LE** y recibe datos de temperatura vía **Wi-Fi UDP Zero-Config**).
* **Software de PC Integrado (Plug & Play):** Aplicación de escritorio moderna y bilingüe para configurar todo visualmente.

---

## 2. Hardware Utilizado (Lista de Materiales - BOM)

Para ensamblar tu BindDeck, necesitarás los siguientes componentes económicos:

1. **Microcontrolador:** ESP32 (Se recomienda el modelo ESP32-WROOM-32 Dev Kit).
2. **Pantalla:** Pantalla OLED de 0.96 pulgadas I2C (Resolución 128x64, controlador SSD1306).
3. **Switches / Botones:** 8x Switches Mecánicos (Ej. **Outemu Red** por su tacto suave y silencioso).
4. **Control Analógico:** 1x Potenciómetro Lineal B10K (10 kOhmios).
5. **Carcasa:** Imprimible en 3D (disponible en Makerworld).
6. **Cableado:** Cables Dupont para las conexiones (o PCB dedicada).
7. **Extras:** Keycaps (teclas) y el knob para el potenciómetro.

---

## 3. Diagrama de Cableado y Ensamblaje

El cableado es directo. No necesitas instalar resistencias adicionales para los botones, ya que el software utiliza las resistencias internas (INPUT_PULLUP) del ESP32.

### Pantalla OLED (Comunicación I2C)
* **VCC:** Conectar a **3.3V** del ESP32.
* **GND:** Conectar a **GND** del ESP32.
* **SDA (Datos):** Conectar al **GPIO 21**.
* **SCL (Reloj):** Conectar al **GPIO 22**.

### Potenciómetro Analógico
* **Pin Izquierdo:** Conectar a **3.3V** del ESP32.
* **Pin Central (Señal):** Conectar al **GPIO 34**.
* **Pin Derecho:** Conectar a **GND** del ESP32.

### Switches Mecánicos
Cada switch mecánico tiene dos patillas:
1. Una patilla de **TODOS** los switches debe ir puenteada y conectada a **GND (Tierra)**.
2. La patilla restante de cada switch se conecta a los pines del ESP32:
   * **Switch 1:** GPIO 13
   * **Switch 2:** GPIO 12
   * **Switch 3:** GPIO 14
   * **Switch 4:** GPIO 27
   * **Switch 5:** GPIO 26
   * **Switch 6:** GPIO 25
   * **Switch 7:** GPIO 33
   * **Switch 8:** GPIO 32

<div class="note">
<strong>Consejo de Ensamblaje:</strong> Puedes soldar o conectar en cadena con un mismo cable todas las patillas GND de los 8 switches y del potenciómetro, llevando un único cable al pin GND del ESP32.
</div>

---

## 4. Primeros Pasos y Configuración

1. **Instalación del Firmware:** Carga el código en tu ESP32 usando PlatformIO o graba el archivo firmware.bin precompilado.
2. **Conexión USB:** Conecta el BindDeck por USB a tu PC. Esto enciende el dispositivo y habilita la conexión Serial para la telemetría.
3. **Sincronización Bluetooth:** Ve a la configuración de Bluetooth de Windows y empareja el dispositivo. Aparecerá reconocido como un **teclado Bluetooth**.
4. **Abrir la Aplicación BindDeck:** Inicia el ejecutable en tu PC. La app detectará automáticamente el puerto USB (COM). Si el indicador superior derecho está en verde, ya estás conectado!
   * *Importante:* Ejecuta la app como **Administrador** la primera vez para que LibreHardwareMonitor pueda leer los sensores de temperatura.

---

## 5. Guía de Uso de la Aplicación (PC)

La aplicación tiene una interfaz virtual idéntica a tu hardware. Todo cambio que realices se envía al hardware al pulsar el botón de **Sincronizar Dispositivo** (icono azul de actualizar).

### Personalizar las Teclas (Macros)
Haz clic en cualquier tecla (SW1 a SW8) de la app para editarla:
* **Acción:**
  * `Programa`: Selecciona un archivo .exe para lanzarlo.
  * `Multimedia`: Play/Pausa, Siguiente, Mute, etc.
  * `Atajo`: Combinaciones de teclas (Ctrl + C, Alt + Tab).
  * `Texto`: Escribe frases o párrafos enteros automáticamente.
* **Etiqueta:** El texto corto (max 8-10 caracteres) que se mostrará en la pantalla OLED.
* **Animación OLED:** Selecciona el icono (Check, Rayo, Corazón, etc.) que aparecerá al pulsar.

### Configurar el Potenciómetro
Selecciona el modo de funcionamiento del dial desde el panel derecho (encMode):
* `Volumen`: Controla el volumen maestro de Windows.
* `Zoom`: Amplía o reduce en navegadores (Ctrl +/-).
* `Pestañas`: Cambia rápidamente entre pestañas.
* `Deshacer / Rehacer`: Control de edición.

<div class="note">
<strong>Rastreo Dinámico:</strong> El potenciómetro se auto-calibra. Si notas que le falta recorrido, gíralo a los topes extremos una vez después de encenderlo. El chip aprenderá sus límites automáticamente.
</div>

### Brillo y Modo Reposo
Ajusta el **Brillo OLED** desde el panel de control. Si no usas el teclado durante 20 segundos, la pantalla pasará al modo de **Telemetría / Reposo** para proteger el panel OLED y mostrar los datos del PC.

---

## 6. Solución de Problemas Frecuentes

* **El indicador de la app está en rojo (Desconectado):**
  * Asegúrate de usar un cable USB de **datos** (no solo de carga).
  * Cierra otros programas que puedan ocupar el puerto COM (ej. Arduino IDE o Cura).
* **Pulso un botón y no ocurre nada:**
  * Comprueba que BindDeck esté conectado por **Bluetooth**. El cable USB envía la configuración y datos de pantalla, pero las pulsaciones de teclado se envían mediante Bluetooth para mayor compatibilidad y menor latencia en juegos.
* **Las temperaturas de CPU/GPU marcan 0 o no se leen:**
  * La aplicación debe tener permisos de **Administrador** en Windows para acceder a los sensores del sistema.
* **El volumen salta de forma errática:**
  * Gira el potenciómetro de un extremo al otro (de 0 a 100). El algoritmo de calibración ajustará los márgenes internos inmediatamente.

---

<div class="center">
  <p><em>Gracias por descargar y montar BindDeck.</em></p>
  <p>Si este proyecto te ha gustado, considera apoyar al creador <strong>@SanX18</strong>.</p>
</div>
