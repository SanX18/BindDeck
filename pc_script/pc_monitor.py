import esptool

import subprocess
import sys
_old_popen = subprocess.Popen
def _new_popen(*args, **kwargs):
    if sys.platform == 'win32':
        kwargs['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
    return _old_popen(*args, **kwargs)
subprocess.Popen = _new_popen

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
import GPUtil
import random
from flask import Flask, render_template, request, jsonify

window_ref = None

# GUI / Icon dependencies
import win32gui
import win32ui
import win32con
import win32api
import win32com.client
from PIL import Image
import base64
from io import BytesIO
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import pystray



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
    "keys": {str(i): {"type": "none", "value": "", "anim": -1} for i in range(13, 22)},
    "esp32": {"animMode": 0, "encMode": 0},
    "app": {"theme": "dark", "lang": "en", "startup": False, "closeMode": "ask"}
}

# --- OTA UPDATER ---
UPDATE_AVAILABLE = False
NEW_VERSION_URL = ""
NEW_VERSION_NAME = ""

# TODO: THE USER MUST CHANGE THIS TO THEIR REAL REPO (E.g., "SanX18/BindDeck")
GITHUB_REPO = "SanX18/BindDeck"
CURRENT_VERSION = "V1.0.0.5"

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
            print("Error loading config:", e)

def manage_startup(enable):
    try:
        startup_path = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup", "BindDeck.bat")
        if enable:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            cmd = f'start "" "{exe_path}"' if getattr(sys, 'frozen', False) else f'start "" pythonw "{exe_path}"'
            with open(startup_path, 'w') as f:
                f.write(f"@echo off\n{cmd}\n")
        else:
            if os.path.exists(startup_path):
                os.remove(startup_path)
    except Exception as e:
        print("Error in startup:", e)

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        manage_startup(config.get("app", {}).get("startup", False))
    except Exception as e:
        print("Error saving config:", e)

# --- KEYBOARD HOOKS ---
last_macro_times = {}

def execute_macro(key_index):
    global last_macro_times
    now = time.time()
    if now - last_macro_times.get(key_index, 0) < 0.3:
        return
    last_macro_times[key_index] = now
    
    if key_index == 21:
        toggle_audio()
        return
        
    action = config["keys"].get(str(key_index), {})
    action_type = action.get("type", "none")
    value = action.get("value", "")
    anim = action.get("anim", -1)
    
    try:
        with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
            f.write(f"[{time.time()}] execute_macro called for key {key_index}. Type: {action_type}, Value: {value}, Anim: {anim}\n")
    except:
        pass
    
    try:
        if int(anim) != -1 and window_ref:
            window_ref.evaluate_js(f"if(typeof playOledPreview === 'function') playOledPreview({anim}, true);")
    except Exception as e:
        print(f"Error anim preview: {e}")
    
    if action_type == "app" and value:
        try:
            val = value.strip('"').strip("'")
            os.startfile(val)
        except Exception as e:
            try:
                subprocess.Popen(value, shell=True)
            except Exception as e2:
                print(f"Error abriendo app: {e2}")
    elif action_type == "shortcut" and value:
        try:
            keys = value.split('+')
            for k in keys: keyboard.press(k)
            time.sleep(0.05)
            for k in reversed(keys): keyboard.release(k)
        except Exception as e:
            with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
                f.write(f"Error shortcut: {e}\n")
    elif action_type == "text" and value:
        try:
            keyboard.write(value)
        except Exception as e:
            pass
    elif action_type == "none":
        try:
            keyboard.press(f"f{key_index}")
            time.sleep(0.05)
            keyboard.release(f"f{key_index}")
        except Exception as e:
            with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
                f.write(f"Error none: {e}\n")


def change_app_volume(app_name, up):
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        if app_name.lower() in ["system", "system volume", "sistema"]:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_vol = volume.GetMasterVolumeLevelScalar()
            if up:
                new_vol = min(1.0, current_vol + 0.04)
            else:
                new_vol = max(0.0, current_vol - 0.04)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return

        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() and session.Process.name().lower() == app_name.lower():
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                current_vol = volume.GetMasterVolume()
                if up:
                    new_vol = min(1.0, current_vol + 0.04)
                else:
                    new_vol = max(0.0, current_vol - 0.04)
                volume.SetMasterVolume(new_vol, None)
    except Exception as e:
        print("Error changing app volume:", e)

current_audio_toggle = 0
def toggle_audio():
    global current_audio_toggle
    # Use SoundVolumeView Device Names for precise switching
    devices = [
        ("Hi-MAX", "Hi-MAX"),
        ("G435 Wireless Gaming Headset", "G435")
    ]
    current_audio_toggle = (current_audio_toggle + 1) % len(devices)
    dev = devices[current_audio_toggle]
    
    try:
        svv_path = os.path.join(sys._MEIPASS, "SoundVolumeView.exe") if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), "SoundVolumeView.exe"))
        subprocess.run([svv_path, "/SetDefault", dev[0], "all"], creationflags=subprocess.CREATE_NO_WINDOW)
        
        if serial_port and serial_port.is_open:
            serial_port.write(f"CMD:MSG:{dev[1]}\n".encode())
    except Exception as e:
        print("Error toggling audio:", e)

def on_key_event(e):
    if e.event_type == keyboard.KEY_DOWN:
        if e.name.startswith('f') and e.name[1:].isdigit():
            key_num = int(e.name[1:])
            if key_num == 23 or key_num == 24:
                if config.get("esp32", {}).get("encMode", 0) == 5:
                    app_name = config.get("esp32", {}).get("encApp", "")
                    if app_name:
                        threading.Thread(target=change_app_volume, args=(app_name, key_num == 24), daemon=True).start()
                    return False
            if key_num == 21: # Encoder button toggle audio
                threading.Thread(target=toggle_audio, daemon=True).start()
                return False
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

@app.route('/api/flash_bundled', methods=['POST'])
def api_flash_bundled():
    port_to_flash = find_esp32_port()
    if not port_to_flash:
        return jsonify({"success": False, "error": "Device not connected via USB"})
        
    global serial_port
    if serial_port and serial_port.is_open:
        try:
            serial_port.write(b"CMD:UPDATE\n")
            serial_port.flush()
            time.sleep(1) # wait for OLED to render the updating screen
        except:
            pass
        serial_port.close()
        serial_port = None
        
    fw_path = os.path.join(base_path, 'firmware.bin')
    if not os.path.exists(fw_path):
        return jsonify({"success": False, "error": "Bundled firmware not found"})
        
    try:
        import subprocess
        try:
            result = subprocess.run(
                ["python", "-m", "esptool", "--port", port_to_flash, "--baud", "460800", "write_flash", "-z", "0x10000", fw_path],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({"success": False, "error": f"esptool failed: {e.stderr}"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/flash_local', methods=['POST'])
def api_flash_local():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"})
        
    port_to_flash = find_esp32_port()
    if not port_to_flash:
        return jsonify({"success": False, "error": "Device not connected via USB"})
        
    global serial_port
    if serial_port and serial_port.is_open:
        serial_port.close()
        serial_port = None
        
    try:
        file.save("local_firmware.bin")
        cmd = [sys.executable, "-m", "esptool", "--port", port_to_flash, "--baud", "460800", "write_flash", "-z", "0x10000", "local_firmware.bin"]
        subprocess.run(cmd, check=True)
        if os.path.exists("local_firmware.bin"):
            os.remove("local_firmware.bin")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config
    if request.method == 'POST':
        new_cfg = request.json
        old_esp32 = config.get("esp32", {})
        old_keys = config.get("keys", {})
        config = new_cfg
        save_config()
        
        if serial_port and serial_port.is_open:
            try:
                new_esp32 = new_cfg.get("esp32", {})
                new_keys = new_cfg.get("keys", {})
                
                anim = new_esp32.get("animMode", 0)
                if anim is None: anim = 0
                if str(old_esp32.get("animMode", "")) != str(anim):
                    serial_port.write(f"CFG:ANIM:{anim}\n".encode('utf-8'))
                    time.sleep(0.1)

                enc = new_esp32.get("encMode", 0)
                if enc is None: enc = 0
                if str(old_esp32.get("encMode", "")) != str(enc):
                    serial_port.write(f"CFG:ENC:{enc}\n".encode('utf-8'))
                    time.sleep(0.1)

                brt = new_esp32.get("brightness", 255)
                if brt is None: brt = 255
                if str(old_esp32.get("brightness", "")) != str(brt):
                    serial_port.write(f"CFG:BRIGHT:{brt}\n".encode('utf-8'))
                    time.sleep(0.1)
                
                # Check if key animations changed
                changed_anims = False
                kb_anims = []
                for i in range(13, 22):
                    key_anim = new_keys.get(str(i), {}).get("anim", -1)
                    old_anim = old_keys.get(str(i), {}).get("anim", -1)
                    if str(key_anim) != str(old_anim): changed_anims = True
                    kb_anims.append(str(key_anim))
                
                if changed_anims:
                    kb_anims_str = ",".join(kb_anims)
                    serial_port.write(f"CFG:KB_ANIM:{kb_anims_str}\n".encode('utf-8'))
                    time.sleep(0.1)
                
                # Check if key texts changed
                for i in range(13, 22):
                    disp_text = new_keys.get(str(i), {}).get("dispText", "")
                    old_text = old_keys.get(str(i), {}).get("dispText", "")
                    if str(disp_text) != str(old_text):
                        idx = i - 13
                        serial_port.write(f"CFG:TXT:{idx}:{disp_text}\n".encode('utf-8'))
                        time.sleep(0.1)
                
            except Exception as e:
                print("Error enviando config al ESP32:", e)
                
        return jsonify({"status": "success"})
    return jsonify(config)

@app.route("/api/preview/<int:mode>", methods=["GET"])
def api_preview(mode):
    if serial_port and serial_port.is_open:
        try:
            serial_port.write(f"CMD:PREVIEW:{mode}\n".encode('utf-8'))
        except:
            pass
    return jsonify({"success": True})

wifi_status_data = {"connected": False, "ssid": "", "ip": ""}

@app.route("/api/get_wifi_status", methods=["GET"])
def api_get_wifi_status():
    global wifi_status_data
    if serial_port and serial_port.is_open:
        try:
            serial_port.write(b"CMD:GET_WIFI\n")
            time.sleep(0.5)
            return jsonify(wifi_status_data)
        except:
            pass
    return jsonify({"connected": False, "ssid": "", "ip": ""})

@app.route("/api/send_config", methods=["POST"])
def api_send_config():
    data = request.json
    cmd = data.get("cmd", "")
    if serial_port and serial_port.is_open and cmd:
        try:
            serial_port.write(cmd.encode('utf-8'))
        except:
            pass
    return jsonify({"success": True})

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


def get_icon_base64(path):
    try:
        import win32gui, win32ui, win32con, win32api
        from PIL import Image
        import base64
        from io import BytesIO
        
        large, small = win32gui.ExtractIconEx(path, 0)
        if not large and not small: return ""
        hicon = large[0] if large else small[0]
        
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        mdc = hdc.CreateCompatibleDC()
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        mdc.SelectObject(hbmp)
        
        brush = win32ui.CreateBrush(win32con.BS_SOLID, win32api.RGB(30, 30, 30), 0)
        mdc.FillRect((0, 0, ico_x, ico_y), brush)
        win32gui.DrawIconEx(mdc.GetSafeHdc(), 0, 0, hicon, ico_x, ico_y, 0, None, win32con.DI_NORMAL)
        
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        
        win32gui.DestroyIcon(hicon)
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return ""

@app.route('/api/installed_apps')
def api_installed_apps():
    import psutil, win32com.client
    shell = win32com.client.Dispatch('WScript.Shell')
    paths = [
        os.environ.get('PROGRAMDATA', 'C:\\ProgramData') + r'\Microsoft\Windows\Start Menu\Programs',
        os.environ.get('APPDATA') + r'\Microsoft\Windows\Start Menu\Programs'
    ]
    apps = [{'name': 'System Volume', 'path': 'System', 'exe': 'System', 'icon': ''}]
    seen_names = set()
    seen_exes = set(['system'])
    try:
        for p in paths:
            for root, dirs, files in os.walk(p):
                for file in files:
                    if file.endswith('.lnk'):
                        try:
                            shortcut = shell.CreateShortCut(os.path.join(root, file))
                            target = shortcut.Targetpath
                            if target.lower().endswith('.exe'):
                                name = os.path.splitext(file)[0]
                                exe = os.path.basename(target)
                                if name not in seen_names and exe.lower() not in ['update.exe', 'unins000.exe', 'uninstall.exe']:
                                    apps.append({'name': name, 'path': target, 'exe': exe, 'icon': get_icon_base64(target)})
                                    seen_names.add(name)
                                    seen_exes.add(exe.lower())
                        except: pass
        for p in psutil.process_iter(['name', 'exe']):
            try:
                exe_path = p.info['exe']
                exe_name = p.info['name']
                if exe_path and exe_name.endswith('.exe') and exe_name.lower() not in seen_exes:
                    if 'system32' not in exe_path.lower() and 'windowsapps' not in exe_path.lower():
                        name = os.path.splitext(exe_name)[0].capitalize()
                        apps.append({'name': name + ' (Running)', 'path': exe_path, 'exe': exe_name, 'icon': get_icon_base64(exe_path)})
                        seen_exes.add(exe_name.lower())
            except: pass
        apps.sort(key=lambda x: x['name'])
    except Exception as e:
        print("Error in apps:", e)
    return jsonify(apps)

@app.route('/api/audio_apps')
def api_audio_apps():
    apps = [{"name": "System Volume (Master)", "exe": "System", "icon": ""}]
    try:
        from pycaw.pycaw import AudioUtilities
        sessions = AudioUtilities.GetAllSessions()
        seen = set()
        for session in sessions:
            if session.Process and session.Process.name():
                name = session.Process.name()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    apps.append({"name": name, "exe": name, "icon": ""})
    except Exception as e:
        print("Error getting audio apps:", e)
    return jsonify(apps)

@app.route('/api/status')
def api_status():
    conn_type = config.get("app", {}).get("connection_type", "usb")
    
    is_usb = serial_port is not None and serial_port.is_open
    is_bt = getattr(app, 'bt_connected', False)
    
    if is_usb:
        return jsonify({"connected": True, "type": "USB", "ping": random.randint(8, 24), "battery": None})
    elif is_bt:
        return jsonify({"connected": True, "type": "Bluetooth", "ping": random.randint(30, 85), "battery": getattr(app, 'bt_battery', None)})
    else:
        return jsonify({"connected": False, "type": "None", "ping": 0, "battery": None})

def check_bt_status_loop():
    ps_cmd = "$dev = Get-PnpDevice -Class Bluetooth | Where-Object { $_.FriendlyName -match 'BindDeck' -and $_.Status -eq 'OK' }; if ($dev) { Write-Output 'CONNECTED'; $prop = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' -ErrorAction SilentlyContinue; if ($prop -and $prop.Data -ne $null) { Write-Output $prop.Data } }"
    while True:
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                startupinfo=startupinfo,
                creationflags=0x08000000,
                text=True
            ).strip().split('\n')
            
            output = [line.strip() for line in output if line.strip()]
            
            app.bt_connected = len(output) > 0 and output[0] == "CONNECTED"
            if len(output) > 1 and output[1].isdigit():
                app.bt_battery = int(output[1])
            else:
                app.bt_battery = None
        except Exception:
            app.bt_connected = False
            app.bt_battery = None
        time.sleep(5)

threading.Thread(target=check_bt_status_loop, daemon=True).start()


@app.route('/api/window/minimize', methods=['POST'])
def api_minimize():
    for w in webview.windows:
        w.hide()
    return jsonify({"status": "ok"})

@app.route('/api/window/quit', methods=['POST'])
def api_quit():
    kill_lhm()
    os._exit(0)
    return jsonify({"status": "ok"})

@app.route('/api/version')
def api_version():
    return jsonify({"version": CURRENT_VERSION})

@app.route('/api/browse')
def browse_file():
    global window_ref
    try:
        import webview
        if window_ref:
            result = window_ref.create_file_dialog(
                webview.OPEN_DIALOG, 
                allow_multiple=False,
                file_types=('Executables (*.exe)', 'All files (*.*)')
            )
            if result and len(result) > 0:
                return jsonify({"path": result[0]})
    except Exception as e:
        print("Error browse:", e)
    return jsonify({"path": ""})

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
        import esptool
        cmd = ["--port", port_to_flash, "--baud", "460800", "write_flash", "-z", "0x10000", "firmware_update.bin"]
        esptool.main(cmd)
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

def serial_read_loop():
    global serial_port
    while True:
        try:
            sp = serial_port
            if sp and sp.is_open and sp.in_waiting > 0:
                line = sp.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("BTN:"):
                    try:
                        idx = int(line.split(":")[1])
                        key_num = idx + 13
                        with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
                            f.write(f"[{time.time()}] SERIAL READ BTN: {idx} (key_num={key_num})\n")
                        threading.Thread(target=execute_macro, args=(key_num,), daemon=True).start()
                    except:
                        pass
                elif line.startswith("ENC:"):
                    cmd = line.split(":")[1]
                    # Solo nos interesa APPVUP y APPVDN para controlar el app volume por USB
                    if cmd == "APPVUP" or cmd == "APPVDN":
                        app_name = config.get("esp32", {}).get("encApp", "")
                        if app_name:
                            threading.Thread(target=change_app_volume, args=(app_name, cmd == "APPVUP"), daemon=True).start()
                    # Otras acciones de encMode 0..3 se pueden simular si queremos que funcionen 100% por USB sin Bluetooth
                    elif cmd == "VUP": keyboard.send("volume up")
                    elif cmd == "VDN": keyboard.send("volume down")
                    elif cmd == "ZIN": keyboard.send("ctrl++")
                    elif cmd == "ZOUT": keyboard.send("ctrl+-")
                    elif cmd == "TFWD": keyboard.send("ctrl+tab")
                    elif cmd == "TBCK": keyboard.send("ctrl+shift+tab")
                    elif cmd == "REDO": keyboard.send("ctrl+y")
                    elif cmd == "UNDO": keyboard.send("ctrl+z")
                elif line.startswith("WIFI_INFO:"):
                    global wifi_status_data
                    parts = line.split(":")[1].split(",")
                    ssid = parts[0] if len(parts) > 0 else ""
                    ip = parts[1] if len(parts) > 1 else ""
                    wifi_status_data = {"connected": ssid != "DISCONNECTED", "ssid": ssid, "ip": ip}
        except:
            pass
        time.sleep(0.02)

def udp_listen_loop():
    try:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.bind(('0.0.0.0', 4211))
        with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
            f.write(f"[{time.time()}] UDP Listener Started on port 4211\n")
        while True:
            data, addr = listen_sock.recvfrom(1024)
            line = data.decode('utf-8', errors='ignore').strip()
            if line.startswith("BTN:"):
                try:
                    idx = int(line.split(":")[1])
                    key_num = idx + 13
                    with open(os.path.join(os.path.expanduser("~"), "binddeck_debug.txt"), "a") as f:
                        f.write(f"[{time.time()}] UDP READ BTN: {idx} (key_num={key_num})\n")
                    threading.Thread(target=execute_macro, args=(key_num,), daemon=True).start()
                except:
                    pass
            elif line.startswith("ENC:"):
                cmd = line.split(":")[1]
                if cmd == "APPVUP" or cmd == "APPVDN":
                    app_name = config.get("esp32", {}).get("encApp", "")
                    if app_name:
                        threading.Thread(target=change_app_volume, args=(app_name, cmd == "APPVUP"), daemon=True).start()
                elif cmd == "VUP": keyboard.send("volume up")
                elif cmd == "VDN": keyboard.send("volume down")
                elif cmd == "ZIN": keyboard.send("ctrl++")
                elif cmd == "ZOUT": keyboard.send("ctrl+-")
                elif cmd == "TFWD": keyboard.send("ctrl+tab")
                elif cmd == "TBCK": keyboard.send("ctrl+shift+tab")
                elif cmd == "REDO": keyboard.send("ctrl+y")
                elif cmd == "UNDO": keyboard.send("ctrl+z")
    except Exception as e:
        print("UDP Listen Error:", e)

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
        
        # Zero-Config Wi-Fi Broadcast to all interfaces
        try:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Standard 255.255.255.255
            udp_socket.sendto(data_str.encode('utf-8'), ('255.255.255.255', 4210))
            
            # Subnet directed broadcasts
            for interface, snics in psutil.net_if_addrs().items():
                for snic in snics:
                    if snic.family == socket.AF_INET and snic.netmask and snic.address != '127.0.0.1':
                        try:
                            # Calculate broadcast address
                            ip_parts = snic.address.split('.')
                            mask_parts = snic.netmask.split('.')
                            bcast_parts = [str(int(ip_parts[i]) | (255 - int(mask_parts[i]))) for i in range(4)]
                            bcast_ip = '.'.join(bcast_parts)
                            udp_socket.sendto(data_str.encode('utf-8'), (bcast_ip, 4210))
                        except:
                            pass
        except:
            pass
        
        if conn_type == "usb":
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


def kill_lhm():
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'LibreHardwareMonitor.exe':
                proc.kill()
    except:
        pass

def main():
    start_lhm()
    load_config()
    
    # Arrancar monitor de hardware en background
    threading.Thread(target=hardware_loop, daemon=True).start()
    threading.Thread(target=serial_read_loop, daemon=True).start()
    threading.Thread(target=udp_listen_loop, daemon=True).start()
    
    # Enganchar teclas F13-F20
    keyboard.hook(on_key_event, suppress=False)

    import pystray


    from PIL import Image
    
    global window_ref
    window = webview.create_window('BindDeck', app, width=1200, height=950, background_color='#001f3f')
    window_ref = window
    force_quit = False
    
    def show_window(icon, item):
        window.show()
    
    def quit_app(icon, item):
        nonlocal force_quit
        force_quit = True
        icon.stop()
        window.destroy()
        kill_lhm()
        os._exit(0)

    def setup_tray():
        try:
            image = Image.open(os.path.join(base_path, 'static', 'logo.png'))
            menu = pystray.Menu(
                pystray.MenuItem("Open", show_window, default=True),
                pystray.MenuItem("Quit", quit_app)
            )
            icon = pystray.Icon("BindDeck", image, "BindDeck", menu)
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
            kill_lhm()
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
