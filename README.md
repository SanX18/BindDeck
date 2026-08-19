<div align="center">
  
  # Macro Deck Companion for ESP32
  
  **Un controlador macro programable open-source y personalizable, potenciado por ESP32 y una intuitiva App de PC.**

  [![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23ea4aaa?style=flat&logo=github)](https://github.com/sponsors/SanX18)
  [![PlatformIO](https://img.shields.io/badge/PlatformIO-Compatible-orange?logo=platformio)](https://platformio.org/)
  [![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
</div>

---

## 🌟 Sobre el Proyecto

**Macro Deck** es un ecosistema completo (Hardware + Software) diseñado para la comunidad Maker. Convierte un simple microcontrolador ESP32 en un potente teclado de macros personalizado con una pantalla OLED interactiva.

Ya seas streamer, programador, editor de vídeo o simplemente busques atajos rápidos para tu día a día, Macro Deck te permite lanzar aplicaciones, ejecutar atajos complejos y controlar el volumen de tu equipo, todo mientras visualizas divertidas y elegantes animaciones en su pantalla.

Este proyecto es ideal para acompañar carcasas impresas en 3D (disponibles en MakerWorld) y crear tu propio teclado auxiliar por una fracción del coste de opciones comerciales.

---

## ✨ Características Principales

*   🚀 **8 Botones Totalmente Personalizables:** Asigna atajos de teclado (ej: `CTRL+SHIFT+S`), lanza programas (`calc.exe`, `spotify.exe`), o simplemente escribe bloques de texto completos con un clic.
*   🎛️ **Potenciómetro Analógico:** Controla el volumen general del sistema operativo, zoom, deshacer/rehacer o pestañas, con un algoritmo de auto-calibración dinámica instantánea.
*   📺 **Pantalla OLED Interactiva:** Animaciones en tiempo real y **Monitor de Recursos del PC** (Temperaturas y Carga de CPU/GPU en tiempo real).
*   🔄 **Sincronización App-Hardware:** Las animaciones y estados se reflejan a la vez en la pantalla física y en la aplicación de escritorio.
*   🏷️ **Textos Personalizados:** Define qué texto quieres que aparezca en la pantalla OLED para cada uno de los botones de manera individual.
*   💻 **Aplicación de Escritorio (Windows):** Una interfaz gráfica limpia, moderna (Modo Claro/Oscuro) y en dos idiomas (Español/Inglés) que se ejecuta en la bandeja del sistema.
*   🔄 **Actualizaciones OTA:** Actualiza el firmware de tu ESP32 cómodamente por USB con un solo clic desde la propia aplicación.

---

## 🛠️ Hardware Necesario

Para construir tu propio Macro Deck necesitarás:

1.  **Microcontrolador ESP32** (Preferiblemente ESP32-WROOM-32 Dev Kit)
2.  **Pantalla OLED 0.96"** I2C (128x64, SSD1306)
3.  **8x Pulsadores Mecánicos** (Cualquier switch tipo Cherry MX o similar)
4.  **1x Potenciómetro Analógico** (Recomendado Lineal de 10k)
5.  **Cables Dupont** o PCB personalizada.
6.  **Carcasa impresa en 3D** (Encuentra mis diseños en [MakerWorld](https://makerworld.com/es/@SanX18))

### Esquema de Conexiones Básico
*   **OLED:** SDA -> GPIO 21 | SCL -> GPIO 22
*   **Potenciómetro:** Pin central (Señal) -> GPIO 34 | Extremos -> 3.3V y GND
*   **Botones (SW1 a SW8):** Pines 13, 12, 14, 27, 26, 25, 33, 32 (Conectados a GND, usando `INPUT_PULLUP` interno).

---

## 💻 Instalación y Uso

El proyecto consta de dos partes: el **Firmware** (lo que va en la placa) y el **Software** (la app para tu PC).

### 1. Firmware (ESP32)
1. Clona este repositorio y ábrelo usando **VSCode + PlatformIO**.
2. Conecta tu ESP32 por USB.
3. Compila y sube el código usando PlatformIO (`Upload`). Las librerías necesarias (`BleKeyboard`, `Adafruit GFX`, etc.) se descargarán automáticamente.

### 2. Software (PC App)
La aplicación está escrita en Python utilizando Flask y PyWebView.
1. Navega a la carpeta `pc_script/`.
2. Instala las dependencias: `pip install -r requirements.txt` (Asegúrate de instalar dependencias típicas como `flask`, `pywebview`, `pyserial`, `keyboard`, `pycaw`).
3. Ejecuta la aplicación: `python pc_monitor.py`
4. Configura tus teclas, elige tus animaciones y ¡disfruta!

---

## 💖 Apoyo y Donaciones

El uso, modificación y distribución de este código es **completamente gratuito** para la comunidad. Se ha desarrollado invirtiendo mucho tiempo, café y pasión. 

Si este proyecto te ha sido útil, te ha inspirado o simplemente quieres invitarme a un café para apoyar el desarrollo continuo y futuros proyectos, puedes hacerlo a través de **GitHub Sponsors**:

👉 **[Apoyar el proyecto en GitHub Sponsors](https://github.com/sponsors/SanX18)**

---

## 📜 Privacidad y Licencia

*   **Privacidad Total:** La aplicación de PC funciona de manera 100% local. No recopila telemetría, no guarda contraseñas y no se conecta a servidores externos. Todo el tráfico ocurre entre tu PC y tu cable USB.
*   **Descargo de responsabilidad:** Este software y esquemas se distribuyen "tal cual" (AS IS). El creador no se hace responsable por daños al hardware derivados de un mal ensamblaje o configuración.

<p align="center">
  <i>Desarrollado por <strong>Marc Sancho Pastor (@SanX18)</strong> .</i>
</p>
