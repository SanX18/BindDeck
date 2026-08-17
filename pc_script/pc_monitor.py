import time
import serial
import serial.tools.list_ports
import psutil
import GPUtil
import requests

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
        # Peticion al servidor web de LibreHardwareMonitor
        response = requests.get("http://localhost:8085/data.json", timeout=1)
        data = response.json()
        
        # Busqueda recursiva de la temperatura de la CPU
        def find_temp(node, is_cpu=False):
            if isinstance(node, dict):
                # Detectar cuando entramos en la seccion del procesador (suele tener este icono o el texto "Intel"/"AMD")
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
    except Exception as e:
        # Si falla (programa cerrado o web server apagado), devolvemos 0
        pass
    
    return 0.0

def main():
    print("Buscando puerto COM del ESP32...")
    port = find_esp32_port()
    if not port:
        print("No se encontró ningún puerto COM. Conecta el ESP32.")
        return

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"Conectado a {port} a 115200 baudios.")
    except Exception as e:
        print(f"Error al abrir el puerto {port}: {e}")
        return

    print("Enviando telemetría... Presiona Ctrl+C para salir.")
    print("Asegúrate de tener LibreHardwareMonitor abierto con el Web Server activo en el puerto 8085.")
    
    try:
        while True:
            cpu_usage = psutil.cpu_percent(interval=None)
            cpu_temp = get_lhm_cpu_temp()
            
            gpus = GPUtil.getGPUs()
            gpu_usage = 0.0
            gpu_temp = 0.0
            if len(gpus) > 0:
                gpu_usage = gpus[0].load * 100
                gpu_temp = gpus[0].temperature

            data_str = f"C:{int(cpu_temp)},U:{int(cpu_usage)},G:{int(gpu_temp)},V:{int(gpu_usage)}\n"
            
            ser.write(data_str.encode('utf-8'))
            print(f"Enviado: {data_str.strip()}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
