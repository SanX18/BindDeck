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
