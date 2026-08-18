let config = {};
let currentKey = null;

const i18n = {
    en: {
        app_title: "Macro Deck",
        app_subtitle: "Programmable Macro Controller",
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
        enc_1: "Scroll (Vertical)",
        enc_2: "Scroll (Horizontal)",
        sync: "Sync to Device",
        control_deck: "Macro Deck",
        select_key_hint: "Select a key to configure its action.",
        action: "Action",
        select_key_first: "Select a key first",
        press: "Press",
        hold: "Hold",
        action_type: "Action type",
        action_none: "No action (Passthrough)",
        action_app: "Open App / Executable",
        action_shortcut: "Keyboard Shortcut",
        action_text: "Write Text",
        anim_on_press: "Animation on Press",
        value: "Value",
        value_hint: "Shortcuts use + separators (CTRL+SHIFT+S). Write Text types raw text. Actions run on PC.",
        custom_text: "OLED Custom Text",
        custom_text_hint: "Optional. Leave empty to display default F13-F20.",
        save_action: "Save action",
        delete_action: "Delete",
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
        about_desc1: "<strong>MacroDeck Companion for ESP32</strong><br>Version: 1.0.0<br>Developed with passion for the Maker community.<br><br>This software allows communication, profile assignment and macros with ESP32 based macro deck devices.",
        about_tab2: "Privacy & Transparency",
        about_desc2: "<li style='margin-bottom: 0.5rem;'>This application runs completely locally on your machine.</li><li style='margin-bottom: 0.5rem;'>It DOES NOT collect, store or transmit keystrokes, passwords, telemetry or personal data to external servers.</li><li style='margin-bottom: 0.5rem;'>Communication is strictly limited to the local connection (USB/Serial/Bluetooth) between your computer and the connected ESP32 device.</li>",
        about_tab3: "Terms & Support",
        about_desc3: "<strong>Disclaimer:</strong><br>This software is provided \"AS IS\", without express or implied warranties of uninterrupted operation or universal hardware compatibility. The developer is not liable for hardware misconfiguration or damages.<br><br><strong>Support & Donations:</strong><br>This application is completely free. If you wish to support the project's maintenance, you can voluntarily do so via the <strong>Sponsor icon at the bottom of the main page</strong>. Donations are symbolic tokens of appreciation and do not constitute a purchase agreement or guaranteed technical support."
    },
    es: {
        app_title: "Macro Deck",
        app_subtitle: "Controlador Macro Programable",
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
        enc_1: "Scroll (Vertical)",
        enc_2: "Scroll (Horizontal)",
        sync: "Sincronizar",
        control_deck: "Macro Deck",
        select_key_hint: "Selecciona una tecla para configurarla.",
        action: "Acción",
        select_key_first: "Selecciona una tecla primero",
        press: "Pulsar",
        hold: "Mantener",
        action_type: "Tipo de acción",
        action_none: "Ninguna (Nativa)",
        action_app: "Abrir App / Ejecutable",
        action_shortcut: "Atajo de Teclado",
        action_text: "Escribir Texto",
        anim_on_press: "Animación al Pulsar",
        value: "Valor",
        value_hint: "Los atajos usan + (ej: CTRL+SHIFT+S). Escribir Texto redacta tal cual. Se ejecuta en el PC.",
        custom_text: "Texto OLED Personalizado",
        custom_text_hint: "Opcional. Si lo dejas vacío se mostrará F13-F20.",
        save_action: "Guardar acción",
        delete_action: "Borrar",
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
        about_desc1: "<strong>MacroDeck Companion for ESP32</strong><br>Versión: 1.0.0<br>Desarrollado con pasión para la comunidad Maker.<br><br>Este software permite la comunicación, asignación de perfiles y macros con dispositivos macro deck basados en microcontroladores ESP32.",
        about_tab2: "Privacidad y Transparencia",
        about_desc2: "<li style='margin-bottom: 0.5rem;'>Esta aplicación funciona de forma completamente local en tu equipo.</li><li style='margin-bottom: 0.5rem;'>NO recopila, almacena ni transmite pulsaciones de teclas, contraseñas, telemetría ni datos personales a servidores externos.</li><li style='margin-bottom: 0.5rem;'>La comunicación se limita exclusivamente a la conexión local (USB/Serial/Bluetooth) entre tu ordenador y el dispositivo ESP32 conectado.</li>",
        about_tab3: "Términos y Soporte",
        about_desc3: "<strong>Descargo de Responsabilidad (Disclaimer):</strong><br>Este software se distribuye \"tal cual\" (AS IS), sin garantías explícitas ni implícitas de funcionamiento ininterrumpido o compatibilidad universal con todos los entornos de hardware. El desarrollador no se hace responsable de configuraciones erróneas en el hardware o pérdidas derivadas de su uso.<br><br><strong>Apoyo y Donaciones:</strong><br>El uso de esta aplicación es completamente gratuito. Si deseas apoyar el mantenimiento del proyecto, puedes hacerlo de forma voluntaria a través del <strong>icono de Sponsor que hay al pie de la ventana principal</strong>. Las donaciones son muestras simbólicas de agradecimiento y no constituyen un contrato de compra-venta ni servicio de asistencia técnica garantizada."
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
}

function updatePresets(type) {
    const datalist = document.getElementById('valuePresets');
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
            if (config.esp32.brightness !== undefined) {
                document.getElementById('oledBrightness').value = Math.round((config.esp32.brightness / 255) * 100);
            }
        }
        
        if (config.app) {
            document.getElementById('appTheme').value = config.app.theme || 'dark';
            document.getElementById('appLang').value = config.app.lang || 'en';
            document.getElementById('appStartup').checked = config.app.startup || false;
            
            if (config.app.theme === 'light') document.body.classList.add('light-theme');
            applyLanguage(config.app.lang || 'en');
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

function playOledPreview(animMode) {
    fetch('/api/preview/' + animMode).catch(e => console.error(e));
    
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
    config.esp32.brightness = Math.round((parseInt(document.getElementById('oledBrightness').value) / 100) * 255);

    if (!config.app) config.app = {};
    config.app.theme = document.getElementById('appTheme').value;
    config.app.lang = document.getElementById('appLang').value;
    config.app.startup = document.getElementById('appStartup').checked;

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
            const saveSettingsBtn = document.getElementById('btn-save-settings');
            if (saveSettingsBtn) {
                const originalText = saveSettingsBtn.innerText;
                saveSettingsBtn.innerText = "Synced!";
                setTimeout(() => saveSettingsBtn.innerText = originalText, 1500);
            }
        }
    } catch (e) {
        alert("Error saving configuration.");
    }
}

// UI EVENTS
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
        document.querySelectorAll('.keycap').forEach(b => b.classList.remove('active-edit'));
        e.target.classList.add('active-edit');
        
        currentKey = e.target.getAttribute('data-key');
        const keyConfig = config.keys[currentKey] || {type: 'none', value: '', anim: -1, dispText: ''};
        
        const panel = document.getElementById('config-panel');
        panel.style.opacity = '1';
        panel.style.pointerEvents = 'auto';
        
        const swNumber = e.target.innerText.split(' ')[1];
        document.getElementById('panel-subtitle').innerText = `Configuring SW ${swNumber} (Native F${currentKey})`;
        
        document.getElementById('actionType').value = keyConfig.type;
        updatePresets(keyConfig.type);
        document.getElementById('actionValue').value = keyConfig.value;
        document.getElementById('dispText').value = keyConfig.dispText || '';
        document.getElementById('keyAnim').value = keyConfig.anim !== undefined ? keyConfig.anim : -1;
    });
});

document.getElementById('actionType').addEventListener('change', (e) => updatePresets(e.target.value));

document.getElementById('btn-save').addEventListener('click', () => saveSettings(false));

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

document.getElementById('btn-save-settings').addEventListener('click', () => saveSettings(false));

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
document.getElementById('btn-open-about').addEventListener('click', () => {
    document.getElementById('about-modal').style.display = 'flex';
});
document.getElementById('btn-close-about').addEventListener('click', () => {
    document.getElementById('about-modal').style.display = 'none';
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
        
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');
        const lang = document.getElementById('appLang').value || 'en';
        
        if (data.connected) {
            dot.style.background = '#22c55e';
            dot.style.boxShadow = '0 0 8px #22c55e';
            text.innerText = i18n[lang].device_connected;
        } else {
            dot.style.background = '#ef4444';
            dot.style.boxShadow = '0 0 8px #ef4444';
            text.innerText = i18n[lang].device_disconnected;
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
