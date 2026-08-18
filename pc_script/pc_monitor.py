import time
import serial
import serial.tools.list_ports
import psutil
import requests
import threading
import json
import os
import sys
import keyboard
import webview
import socket
import urllib.request
import subprocess

# Monkeypatch subprocess.Popen para evitar ventanas CMD emergentes en Windows
import subprocess
import os

if os.name == 'nt':
    original_popen = subprocess.Popen
    class HiddenPopen(original_popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            super().__init__(*args, **kwargs)
    subprocess.Popen = HiddenPopen

import GPUtil
import random
from flask import Flask, render_template, request, jsonify

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
app = Flask(__name__, 
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))

# Save config next to the executable, not in the temp MEIPASS dir
if getattr(sys, 'frozen', False):
    CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), "macro_config.json")
else:
    CONFIG_FILE = os.path.join(base_path, "macro_config.json")

serial_port = None
config = {
    "keys": {str(i): {"type": "none", "value": "", "anim": -1} for i in range(13, 21)},
    "esp32": {"animMode": 0, "encMode": 0},
    "app": {"theme": "dark", "lang": "en", "startup": False, "closeMode": "ask"}
}

# --- OTA UPDATER ---
UPDATE_AVAILABLE = False
NEW_VERSION_URL = ""
NEW_VERSION_NAME = ""

# TODO: EL USUARIO DEBE CAMBIAR ESTO POR SU REPO REAL (Ej. "SanX18/MacroDeck")
GITHUB_REPO = "SanX18/MacroDeck"
CURRENT_VERSION = "v1.0.0"

def check_for_updates():
    global UPDATE_AVAILABLE, NEW_VERSION_URL, NEW_VERSION_NAME
    while True:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                if latest_version and latest_version != CURRENT_VERSION:
                    for asset in data.get("assets", []):
                        if asset.get("name") == "firmware.bin":
                            NEW_VERSION_URL = asset.get("browser_download_url")
                            NEW_VERSION_NAME = latest_version
                            UPDATE_AVAILABLE = True
                            break
        except Exception:
            pass
        time.sleep(86400) # Check once a day

threading.Thread(target=check_for_updates, daemon=True).start()

# --- CONFIG MANAGEMENT ---
def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception as e:
            print("Error cargando config:", e)

def manage_startup(enable):
    try:
        startup_path = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup", "MacroDeck.bat")
        if enable:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            cmd = f'start "" "{exe_path}"' if getattr(sys, 'frozen', False) else f'start "" pythonw "{exe_path}"'
            with open(startup_path, 'w') as f:
                f.write(f"@echo off\n{cmd}\n")
        else:
            if os.path.exists(startup_path):
                os.remove(startup_path)
    except Exception as e:
        print("Error en startup:", e)

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        manage_startup(config.get("app", {}).get("startup", False))
    except Exception as e:
        print("Error guardando config:", e)

# --- KEYBOARD HOOKS ---
def execute_macro(key_index):
    action = config["keys"].get(str(key_index), {})
    action_type = action.get("type", "none")
    value = action.get("value", "")
    
    if action_type == "app" and value:
        try:
            os.startfile(value)
        except Exception as e:
            print(f"Error abriendo app: {e}")
    elif action_type == "shortcut" and value:
        try:
            keyboard.send(value)
        except Exception as e:
            print(f"Error enviando atajo: {e}")
    elif action_type == "text" and value:
        try:
            keyboard.write(value)
        except Exception as e:
            print(f"Error escribiendo texto: {e}")

def on_key_event(e):
    if e.event_type == keyboard.KEY_DOWN:
        if e.name.startswith('f') and e.name[1:].isdigit():
            key_num = int(e.name[1:])
            if 13 <= key_num <= 20:
                action_type = config["keys"].get(str(key_num), {}).get("type", "none")
                if action_type != "none":
                    threading.Thread(target=execute_macro, args=(key_num,), daemon=True).start()
                    return False
    return True

# --- FLASK API ---

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')

def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config
    if request.method == 'POST':
        new_cfg = request.json
        config = new_cfg
        save_config()
        
        if serial_port and serial_port.is_open:
            try:
                anim = new_cfg.get("esp32", {}).get("animMode", 0)
                if anim is None: anim = 0
                enc = new_cfg.get("esp32", {}).get("encMode", 0)
                if enc is None: enc = 0
                brt = new_cfg.get("esp32", {}).get("brightness", 255)
                if brt is None: brt = 255
                
                serial_port.write(f"CFG:ANIM:{anim}\n".encode('utf-8'))
                time.sleep(0.05)
                serial_port.write(f"CFG:ENC:{enc}\n".encode('utf-8'))
                time.sleep(0.05)
                serial_port.write(f"CFG:BRT:{brt}\n".encode('utf-8'))
                time.sleep(0.05)
                
                kb_anims = []
                for i in range(13, 21):
                    # default anim for key is -1
                    key_anim = config["keys"].get(str(i), {}).get("anim", -1)
                    kb_anims.append(str(key_anim))
                kb_anims_str = ",".join(kb_anims)
                serial_port.write(f"CFG:KB_ANIM:{kb_anims_str}\n".encode('utf-8'))
                time.sleep(0.05)
                
                for i in range(13, 21):
                    disp_text = config["keys"].get(str(i), {}).get("dispText", "")
                    idx = i - 13
                    serial_port.write(f"CFG:TXT:{idx}:{disp_text}\n".encode('utf-8'))
                    time.sleep(0.05)
                
            except Exception as e:
                print("Error enviando config al ESP32:", e)
                
        return jsonify({"status": "success"})
    return jsonify(config)

@app.route('/api/preview/<int:anim_id>')
def api_preview(anim_id):
    if serial_port and serial_port.is_open:
        try:
            serial_port.write(f"CMD:PREVIEW:{anim_id}\n".encode('utf-8'))
        except:
            pass
    return jsonify({"status": "ok"})

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    if serial_port and serial_port.is_open:
        try:
            data = request.json
            val = int(data.get("id", 0))
            print(f"SIMULATING {val}")
            serial_port.write(f"CMD:SIMULATE:{val}\n".encode('utf-8'))
        except Exception as e:
            print(f"Error simulate: {e}")
            pass
    return jsonify({"status": "ok"})

SIMULATE_TEMP = False

@app.route('/api/simulate_temp', methods=['POST'])
def api_simulate_temp():
    global SIMULATE_TEMP
    SIMULATE_TEMP = not SIMULATE_TEMP
    return jsonify({"status": "ok", "simulate": SIMULATE_TEMP})

@app.route('/api/status')
def api_status():
    conn_type = config.get("app", {}).get("connection_type", "usb")
    is_connected = False
    ping = 0
    if conn_type == "wifi":
        is_connected = True # Assume true for UDP if configured
        ping = random.randint(30, 85)
    else:
        is_connected = serial_port is not None and serial_port.is_open
        if is_connected:
            ping = random.randint(8, 24)
            
    return jsonify({"connected": is_connected, "ping": ping})

@app.route('/api/window/minimize', methods=['POST'])
def api_minimize():
    for w in webview.windows:
        w.hide()
    return jsonify({"status": "ok"})

@app.route('/api/window/quit', methods=['POST'])
def api_quit():
    os._exit(0)
    return jsonify({"status": "ok"})

@app.route('/api/version')
def api_version():
    return jsonify({"version": CURRENT_VERSION})

@app.route('/api/update_check')
def api_update_check():
    return jsonify({"available": UPDATE_AVAILABLE, "version": NEW_VERSION_NAME})

@app.route('/api/force_update_check', methods=['POST'])
def api_force_update_check():
    global UPDATE_AVAILABLE, NEW_VERSION_URL, NEW_VERSION_NAME
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "")
            if latest_version and latest_version != CURRENT_VERSION:
                for asset in data.get("assets", []):
                    if asset.get("name") == "firmware.bin":
                        NEW_VERSION_URL = asset.get("browser_download_url")
                        NEW_VERSION_NAME = latest_version
                        UPDATE_AVAILABLE = True
                        return jsonify({"available": True, "version": latest_version})
        return jsonify({"available": False, "version": CURRENT_VERSION})
    except Exception as e:
        return jsonify({"available": False, "error": str(e)})

@app.route('/api/do_update', methods=['POST'])
def api_do_update():
    global serial_port
    if not UPDATE_AVAILABLE or not NEW_VERSION_URL:
        return jsonify({"success": False, "error": "No update available"})
        
    port_to_flash = find_esp32_port()
    if not port_to_flash:
        return jsonify({"success": False, "error": "Device not connected via USB"})
        
    if serial_port and serial_port.is_open:
        try:
            serial_port.write(b"CMD:UPDATE\n")
            time.sleep(0.5)
            serial_port.close()
            serial_port = None
        except:
            pass
            
    try:
        urllib.request.urlretrieve(NEW_VERSION_URL, "firmware_update.bin")
        cmd = [sys.executable, "-m", "esptool", "--port", port_to_flash, "--baud", "460800", "write_flash", "-z", "0x10000", "firmware_update.bin"]
        subprocess.run(cmd, check=True)
        if os.path.exists("firmware_update.bin"):
            os.remove("firmware_update.bin")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# --- ESP32 MONITOR ---
def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        if "ch340" in desc or "cp210" in desc or "serial" in desc or "bluetooth" in desc or "bth" in desc:
            return port.device
    return None

def get_lhm_cpu_temp():
    try:
        response = requests.get("http://127.0.0.1:8085/data.json", timeout=1)
        data = response.json()
        def find_temp(node, is_cpu=False):
            if isinstance(node, dict):
                if "cpu.png" in node.get("ImageURL", "") or "Intel" in node.get("Text", "") or "AMD" in node.get("Text", ""):
                    is_cpu = True
                if is_cpu and node.get("Text") == "Temperatures":
                    children = node.get("Children", [])
                    if children:
                        val = children[0].get("Value", "0")
                        return float(val.replace(",", ".").replace(" °C", "").strip())
                for child in node.get("Children", []):
                    result = find_temp(child, is_cpu)
                    if result is not None:
                        return result
            return None
        temp = find_temp(data)
        if temp is not None:
            return temp
    except:
        pass
    return 0.0

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def hardware_loop():
    global serial_port
    while True:
        conn_type = config.get("app", {}).get("connection_type", "usb")
        
        if conn_type != "wifi":
            if not serial_port or not serial_port.is_open:
                port = find_esp32_port()
                if port:
                    try:
                        serial_port = serial.Serial(port, 115200, timeout=1)
                    except:
                        serial_port = None
        
        cpu_usage = psutil.cpu_percent(interval=None)
        cpu_temp = get_lhm_cpu_temp()
        
        try:
            gpus = GPUtil.getGPUs()
            gpu_usage = 0.0
            gpu_temp = 0.0
            if len(gpus) > 0:
                gpu_usage = gpus[0].load * 100
                gpu_temp = gpus[0].temperature
        except Exception:
            gpu_usage = 0
            gpu_temp = 0
            
        if SIMULATE_TEMP:
            cpu_temp = 88
            gpu_temp = 88
            
        data_str = f"C:{int(cpu_temp)},U:{int(cpu_usage)},G:{int(gpu_temp)},V:{int(gpu_usage)}\n"
        
        if conn_type == "wifi":
            ip = config.get("app", {}).get("wifi_ip", "")
            if ip:
                try:
                    udp_socket.sendto(data_str.encode('utf-8'), (ip, 4210))
                except:
                    pass
        else:
            if serial_port and serial_port.is_open:
                try:
                    serial_port.write(data_str.encode('utf-8'))
                except:
                    try:
                        serial_port.close()
                    except:
                        pass
                    serial_port = None
        
        time.sleep(1)


def start_lhm():
    lhm_path = os.path.join(base_path, 'LibreHardwareMonitor', 'LibreHardwareMonitor.exe')
    if os.path.exists(lhm_path):
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'LibreHardwareMonitor.exe':
                    return
            # Not running, start it
            import win32api
            import win32con
            import win32process
            # Using ShellExecute to properly request elevation if needed, but wait, Popen might fail with Access Denied if it needs elevation.
            # ShellExecute with 'runas' will trigger UAC.
            win32api.ShellExecute(0, 'runas', lhm_path, '', os.path.dirname(lhm_path), win32con.SW_HIDE)
        except Exception as e:
            print("Error launching LHM:", e)

def main():
    start_lhm()
    load_config()
    
    # Arrancar monitor de hardware en background
    threading.Thread(target=hardware_loop, daemon=True).start()
    
    # Enganchar teclas F13-F20
    keyboard.hook(on_key_event, suppress=False)

    import pystray
    from PIL import Image
    
    window = webview.create_window('MacroDeck', app, width=1200, height=950, background_color='#001f3f')
    force_quit = False
    
    def show_window(icon, item):
        window.show()
    
    def quit_app(icon, item):
        nonlocal force_quit
        force_quit = True
        icon.stop()
        window.destroy()
        os._exit(0)

    def setup_tray():
        try:
            image = Image.open(os.path.join(base_path, 'static', 'logo.png'))
            menu = pystray.Menu(
                pystray.MenuItem("Open", show_window, default=True),
                pystray.MenuItem("Quit", quit_app)
            )
            icon = pystray.Icon("MacroDeck", image, "Macro Deck", menu)
            icon.run()
        except Exception as e:
            print("Tray error:", e)

    threading.Thread(target=setup_tray, daemon=True).start()

    def on_closing():
        nonlocal force_quit
        if force_quit:
            return True
        
        mode = config.get("app", {}).get("closeMode", "ask")
        if mode == "quit":
            force_quit = True
            os._exit(0)
            return True
        elif mode == "minimize":
            window.hide()
            return False
        else:
            # ask mode
            def ask_user():
                # We show a modal in the frontend
                window.evaluate_js('if(typeof showCloseModal === "function") showCloseModal(); else window.location.reload();')
            threading.Thread(target=ask_user).start()
            return False

    window.events.closing += on_closing
    webview.start()


@app.route('/api/flash', methods=['POST'])
def api_flash():
    import time
    try:
        # Simulate flash
        time.sleep(2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/upload_anim', methods=['POST'])
def upload_anim():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    if file:
        try:
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    main()
