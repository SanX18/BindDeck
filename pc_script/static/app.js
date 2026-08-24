
let installedApps = [];
fetch('/api/installed_apps')
    .then(r => r.json())
    .then(apps => {
        installedApps = apps;
        
        // Populate encApp (Volume Mixer)
        
        // Populate actionValue presets if currently 'app'
        const actType = document.getElementById('actionType');
        if (actType && actType.value === 'app') {
            updateValuePresets();
        }
    })
    .catch(e => console.error(e));

// Override updateValuePresets to use our fetched list if actionType is 'app'
// First, check if updateValuePresets exists.

let config = {};
let currentKey = null;

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('testModeToggle');
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('test-mode-active');
            } else {
                document.body.classList.remove('test-mode-active');
            }
        });
    }
});

const i18n = {
    en: {
        app_title: "BindDeck",
        app_subtitle: "Control Center",
        device_connected: "Device Connected",
        device_disconnected: "Disconnected",
        device_settings: "Device Settings",
        oled_anim: "OLED Animation",
        anim_0: "Expanding Waves",
        anim_1: "Flash Notification",
        anim_2: "Minimal Text",
        anim_3: "Waves + Mic Mute",
        anim_default: "Default (from Device Settings)",
        oled_brightness: "OLED Brightness",
        enc_action: "Encoder Action",
        enc_0: "System Volume",
        enc_1: "Zoom (In/Out)",
        enc_2: "Browser Tabs (Prev/Next)",
        enc_3: "Undo / Redo",
        sync: "Sync to Device",
        sync_tooltip: "Send current configuration and colors to the device instantly.",
        control_deck: "BindDeck",
        select_key_hint: "Select a key to configure its action.",
        action: "Action",
        select_key_first: "Select a key first",
        press: "Press",
        hold: "Hold",
        action_type: "Action type",
        action_none: "Native Keyboard (F13-F20)",
        action_app: "Run Program or File",
        action_shortcut: "Complex Keyboard Shortcut",
        action_text: "Auto-Type Text",
        anim_on_press: "Animation on Press",
        value: "Action Configuration",
        value_hint: "Apps: path or name (calc.exe). Shortcuts: use + (CTRL+SHIFT+C).",
        custom_text: "On-Screen Custom Text",
        custom_text_hint: "Optional. Short text to display when button is pressed.",
        save_action: "Save",
        delete_action: "Delete",
        hw_leds: "My build has LED's",
        global_color: "Global Color",
        led_effect: "LED Effect",
        led_solid: "Solid Color",
        led_breath: "Breathing",
        led_rainbow: "Rainbow",
        led_wave: "Wave on Press",
        settings_title: "App Settings",
        theme: "Theme",
        dark: "Dark",
        light: "Light",
        language: "Language",
        startup: "Start with Windows",
        updates: "Updates",
        check_updates: "Check for Updates",
        close: "Close",
        save: "Save",
        about_title: "Acerca de / About",
        about_tab1: "Sobre la App / About the App",
        about_desc1: "<strong>BindDeck Companion for ESP32</strong><br>Version: 1.0.0<br>Developed with passion for the Maker community.<br><br>This software allows communication, profile assignment and macros with ESP32 based BindDeck devices.",
        about_tab2: "Privacy & Transparency",
        about_desc2: "<li style='margin-bottom: 0.5rem;'>This application runs completely locally on your machine.</li><li style='margin-bottom: 0.5rem;'>It DOES NOT collect, store or transmit keystrokes, passwords, telemetry or personal data to external servers.</li><li style='margin-bottom: 0.5rem;'>Communication is strictly limited to the local connection (USB/Serial/Bluetooth) between your computer and the connected ESP32 device.</li>",
        about_tab3: "Terms & Support",
        about_desc3: "<strong>Disclaimer:</strong><br>This software is provided \"AS IS\", without express or implied warranties of uninterrupted operation or universal hardware compatibility. The developer is not liable for hardware misconfiguration or damages.<br><br><strong>Support & Donations:</strong><br>This application is completely free. If you wish to support the project's maintenance, you can voluntarily do so via the <strong>Sponsor icon at the bottom of the main page</strong>. Donations are symbolic tokens of appreciation and do not constitute a purchase agreement or guaranteed technical support.",
        close_action: "When clicking X",
        close_ask: "Ask me every time",
        close_minimize: "Minimize to System Tray",
        close_quit: "Quit Application",
        close_title: "Close BindDeck?",
        close_desc: "Do you want to minimize the application to the system tray so your macros keep working, or quit entirely?",
        close_remember: "Remember my choice",
        close_minimize_btn: "Minimize to Tray",
        close_quit_btn: "Quit Entirely",
        close_cancel: "Cancel",
        test_mode: "Test Mode"
    },
    es: {
        app_title: "BindDeck",
        app_subtitle: "Centro de Control",
        device_connected: "Dispositivo Conectado",
        device_disconnected: "Desconectado",
        device_settings: "Ajustes del Dispositivo",
        oled_anim: "Animación OLED",
        anim_0: "Ondas Expansivas",
        anim_1: "Notificación Flash",
        anim_2: "Texto Minimalista",
        anim_3: "Ondas + Micrófono Mute",
        anim_default: "Por defecto (Ajustes)",
        oled_brightness: "Brillo OLED",
        enc_action: "Acción del Encoder",
        enc_0: "Volumen del Sistema",
        enc_1: "Hacer Zoom (+ / -)",
        enc_2: "Pestañas Navegador (Izq/Der)",
        enc_3: "Deshacer / Rehacer",
        sync: "Sincronizar",
        sync_tooltip: "Envía la configuración y colores actuales al dispositivo al instante.",
        control_deck: "BindDeck",
        select_key_hint: "Selecciona una tecla para configurarla.",
        action: "Acción",
        select_key_first: "Selecciona una tecla primero",
        press: "Pulsar",
        hold: "Mantener",
        action_type: "Tipo de acción",
        action_none: "Teclado Nativo (F13-F20)",
        action_app: "Ejecutar Programa o Archivo",
        action_shortcut: "Atajo de Teclado Múltiple",
        action_text: "Escribir Texto Automático",
        anim_on_press: "Animación al Pulsar",
        value: "Configuración de la Acción",
        value_hint: "Programas: ruta o nombre (ej. calc.exe). Atajos: unir con + (ej. CTRL+SHIFT+C).",
        custom_text: "Texto Personalizado en Pantalla",
        custom_text_hint: "Opcional. Texto breve a mostrar cuando se pulsa el botón.",
        save_action: "Guardar",
        delete_action: "Borrar",
        hw_leds: "Mi dispositivo tiene LED's",
        global_color: "Color Global",
        led_effect: "Efecto LED",
        led_solid: "Color Fijo",
        led_breath: "Respiración",
        led_rainbow: "Arcoíris",
        led_wave: "Onda al Pulsar",
        settings_title: "Ajustes de la App",
        theme: "Tema",
        dark: "Oscuro",
        light: "Claro",
        language: "Idioma",
        startup: "Iniciar con Windows",
        updates: "Actualizaciones",
        check_updates: "Comprobar Actualizaciones",
        close: "Cerrar",
        save: "Guardar",
        about_title: "Acerca de / About",
        about_tab1: "Sobre la App",
        about_desc1: "<strong>BindDeck Companion for ESP32</strong><br>Versión: 1.0.0<br>Desarrollado con pasión para la comunidad Maker.<br><br>Este software permite la comunicación, asignación de perfiles y macros con dispositivos BindDeck basados en microcontroladores ESP32.",
        about_tab2: "Privacidad y Transparencia",
        about_desc2: "<li style='margin-bottom: 0.5rem;'>Esta aplicación funciona de forma completamente local en tu equipo.</li><li style='margin-bottom: 0.5rem;'>NO recopila, almacena ni transmite pulsaciones de teclas, contraseñas, telemetría ni datos personales a servidores externos.</li><li style='margin-bottom: 0.5rem;'>La comunicación se limita exclusivamente a la conexión local (USB/Serial/Bluetooth) entre tu ordenador y el dispositivo ESP32 conectado.</li>",
        about_tab3: "Términos y Soporte",
        about_desc3: "<strong>Descargo de Responsabilidad (Disclaimer):</strong><br>Este software se distribuye \"tal cual\" (AS IS), sin garantías explícitas ni implícitas de funcionamiento ininterrumpido o compatibilidad universal con todos los entornos de hardware. El desarrollador no se hace responsable de configuraciones erróneas en el hardware o pérdidas derivadas de su uso.<br><br><strong>Apoyo y Donaciones:</strong><br>El uso de esta aplicación es completamente gratuito. Si deseas apoyar el mantenimiento del proyecto, puedes hacerlo de forma voluntaria a través del <strong>icono de Sponsor que hay al pie de la ventana principal</strong>. Las donaciones son muestras simbólicas de agradecimiento y no constituyen un contrato de compra-venta ni servicio de asistencia técnica garantizada.",
        close_action: "Al pulsar la X",
        close_ask: "Preguntarme cada vez",
        close_minimize: "Minimizar a la Bandeja (Fondo)",
        close_quit: "Cerrar Aplicación",
        close_title: "¿Cerrar BindDeck?",
        close_desc: "¿Deseas minimizar la aplicación a la bandeja del sistema para que tus macros sigan funcionando, o cerrarla completamente?",
        close_remember: "Recordar mi decisión",
        close_minimize_btn: "Minimizar a la Bandeja",
        close_quit_btn: "Cerrar Completamente",
        close_cancel: "Cancelar",
        test_mode: "Modo Prueba"
    }
};

function applyLanguage(lang) {
    const dict = i18n[lang] || i18n['en'];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });
    const syncBtn = document.getElementById('btn-sync-header');
    if (syncBtn && dict['sync_tooltip']) {
        syncBtn.title = dict['sync_tooltip'];
    }
}

function updatePresets(type) {
    const btnBrowse = document.getElementById('btn-browse');
    if (btnBrowse) {
        btnBrowse.style.display = (type === 'app') ? 'flex' : 'none';
    }
    
    const datalist = document.getElementById('valuePresets');
    if (!datalist) return;
    datalist.innerHTML = '';
    
    let presets = [];
    if (type === 'app') {
        presets = ['calc.exe', 'notepad.exe', 'explorer.exe', 'mspaint.exe', 'spotify.exe'];
    } else if (type === 'shortcut') {
        presets = ['ctrl+c', 'ctrl+v', 'ctrl+x', 'alt+tab', 'alt+f4', 'win+d', 'play/pause media', 'volume mute', 'next track'];
    } else if (type === 'text') {
        presets = ['Hello World', 'johndoe@email.com', 'npm run dev', 'git status'];
    }
    
    presets.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p;
        datalist.appendChild(opt);
    });
}

async function fetchConfig() {
    try {
        const res = await fetch('/api/config?t=' + new Date().getTime());
        config = await res.json();
        
        if (config.esp32) {
            document.getElementById('animMode').value = config.esp32.animMode || 0;
            document.getElementById('encMode').value = config.esp32.encMode || 0;

    if (document.getElementById('encMode')) {
        if (document.getElementById('encAppContainer')) document.getElementById('encAppContainer').style.display = (document.getElementById('encMode').value == 5) ? 'block' : 'none';
    }

            if (document.getElementById('encApp')) document.getElementById('encApp').value = config.esp32.encApp || '';

    const encModeSelect = document.getElementById('encMode');
    if (encModeSelect) {
        
        
    
    
    }

            if (config.esp32.brightness !== undefined) {
                const bVal = Math.round((config.esp32.brightness / 255) * 100);
                document.getElementById('oledBrightness').value = bVal;
                const valSpan = document.getElementById('brightness-val');
                if(valSpan) valSpan.innerText = bVal + '%';
            }
            if (config.esp32.hwLeds !== undefined) {
                document.getElementById('hwHasLeds').checked = config.esp32.hwLeds;
                document.getElementById('ledColorPicker').style.display = config.esp32.hwLeds ? 'flex' : 'none';
            }
            if (config.esp32.ledColor) {
                document.getElementById('globalLedColor').value = config.esp32.ledColor;
            }
            if (config.esp32.ledEffect !== undefined) {
                document.getElementById('ledEffect').value = config.esp32.ledEffect;
            }
        }
        
        try {
            const verRes = await fetch('/api/version');
            const verData = await verRes.json();
            const ver = verData.version;
            i18n.en.about_desc1 = i18n.en.about_desc1.replace(/1\.0\.0/g, ver);
            i18n.es.about_desc1 = i18n.es.about_desc1.replace(/1\.0\.0/g, ver);
            const elVer = document.getElementById('current-version-text');
            if (elVer) elVer.innerText = ver;
        } catch(e) {}
        
        if (config.app) {
            document.getElementById('appTheme').value = config.app.theme || 'dark';
            document.getElementById('appLang').value = config.app.lang || 'en';
            document.getElementById('appStartup').checked = config.app.startup || false;
            document.getElementById('closeMode').value = config.app.closeMode || 'ask';
            
            if (config.app.theme === 'light') document.body.classList.add('light-theme');
            applyLanguage(config.app.lang || 'en');
            
            if (config.app.tutorialSeen === undefined || config.app.tutorialSeen === false) {
                currentTutorialStep = 0;
                showTutorialStep(0);
            }
        }
        
        updateButtonLabels();
    } catch (e) {
        console.error("Error fetching config", e);
    }
}

function updateButtonLabels() {
    if (!config.keys) return;
    document.querySelectorAll('.keycap').forEach(btn => {
        const key = btn.getAttribute('data-key');
        const keyConf = config.keys[key];
        if (keyConf && keyConf.type !== 'none') {
            btn.classList.add('has-action');
        } else {
            btn.classList.remove('has-action');
        }
    });
}

function playOledPreview(animMode, localOnly = false) {
    if (!localOnly) fetch('/api/preview/' + animMode).catch(e => console.error(e));
    
    const idle = document.getElementById('oled-idle');
    const layer = document.getElementById('oled-anim-layer');
    if(!idle || !layer) return;
    
    idle.style.display = 'none';
    layer.style.display = 'flex';
    layer.className = 'oled-anim-layer'; 
    layer.innerHTML = '';
    
    if (animMode == 0) {
        layer.classList.add('preview-wave');
        layer.innerHTML = '<span>BTN</span>';
    } else if (animMode == 1) {
        layer.classList.add('preview-flash');
        layer.innerHTML = '<span style="color:black;">FLASH</span>';
    } else if (animMode == 2) {
        layer.classList.add('preview-text');
        layer.innerHTML = '<span>HIT</span>';
    } else if (animMode == 3) {
        layer.classList.add('preview-wave');
        layer.innerHTML = '<span style="color: #ef4444; font-weight: bold; background: black; padding: 2px 4px; border: 1px solid #ef4444; border-radius: 4px; z-index: 10;">MUTED</span>';
    }
    
    const duration = (animMode == 2) ? 800 : 800;
    
    setTimeout(() => {
        layer.style.display = 'none';
        idle.style.display = 'block';
    }, duration);
}

async function saveSettings(silent = false) {
    if (currentKey) {
        config.keys[currentKey] = {
            type: document.getElementById('actionType').value,
            value: document.getElementById('actionValue').value,
            anim: parseInt(document.getElementById('keyAnim').value),
            dispText: document.getElementById('dispText').value.substring(0, 15)
        };
    }
    
    if (!config.esp32) config.esp32 = {};
    config.esp32.animMode = parseInt(document.getElementById('animMode').value);
    config.esp32.encMode = parseInt(document.getElementById('encMode').value);
    if (document.getElementById('encApp')) config.esp32.encApp = document.getElementById('encApp').value;
    config.esp32.brightness = Math.round((parseInt(document.getElementById('oledBrightness').value) / 100) * 255);
    config.esp32.hwLeds = document.getElementById('hwHasLeds').checked;
    config.esp32.ledColor = document.getElementById('globalLedColor').value;
    config.esp32.ledEffect = parseInt(document.getElementById('ledEffect').value);

    if (!config.app) config.app = {};
    config.app.theme = document.getElementById('appTheme').value;
    config.app.lang = document.getElementById('appLang').value;
    config.app.startup = document.getElementById('appStartup').checked;
    config.app.closeMode = document.getElementById('closeMode').value;

    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        updateButtonLabels();
        
        if (!silent) {
            const saveBtn = document.getElementById('btn-save');
            if (saveBtn) {
                const originalText = saveBtn.innerText;
                saveBtn.innerText = "Saved";
                setTimeout(() => saveBtn.innerText = originalText, 1500);
            }
            const saveSettingsBtn = document.getElementById('btn-sync-header');
            if (saveSettingsBtn) {
                saveSettingsBtn.style.color = "#22c55e";
                setTimeout(() => saveSettingsBtn.style.color = "var(--text-main)", 1500);
            }
        }
    } catch (e) {
        alert("Error saving configuration.");
    }
}

// UI EVENTS

let previewVolume = 50;
let volHideTimeout;

function playOledVolume(delta) {
    previewVolume += delta * 5;
    if (previewVolume > 100) previewVolume = 100;
    if (previewVolume < 0) previewVolume = 0;

    const idle = document.getElementById('oled-idle');
    const layer = document.getElementById('oled-anim-layer');
    if(!idle || !layer) return;
    
    idle.style.display = 'none';
    layer.style.display = 'flex';
    layer.className = 'oled-anim-layer';
    
    layer.innerHTML = `<div style="width: 80%; text-align: center;">
        <div style="font-size: 10px; color: #fff; margin-bottom: 2px;">VOLUMEN</div>
        <div style="width: 100%; height: 10px; border: 1px solid #fff; border-radius: 2px; padding: 1px; box-sizing: border-box; display: flex; align-items: stretch;">
            <div style="width: ${previewVolume}%; background: #fff; transition: width 0.1s;"></div>
        </div>
    </div>`;

    clearTimeout(volHideTimeout);
    volHideTimeout = setTimeout(() => {
        layer.style.display = 'none';
        idle.style.display = 'block';
    }, 1500);
}

function simulateAction(id) {
    fetch('/api/simulate', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    }).catch(e => console.error(e));
}

function simulateCurrentKey() {
    if(!currentKey) return;
    const keyIndex = parseInt(currentKey) - 13;
    simulateAction(keyIndex);
}

document.querySelectorAll('.keycap').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (currentKey) {
            // Save the currently edited key before switching
            if (!config.keys) config.keys = {};
            config.keys[currentKey] = {
                type: document.getElementById('actionType').value,
                value: document.getElementById('actionValue').value,
                anim: parseInt(document.getElementById('keyAnim').value),
                dispText: document.getElementById('dispText').value.substring(0, 15)
            };
        }
        
        document.querySelectorAll('.keycap').forEach(b => b.classList.remove('active-edit'));
        btn.classList.add('active-edit');
        
        currentKey = btn.getAttribute('data-key');
        const keyConfig = config.keys[currentKey] || {type: 'none', value: '', anim: -1, dispText: ''};
        
        const panel = document.getElementById('config-panel');
        panel.style.opacity = '1';
        panel.style.pointerEvents = 'auto';
        
        const swNumber = btn.innerText.includes('SW') ? btn.innerText.split(' ')[1] : 'Encoder';
        const lang = document.getElementById('appLang').value || 'en';
        const prefix = (lang === 'es') ? 'Configuración Switch ' : 'Configuring Switch ';
        document.getElementById('panel-subtitle').innerText = `${prefix}${swNumber} (F${currentKey})`;
        
        document.getElementById('actionType').value = keyConfig.type;
        updatePresets(keyConfig.type);
        document.getElementById('actionValue').value = keyConfig.value;
        document.getElementById('dispText').value = keyConfig.dispText || '';
        document.getElementById('keyAnim').value = keyConfig.anim !== undefined ? keyConfig.anim : -1;
    });
});

document.getElementById('actionType').addEventListener('change', (e) => {
    updatePresets(e.target.value);
    const actIn = document.getElementById('actionValue');
    const actLst = document.getElementById('valueAcList');
    if (e.target.value === 'app' && actIn && actLst) {
        actIn.focus();
        updateAcList(actIn, actLst, 'action');
    } else if (actLst) {
        actLst.style.display = 'none';
    }
});

document.getElementById('btn-save').addEventListener('click', () => saveSettings(false));

document.getElementById('btn-browse').addEventListener('click', async () => {
    try {
        const res = await fetch('/api/browse');
        const data = await res.json();
        if (data.path) {
            document.getElementById('actionValue').value = data.path;
        }
    } catch (e) {
        console.error("Error browsing file:", e);
    }
});

document.getElementById('btn-delete').addEventListener('click', () => {
    if (!currentKey) return;
    
    document.getElementById('actionType').value = 'none';
    document.getElementById('actionValue').value = '';
    document.getElementById('keyAnim').value = '-1';
    
    saveSettings(true);
    
    const delBtn = document.getElementById('btn-delete');
    const originalText = delBtn.innerText;
    delBtn.innerText = i18n[document.getElementById('appLang').value || 'en'].delete_action + "...";
    setTimeout(() => delBtn.innerText = originalText, 1000);
});

document.getElementById('btn-sync-header').addEventListener('click', () => saveSettings(false));

// Panel Drag and Drop
const panels = document.querySelectorAll('.main-layout > .panel');
panels.forEach(panel => {
    const handle = panel.querySelector('.drag-handle');
    if(handle) {
        handle.addEventListener('mousedown', () => panel.setAttribute('draggable', 'true'));
        handle.addEventListener('mouseup', () => panel.removeAttribute('draggable'));
    }
    
    panel.addEventListener('dragstart', (e) => {
        panel.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });
    
    panel.addEventListener('dragend', () => {
        panel.classList.remove('dragging');
        panel.removeAttribute('draggable');
    });
});

const layout = document.querySelector('.main-layout');
layout.addEventListener('dragover', (e) => {
    e.preventDefault();
    const draggingPanel = document.querySelector('.dragging');
    if (!draggingPanel) return;
    
    const siblings = [...layout.querySelectorAll('.panel:not(.dragging)')];
    const nextSibling = siblings.find(sibling => {
        const box = sibling.getBoundingClientRect();
        const offset = e.clientX - box.left - box.width / 2;
        return offset < 0;
    });
    
    if (nextSibling) {
        layout.insertBefore(draggingPanel, nextSibling);
    } else {
        layout.appendChild(draggingPanel);
    }
});

document.getElementById('hwHasLeds').addEventListener('change', (e) => {
    document.getElementById('ledColorPicker').style.display = e.target.checked ? 'flex' : 'none';
    saveSettings(true);
});
document.getElementById('globalLedColor').addEventListener('change', (e) => {
    saveSettings(true);
});
document.getElementById('ledEffect').addEventListener('change', (e) => {
    saveSettings(true);
});

document.getElementById('animMode').addEventListener('change', (e) => {
    saveSettings(true);
    playOledPreview(e.target.value);
});

document.getElementById('oledBrightness').addEventListener('change', (e) => {
    saveSettings(true);
});

document.getElementById('keyAnim').addEventListener('change', (e) => {
    saveSettings(true);
    let val = e.target.value;
    if (val == -1) val = document.getElementById('animMode').value;
    playOledPreview(val);
});

// SETTINGS MODAL
document.getElementById('btn-open-settings').addEventListener('click', () => {
    document.getElementById('settings-modal').style.display = 'flex';
});
document.getElementById('btn-close-settings').addEventListener('click', () => {
    document.getElementById('settings-modal').style.display = 'none';
});
document.getElementById('btn-save-app-settings').addEventListener('click', () => {
    const theme = document.getElementById('appTheme').value;
    if(theme === 'light') document.body.classList.add('light-theme');
    else document.body.classList.remove('light-theme');
    
    applyLanguage(document.getElementById('appLang').value);
    
    saveSettings(true);
    document.getElementById('settings-modal').style.display = 'none';
});

// ABOUT MODAL
const knob = document.getElementById('encoder-knob');
let isDraggingKnob = false;
let currentRotation = 0;
let startY = 0;

knob.addEventListener('mousedown', (e) => {
    isDraggingKnob = true;
    startY = e.clientY;
    knob.style.cursor = 'grabbing';
});
window.addEventListener('mouseup', () => {
    if(isDraggingKnob) {
        isDraggingKnob = false;
        knob.style.cursor = 'grab';
    }
});
window.addEventListener('mousemove', (e) => {
    if (!isDraggingKnob) return;
    const diff = startY - e.clientY;
    if (Math.abs(diff) > 5) {
        currentRotation += diff > 0 ? 15 : -15;
        knob.style.transform = `rotate(${currentRotation}deg)`;
        simulateAction(-3); // Simulate giro
        playOledVolume(diff > 0 ? 1 : -1);
        startY = e.clientY; // Reset for continuous rotation
    }
});

document.getElementById('btn-open-about').addEventListener('click', () => {
    document.getElementById('about-modal').style.display = 'flex';
});
document.getElementById('btn-close-about').addEventListener('click', () => {
    document.getElementById('about-modal').style.display = 'none';
});

document.querySelectorAll('.about-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        document.querySelectorAll('.about-tab').forEach(t => {
            t.classList.remove('active');
            t.style.color = 'var(--text-muted)';
            t.style.borderBottomColor = 'transparent';
            t.style.fontWeight = 'normal';
        });
        e.target.classList.add('active');
        e.target.style.color = 'var(--primary)';
        e.target.style.borderBottomColor = 'var(--primary)';
        e.target.style.fontWeight = 'bold';
        
        document.querySelectorAll('.about-content').forEach(c => c.style.display = 'none');
        document.getElementById('about-content-' + e.target.getAttribute('data-tab')).style.display = 'block';
    });
});

document.getElementById('btn-check-updates').addEventListener('click', async () => {
    const btn = document.getElementById('btn-check-updates');
    const originalText = btn.innerText;
    btn.innerText = "...";
    btn.disabled = true;
    
    try {
        const res = await fetch('/api/force_update_check', { method: 'POST' });
        const data = await res.json();
        
        if (data.available) {
            document.getElementById('update-banner').style.display = 'block';
            document.getElementById('update-version').innerText = data.version;
            alert((document.getElementById('appLang').value === 'es') ? "¡Hay una nueva versión disponible!" : "New version available!");
        } else {
            alert((document.getElementById('appLang').value === 'es') ? "Ya tienes la última versión instalada." : "You are on the latest version.");
        }
    } catch(e) {
        alert("Error de conexión");
    }
    
    btn.innerText = originalText;
    btn.disabled = false;
});

setInterval(async () => {
    try {
        const res = await fetch('/api/status?t=' + new Date().getTime());
        const data = await res.json();
        
        // WiFi Status
        fetch('/api/get_wifi_status').then(r => r.json()).then(wifi => {
            const wifiSpan = document.getElementById('wifiStatusText');
            if(wifiSpan) {
                if(wifi.connected) {
                    wifiSpan.innerText = `Conectado a ${wifi.ssid} (${wifi.ip})`;
                    wifiSpan.style.color = '#4ade80';
                } else {
                    wifiSpan.innerText = `Desconectado`;
                    wifiSpan.style.color = 'var(--text-muted)';
                }
            }
        }).catch(e => {});
        
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');
        const pingText = document.getElementById('ping-text');
        const lang = document.getElementById('appLang').value || 'en';
        
        if (data.connected) {
            dot.style.background = '#22c55e';
            dot.style.boxShadow = '0 0 8px #22c55e';
            let ctext = i18n[lang].device_connected;
            
            let iconHtml = '';
            let batHtml = '';
            if (data.type === 'USB') {
                iconHtml = '<svg style="margin-left:5px; vertical-align:middle;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 2v7.31"/><path d="M14 9.3V1.99"/><path d="M10 15v4.5a2.5 2.5 0 0 0 5 0V15"/><rect x="8" y="9" width="8" height="6" rx="1"/></svg>';
            } else if (data.type === 'Bluetooth') {
                iconHtml = '<svg style="margin-left:5px; vertical-align:middle;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6.5 6.5 11 11L12 23V1l5.5 5.5-11 11"/></svg>';
                if (data.battery !== null && data.battery !== undefined) {
                    batHtml = `<span style="font-size:12px; color:#aaa; margin-left:8px; vertical-align:middle;">🔋 ${data.battery}%</span>`;
                }
            }
            text.innerHTML = ctext + iconHtml + batHtml;
            
            if (pingText) {
                pingText.style.display = 'inline';
                pingText.innerText = `(${data.ping}ms)`;
            }
        } else {
            dot.style.background = '#ef4444';
            dot.style.boxShadow = '0 0 8px #ef4444';
            text.innerText = i18n[lang].device_disconnected;
            if (pingText) pingText.style.display = 'none';
        }
    } catch(e) {}
}, 2000);

fetchConfig();

// OTA Updater logic
setInterval(async () => {
    try {
        const res = await fetch('/api/update_check');
        const data = await res.json();
        if (data.available) {
            document.getElementById('update-banner').style.display = 'block';
            document.getElementById('update-version').innerText = data.version;
        }
    } catch(e) {}
}, 60000); // Check UI every 60s

async function startUpdate() {
    const lang = document.getElementById('appLang').value || 'en';
    const msg = (lang === 'es') ? "¿Seguro que quieres actualizar? El dispositivo se reiniciará." : "Are you sure you want to update? Device will restart.";
    if(!confirm(msg)) return;
    
    const banner = document.getElementById('update-banner');
    banner.innerHTML = (lang === 'es') ? "Actualizando... NO DESCONECTES EL CABLE. Revisa la pantalla del dispositivo." : "Updating... DO NOT DISCONNECT. Check device screen.";
    
    try {
        const res = await fetch('/api/do_update', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert((lang === 'es') ? "¡Actualización completada con éxito!" : "Update successful!");
            banner.style.display = 'none';
        } else {
            alert("Error: " + data.error);
            banner.style.display = 'none';
        }
    } catch(e) {
        alert("Network error.");
    }
}

// CLOSE MODAL LOGIC
window.showCloseModal = function() {
    document.getElementById('close-modal').style.display = 'flex';
};

document.getElementById('btn-close-cancel').addEventListener('click', () => {
    document.getElementById('close-modal').style.display = 'none';
});

document.getElementById('btn-close-minimize').addEventListener('click', async () => {
    document.getElementById('close-modal').style.display = 'none';
    if (document.getElementById('closeRemember').checked) {
        document.getElementById('closeMode').value = 'minimize';
        await saveSettings(true);
    }
    fetch('/api/window/minimize', { method: 'POST' });
});

document.getElementById('btn-close-quit').addEventListener('click', async () => {
    document.getElementById('close-modal').style.display = 'none';
    if (document.getElementById('closeRemember').checked) {
        document.getElementById('closeMode').value = 'quit';
        await saveSettings(true);
    }
    fetch('/api/window/quit', { method: 'POST' });
});

function flashFirmware() {
    const btn = document.getElementById('btn-flash-firmware');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span data-i18n="flashing">Instalando...</span>';
    btn.disabled = true;
    
    fetch('/api/flash', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            alert("Firmware instalado correctamente!");
        } else {
            alert("Error instalando firmware: " + data.error);
        }
    })
    .catch(e => {
        alert("Error de conexion: " + e);
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}


// TUTORIAL LOGIC
const tutorialSteps = [
    {
        title: "¡Bienvenido a BindDeck!",
        text: "Vamos a darte un rápido paseo para que descubras todo lo que puedes hacer con tu dispositivo."
    },
    {
        title: "Primer Paso: Instalar Firmware",
        text: "Para que el ESP32 funcione con la configuración de BindDeck, el primer paso indispensable es <strong>instalar el firmware</strong> utilizando el panel correspondiente de instalación."
    },
    {
        title: "Ajustes del Dispositivo",
        text: "En el panel de la izquierda puedes conectar tu ESP32, ya sea por USB, Bluetooth o Wi-Fi, y cambiar el comportamiento de los LEDs y la pantalla OLED."
    },
    {
        title: "Configuración de Teclas",
        text: "En el panel de la derecha (Acción) puedes asignar atajos de teclado, abrir programas y cambiar las animaciones de cada tecla por separado."
    },
    {
        title: "Sincronizar Cambios",
        text: "Recuerda que <strong>tras cada cambio</strong> que realices en la configuración, debes pulsar el botón superior de <strong>Sincronizar Dispositivo</strong> para aplicarlos al ESP32."
    },
    {
        title: "Modo Prueba",
        text: "Arriba tienes el Modo Prueba. Si lo activas, puedes hacer clic en los botones de la pantalla virtual y arrastrar la rueda para simular su comportamiento en tiempo real."
    },
    {
        title: "¡Gracias por usar BindDeck!",
        text: "Te agradecemos mucho que hayas descargado nuestra app. Si deseas apoyar el proyecto, puedes hacerlo a través de <a href='https://github.com/sponsors/SanX18' target='_blank' style='color: var(--primary); text-decoration: underline;'>GitHub Sponsors</a>, o mediante el botón que encontrarás abajo en el pie de la aplicación."
    }
];

let currentTutorialStep = 0;

function showTutorialStep(step) {
    document.getElementById('tutorial-modal').style.display = 'flex';
    document.getElementById('tut-title').innerText = tutorialSteps[step].title;
    document.getElementById('tut-text').innerHTML = tutorialSteps[step].text;
    document.getElementById('tut-progress').innerText = (step + 1) + " / " + tutorialSteps.length;
    
    if (step === tutorialSteps.length - 1) {
        document.getElementById('tut-btn-next').innerText = "Finalizar";
    } else {
        document.getElementById('tut-btn-next').innerText = "Siguiente";
    }
}

function nextTutorialStep() {
    currentTutorialStep++;
    if (currentTutorialStep >= tutorialSteps.length) {
        closeTutorial();
    } else {
        showTutorialStep(currentTutorialStep);
    }
}

function closeTutorial() {
    document.getElementById('tutorial-modal').style.display = 'none';
    if (!config.app) config.app = {};
    config.app.tutorialSeen = true;
    try {
        fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
    } catch(e) {}
}

// Auto-show tutorial on first run
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('tut-btn-next').addEventListener('click', nextTutorialStep);
    document.getElementById('tut-btn-skip').addEventListener('click', closeTutorial);

    document.getElementById('btn-tutorial-header').addEventListener('click', () => {
        currentTutorialStep = 0;
        showTutorialStep(0);
    });


});

function saveWifiConfig() {
    const ssid = document.getElementById('wifiSSID').value;
    const pwd = document.getElementById('wifiPass').value;
    if (!ssid) return;
    
    fetch('/api/send_config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cmd: `CFG:WIFI:${ssid}|${pwd}\n`})
    }).then(res => {
        if(res.ok) alert("Configuración Wi-Fi enviada al dispositivo. Se reiniciará la conexión Wi-Fi.");
    });
}

function toggleCustomAnim() {
    const animMode = document.getElementById('animMode').value;
    const container = document.getElementById('customAnimContainer');
    if(animMode == "4") {
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

function uploadCustomAnim() {
    const fileInput = document.getElementById('customAnimFile');
    const status = document.getElementById('customAnimStatus');
    
    if (fileInput.files.length === 0) return;
    
    const file = fileInput.files[0];
    status.innerText = "Subiendo " + file.name + "...";
    status.style.color = "var(--text-main)";
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload_anim', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            status.innerText = "Animacion guardada!";
            status.style.color = "var(--primary)";
        } else {
            status.innerText = "Error: " + data.error;
            status.style.color = "red";
        }
    })
    .catch(err => {
        status.innerText = "Error de conexion.";
        status.style.color = "red";
    });
}





document.getElementById('encMode').addEventListener('change', (e) => {
    const val = e.target.value;
    if (document.getElementById('encAppContainer')) document.getElementById('encAppContainer').style.display = (val == 5) ? 'block' : 'none';
});


function buildAcList(inputEl, listEl, type) {
    inputEl.addEventListener('focus', () => updateAcList(inputEl, listEl, type));
    inputEl.addEventListener('click', () => updateAcList(inputEl, listEl, type));
    inputEl.addEventListener('input', () => updateAcList(inputEl, listEl, type));

    document.addEventListener('click', (e) => {
        if (!inputEl.contains(e.target) && !listEl.contains(e.target)) listEl.style.display = 'none';
    });
    window.addEventListener('scroll', (e) => {
        if (e.target === listEl || listEl.contains(e.target)) return;
        if (listEl.style.display === 'block') {
            const rect = inputEl.getBoundingClientRect();
            listEl.style.top = rect.bottom + 'px';
            listEl.style.left = rect.left + 'px';
            // Hide if it goes off screen
            if (rect.bottom < 0 || rect.top > window.innerHeight || rect.width === 0) {
                listEl.style.display = 'none';
            }
        }
    }, true);

}
async function updateAcList(inputEl, listEl, type) {
    if (type === 'action' && document.getElementById('actionType').value !== 'app') {
        listEl.style.display = 'none';
        return;
    }
    
    let sourceApps = installedApps;
    if (type === 'enc') {
        try {
            const res = await fetch('/api/audio_apps');
            sourceApps = await res.json();
        } catch (e) {
            sourceApps = [];
        }
    }
    
    if (!sourceApps.length) {
        listEl.style.display = 'none';
        return;
    }
    
    const q = inputEl.value.toLowerCase();
    const filtered = sourceApps.filter(a => a.name.toLowerCase().includes(q) || a.exe.toLowerCase().includes(q));
    listEl.innerHTML = '';
    if (filtered.length === 0) { listEl.style.display = 'none'; return; }
    
    filtered.forEach(a => {
        const item = document.createElement('div');
        item.className = 'ac-item';
        
        const img = document.createElement('img');
        img.src = a.icon || 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><rect width="24" height="24" fill="%23444"/></svg>';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'ac-text';
        const nameDiv = document.createElement('div'); nameDiv.className = 'ac-name'; nameDiv.innerText = a.name;
        const pathDiv = document.createElement('div'); pathDiv.className = 'ac-path'; pathDiv.innerText = type === 'enc' ? a.exe : a.path;
        
        textDiv.appendChild(nameDiv); textDiv.appendChild(pathDiv);
        item.appendChild(img); item.appendChild(textDiv);
        
        item.addEventListener('click', () => {
            inputEl.value = type === 'enc' ? a.exe : a.path;
            listEl.style.display = 'none';
            // trigger save
            if (type === 'enc') {
                config.esp32.encApp = a.exe;
                saveSettings();
            } else {
                config.keys[currentKey].value = a.path;
                saveSettings();
            }
        });
        listEl.appendChild(item);
    });
        listEl.style.display = 'block';
    const rect = inputEl.getBoundingClientRect();
    listEl.style.position = 'fixed';
    listEl.style.top = rect.bottom + 'px';
    listEl.style.left = rect.left + 'px';
    listEl.style.width = rect.width + 'px';

}

setTimeout(() => {
    const encIn = document.getElementById('encApp');
    const encLst = document.getElementById('encAppAcList');
    if (encIn && encLst) buildAcList(encIn, encLst, 'enc');
    
    const actIn = document.getElementById('actionValue');
    const actLst = document.getElementById('valueAcList');
    if (actIn && actLst) buildAcList(actIn, actLst, 'action');
}, 1000);

let brtTimeout;
document.getElementById('oledBrightness').addEventListener('input', (e) => {
    const valSpan = document.getElementById('brightness-val');
    if (valSpan) valSpan.innerText = e.target.value + '%';
    clearTimeout(brtTimeout);
    brtTimeout = setTimeout(() => {
        saveSettings(true);
    }, 200); // Debounce real-time update
});

// Flash bundled firmware
const btnFlashBundled = document.getElementById('btn-flash-bundled');
if (btnFlashBundled) {
    btnFlashBundled.addEventListener('click', async () => {
        const lang = document.getElementById('appLang').value || 'en';
        if(!confirm(lang === 'es' ? '¿Seguro que quieres instalar el Firmware Oficial en el dispositivo conectado? Se borrará el anterior.' : 'Are you sure you want to install the Official Firmware? Device will be overwritten.')) return;
        
        const originalText = btnFlashBundled.innerText;
        btnFlashBundled.innerText = (lang === 'es') ? 'Instalando Firmware...' : 'Installing...';
        btnFlashBundled.disabled = true;
        
        try {
            const res = await fetch('/api/flash_bundled', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                alert(lang === 'es' ? '¡Firmware instalado con éxito! El dispositivo se está reiniciando.' : 'Firmware installed successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        } catch(err) {
            alert('Connection error');
        }
        
        btnFlashBundled.innerText = originalText;
        btnFlashBundled.disabled = false;
    });
}
