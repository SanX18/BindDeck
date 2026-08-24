<div align="center">
  
  # BindDeck Companion for ESP32
  
  **Un controlador macro programable open-source y personalizable, potenciado por ESP32 y una intuitiva App de PC.**

  [![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23ea4aaa?style=flat&logo=github)](https://github.com/sponsors/SanX18)
  [![Buy me a coffe](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23ea4aaa?style=flat&logo=buymeacoffe)](buymeacoffee.com/sanx18)
  [![PlatformIO](https://img.shields.io/badge/PlatformIO-Compatible-orange?logo=platformio)](https://platformio.org/)
  [![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
</div>

---


**BindDeck** es un ecosistema completo de hardware y software diseñado para potenciar tu productividad y tu setup. Convierte un simple microcontrolador ESP32 en un potente teclado de macros personalizado, equipado con una pantalla OLED interactiva, un control analógico y botones mecánicos. Es el accesorio ideal para streamers, programadores, editores de vídeo y cualquier entusiasta de la tecnología.

## 🚀 ¿Qué hace la aplicación?

BindDeck no es solo un teclado de atajos; es una herramienta interactiva. Todo lo que ves en la pantalla de tu PC se sincroniza al instante con tu dispositivo físico:

*   **Lanzador y Atajos (8 Botones):** Asigna combinaciones complejas de teclado (ej. `CTRL+SHIFT+S`), lanza tus programas favoritos (`calc.exe`, `spotify.exe`) o ejecuta bloques enteros de texto con una sola pulsación.
*   **Control Analógico Inteligente:** Incorpora un potenciómetro con un algoritmo de auto-calibración dinámica. Úsalo para ajustar el volumen general de tu sistema operativo, hacer zoom, navegar por pestañas o usar el deshacer/rehacer.
*   **Monitor de Hardware en Tiempo Real:** Su pantalla OLED no solo muestra simpáticas animaciones cuando pulsas los botones; cuando está en reposo actúa como un monitor de telemetría, mostrando las temperaturas y la carga (uso) de tu CPU y GPU en tiempo real.
*   **Textos Personalizables:** A través de la app, puedes escribir qué texto quieres que aparezca en la pantalla OLED de manera individual para cada uno de los 8 botones.
*   **Conectividad Dual Híbrida (Cable o Inalámbrico):** Puedes usarlo clásicamente por cable USB, o de manera **100% Inalámbrica**. Envía tus macros al PC usando **Bluetooth LE** (para un bajo consumo de batería) y recibe los datos de las temperaturas del PC vía **Wi-Fi UDP Zero-Config**.
*   **Software de PC Integrado (Plug & Play):** Cuenta con una moderna aplicación de escritorio para Windows (con Modo Claro/Oscuro y bilingüe Español/Inglés). Desde ella configuras todo visualmente y puedes hasta actualizar el firmware de tu ESP32 vía OTA (Over-The-Air) con un solo clic.

---

## 🛠️ Hardware Utilizado (BOM)

Para montar la electrónica de esta carcasa, necesitarás componentes muy económicos y accesibles.

1.  **Microcontrolador:** ESP32 (Se recomienda el modelo clásico ESP32-WROOM-32 Dev Kit).
2.  **Pantalla:** Pantalla OLED de 0.96" I2C (Resolución 128x64, con controlador SSD1306).
3.  **Switches / Botones:** 8x Switches Mecánicos. *(En este proyecto se han utilizado switches **Outemu Red**. Al ser lineales y silenciosos, ofrecen un tacto suave, rápido y perfecto para ejecutar macros sin el clásico "clic" ruidoso).*
4.  **Control Analógico:** 1x Potenciómetro Lineal B10K (10 kOhmios).
5.  **Cableado:** Cables Dupont para realizar las conexiones interiores (o una PCB si decides fabricarla).
6.  **Extras:** Keycaps (teclas) de tu elección para decorar los switches mecánicos.

---

## 🔌 Diagrama de Conexiones Físicas

El cableado es directo y sencillo. No necesitas instalar resistencias adicionales para los botones, ya que el código se encarga de activar las resistencias internas (`INPUT_PULLUP`) del ESP32.

### 📺 Pantalla OLED (Comunicación I2C)
*   **VCC:** Conectar a **3.3V** del ESP32.
*   **GND:** Conectar a **GND** del ESP32.
*   **SDA (Línea de Datos):** Conectar al **GPIO 21**.
*   **SCL (Línea de Reloj):** Conectar al **GPIO 22**.

### 🎛️ Potenciómetro Analógico
*   **Pin Izquierdo:** Conectar a **3.3V** del ESP32.
*   **Pin Central (Señal):** Conectar al **GPIO 34**.
*   **Pin Derecho:** Conectar a **GND** del ESP32.

### ⌨️ Switches Mecánicos (Outemu Red)
Cada switch mecánico tiene dos patillas. Una patilla de **todos los switches debe ir conectada a GND (Tierra)**. La patilla restante de cada switch se conecta a los siguientes pines del ESP32:
*   **Switch 1:** GPIO 13
*   **Switch 2:** GPIO 12
*   **Switch 3:** GPIO 14
*   **Switch 4:** GPIO 27
*   **Switch 5:** GPIO 26
*   **Switch 6:** GPIO 25
*   **Switch 7:** GPIO 33
*   **Switch 8:** GPIO 32

*(💡 Consejo: Puedes puentear o "cadenerar" con un mismo cable todas las patillas GND de los 8 switches y el potenciómetro para llevar un único cable al pin GND del ESP32).*

---

## 💻 Instrucciones Rápidas de Software

El proyecto se divide en el **Firmware** (lo que va en el ESP32) y la **App de PC**.

1.  Carga el código fuente en tu ESP32 (compatible con PlatformIO / VSCode). Toda la información está disponible en el repositorio de GitHub de *SanX18/BindDeck*.
2.  Abre la aplicación de escritorio `BindDeck.exe` en tu ordenador.
3.  **⚠️ Importante:** La primera vez que abras la App, te pedirá permisos de Administrador en Windows. **Debes aceptarlos**. Esto es obligatorio para que el motor integrado de hardware (*LibreHardwareMonitor*) tenga acceso de lectura a los sensores de temperatura de tu CPU y Gráfica para enviarlos a la pequeña pantalla OLED.
4.  Todo el tráfico es 100% privado y local. ¡Configura tus botones, personaliza tu experiencia y disfruta de tu propio macro pad inteligente!

---

## 💖 Apoyo y Donaciones

El uso, modificación y distribución de este código es **completamente gratuito** para la comunidad. Se ha desarrollado invirtiendo mucho tiempo, café y pasión. 

  Si este proyecto te ha sido útil, te ha inspirado o simplemente quieres invitarme a un café para apoyar el desarrollo continuo y futuros proyectos, puedes hacerlo a través de **GitHub Sponsors** o **BuyMeACoffe**:

👉 **[Apoyar el proyecto en GitHub Sponsors](https://github.com/sponsors/SanX18)**

👉 **[Apoyar el proyecto en ByMeACoffe]( https://www.buymeacoffee.com/sanx18)**

---

## 📜 Privacidad y Licencia

*   **Privacidad Total:** La aplicación de PC funciona de manera 100% local. No recopila telemetría, no guarda contraseñas y no se conecta a servidores externos. Todo el tráfico ocurre entre tu PC y tu cable USB.
*   **Descargo de responsabilidad:** Este software y esquemas se distribuyen "tal cual" (AS IS). El creador no se hace responsable por daños al hardware derivados de un mal ensamblaje o configuración.

<p align="center">
  <i>Desarrollado por <strong>Marc Sancho Pastor (@SanX18)</strong> .</i>
</p>
