import codecs

py = codecs.open('pc_monitor.py', 'r', 'utf-8').read()

lhm_func = '''
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

'''

py = py.replace('def main():', lhm_func + 'def main():\n    start_lhm()')

codecs.open('pc_monitor.py', 'w', 'utf-8').write(py)
