let config = {};
let currentKey = null;

async function fetchConfig() {
    try {
        const res = await fetch('/api/config');
        config = await res.json();
        
        if (config.esp32) {
            document.getElementById('animMode').value = config.esp32.animMode || 0;
            document.getElementById('encMode').value = config.esp32.encMode || 0;
        }
        
        updateButtonLabels();
    } catch (e) {
        console.error("Error fetching config", e);
    }
}

function updateButtonLabels() {
    if (!config.keys) return;
    document.querySelectorAll('.macro-key').forEach(btn => {
        const key = btn.getAttribute('data-key');
        const keyConf = config.keys[key];
        if (keyConf && keyConf.type !== 'none') {
            btn.style.borderLeft = "4px solid var(--accent)";
        } else {
            btn.style.borderLeft = "1px solid var(--border)";
        }
    });
}

async function saveConfig() {
    if (currentKey) {
        config.keys[currentKey] = {
            type: document.getElementById('actionType').value,
            value: document.getElementById('actionValue').value
        };
    }
    
    if (!config.esp32) config.esp32 = {};
    config.esp32.animMode = parseInt(document.getElementById('animMode').value);
    config.esp32.encMode = parseInt(document.getElementById('encMode').value);

    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        updateButtonLabels();
        
        const saveBtn = document.getElementById('btn-save');
        const originalText = saveBtn.innerText;
        saveBtn.innerText = "¡Guardado!";
        saveBtn.style.background = "#22c55e"; 
        setTimeout(() => {
            saveBtn.innerText = originalText;
            saveBtn.style.background = "";
        }, 1500);
        
    } catch (e) {
        alert("Error al guardar la configuración.");
    }
}

document.querySelectorAll('.macro-key').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.macro-key').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        currentKey = e.target.getAttribute('data-key');
        const keyConfig = config.keys[currentKey] || {type: 'none', value: ''};
        
        document.getElementById('config-panel').style.display = 'block';
        
        document.getElementById('actionType').value = keyConfig.type;
        document.getElementById('actionValue').value = keyConfig.value;
    });
});

document.getElementById('btn-save').addEventListener('click', saveConfig);
document.getElementById('animMode').addEventListener('change', saveConfig);
document.getElementById('encMode').addEventListener('change', saveConfig);

fetchConfig();
