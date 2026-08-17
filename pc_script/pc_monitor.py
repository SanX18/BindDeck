import time
import serial
import serial.tools.list_ports
import psutil
import requests
import threading
import json
import os
import keyboard
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
CONFIG_FILE = "macro_config.json"
serial_port = None
config = {
    "keys": {str(i): {"type": "none", "value": ""} for i in range(13, 21)},
    "esp32": {"animMode": 0, "encMode": 0}
}

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

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# --- KEYBOARD HOOKS ---
def execute_macro(key_index):
    # key_index va de 13 a 20
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

def on_key_event(e):
    if e.event_type == keyboard.KEY_DOWN:
        # F13 to F20
        if e.name.startswith('f') and e.name[1:].isdigit():
            key_num = int(e.name[1:])
            if 13 <= key_num <= 20:
                action_type = config["keys"].get(str(key_num), {}).get("type", "none")
                if action_type != "none":
                    # Si tiene accion, ejecutamos en hilo separado y SUPRIMIMOS el evento
                    threading.Thread(target=execute_macro, args=(key_num,), daemon=True).start()
                    # Retornar False suprime la tecla original para que Windows no la vea
                    return False
    return True

# --- FLASK API ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config
    if request.method == 'POST':
        data = request.json
        config = data
        save_config()
        
        # Enviar comandos al ESP32 si está conectado
        if serial_port and serial_port.is_open:
            try:
                anim = config.get("esp32", {}).get("animMode", 0)
                enc = config.get("esp32", {}).get("encMode", 0)
                serial_port.write(f"CFG:ANIM:{anim}\n".encode('utf-8'))
                time.sleep(0.1)
                serial_port.write(f"CFG:ENC:{enc}\n".encode('utf-8'))
            except Exception as e:
                print("Error enviando config al ESP32:", e)
                
        return jsonify({"status": "success"})
    return jsonify(config)

def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# --- ESP32 MONITOR ---
def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "CH340" in port.description or "CP210x" in port.description or "Serial" in port.description:
            return port.device
    if len(ports) > 0:
        return ports[0].device
    return None

def get_lhm_cpu_temp():
    try:
        response = requests.get("http://localhost:8085/data.json", timeout=1)
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

def main():
    global serial_port
    load_config()
    
    # Iniciar Flask en hilo de fondo
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Enganchar el teclado globalmente
    keyboard.hook(on_key_event, suppress=False)

    print("Buscando ESP32...")
    port = find_esp32_port()
    if not port:
        print("No ESP32 conectado. Abriendo solo la web (http://localhost:5000).")
    else:
        try:
            serial_port = serial.Serial(port, 115200, timeout=1)
            print(f"Conectado a {port}.")
        except Exception as e:
            print(f"Error puerto {port}: {e}")

    try:
        while True:
            cpu_usage = psutil.cpu_percent(interval=None)
            cpu_temp = get_lhm_cpu_temp()
            # Quitamos GPUtil ya que fallaba en python 3.14, enviamos 0 temporalmente o extraemos de LHM
            # Para simplificar y no depender de GPUtil, extraemos GPU temp de LHM también si queremos,
            # o dejamos 0 por ahora para no sobrecargar el parser recursivo.
            gpu_usage = 0
            gpu_temp = 0
            
            if serial_port and serial_port.is_open:
                data_str = f"C:{int(cpu_temp)},U:{int(cpu_usage)},G:{int(gpu_temp)},V:{int(gpu_usage)}\n"
                try:
                    serial_port.write(data_str.encode('utf-8'))
                except:
                    pass
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        if serial_port:
            serial_port.close()

if __name__ == "__main__":
    main()
