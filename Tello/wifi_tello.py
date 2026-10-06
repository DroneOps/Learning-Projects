# Utilidades para detectar, buscar y conectarse a la red Wi-Fi del dron Tello.
# Funciona en macOS (networksetup), Linux (nmcli) y Windows (netsh), sin librerias extra.
import os
import platform
import re
import subprocess
import tempfile
import time

PREFIJO_TELLO = "TELLO-"
SISTEMA = platform.system()


def _ejecutar(*comando):
    """Ejecuta un comando y regresa su salida como texto ('' si falla)."""
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=30)
        return resultado.stdout if resultado.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _interfaz_wifi_mac():
    """Nombre del dispositivo Wi-Fi en macOS (normalmente en0)."""
    puertos = _ejecutar("networksetup", "-listallhardwareports")
    encontrado = re.search(r"Hardware Port: (?:Wi-Fi|AirPort)\nDevice: (\S+)", puertos)
    return encontrado.group(1) if encontrado else "en0"


def red_actual():
    """Regresa el nombre (SSID) de la red Wi-Fi actual, o None si no se puede saber."""
    if SISTEMA == "Darwin":
        salida = _ejecutar("networksetup", "-getairportnetwork", _interfaz_wifi_mac())
        encontrado = re.search(r"Current Wi-Fi Network: (.+)", salida)
    elif SISTEMA == "Linux":
        encontrado = re.search(r"^yes:(.+)$", _ejecutar("nmcli", "-t", "-f", "active,ssid", "dev", "wifi"), re.M)
    elif SISTEMA == "Windows":
        encontrado = re.search(r"^\s*SSID\s*:\s*(.+)$", _ejecutar("netsh", "wlan", "show", "interfaces"), re.M)
    else:
        encontrado = None
    return encontrado.group(1).strip() if encontrado else None


def buscar_redes_tello():
    """Escanea las redes cercanas y regresa las que empiezan con TELLO- (ordenadas, sin repetir)."""
    if SISTEMA == "Darwin":
        salida = _ejecutar("system_profiler", "SPAirPortDataType")
        nombres = re.findall(r"^\s+(.+?):\s*$", salida, re.M)
    elif SISTEMA == "Linux":
        nombres = _ejecutar("nmcli", "-t", "-f", "ssid", "dev", "wifi", "list", "--rescan", "yes").splitlines()
    elif SISTEMA == "Windows":
        nombres = re.findall(r"^SSID \d+\s*:\s*(.+)$", _ejecutar("netsh", "wlan", "show", "networks"), re.M)
    else:
        nombres = []
    return sorted({n.strip() for n in nombres if n.strip().startswith(PREFIJO_TELLO)})


def _conectar_windows(ssid):
    # Windows solo se conecta a redes con perfil guardado; creamos uno para la red abierta del Tello
    perfil = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{ssid}</name>
  <SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>manual</connectionMode>
  <MSM><security><authEncryption>
    <authentication>open</authentication><encryption>none</encryption><useOneX>false</useOneX>
  </authEncryption></security></MSM>
</WLANProfile>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as archivo:
        archivo.write(perfil)
    try:
        _ejecutar("netsh", "wlan", "add", "profile", f"filename={archivo.name}")
    finally:
        os.remove(archivo.name)
    _ejecutar("netsh", "wlan", "connect", f"name={ssid}")


def conectar(ssid, espera=20):
    """Se conecta a la red indicada (el Tello no usa contraseña) y espera a que quede activa."""
    if SISTEMA == "Darwin":
        _ejecutar("networksetup", "-setairportnetwork", _interfaz_wifi_mac(), ssid)
    elif SISTEMA == "Linux":
        _ejecutar("nmcli", "dev", "wifi", "connect", ssid)
    elif SISTEMA == "Windows":
        _conectar_windows(ssid)

    limite = time.time() + espera
    while time.time() < limite:
        if red_actual() == ssid:
            return True
        time.sleep(1)
    return False


def _elegir_red(redes):
    """Muestra un menu numerado con las redes Tello y regresa la elegida (None para salir)."""
    print("\nRedes Tello disponibles:")
    for numero, nombre in enumerate(redes, start=1):
        print(f"  [{numero}] {nombre}")
    print("  [R] Volver a buscar   [S] Salir")

    while True:
        opcion = input("Elige una red [1]: ").strip().lower() or "1"
        if opcion == "s":
            return None
        if opcion == "r":
            return "REINTENTAR"
        if opcion.isdigit() and 1 <= int(opcion) <= len(redes):
            return redes[int(opcion) - 1]
        print("Opción no válida, intenta de nuevo.")


def asegurar_red_tello():
    """
    Verifica que estemos conectados a una red TELLO-.
    Si no, busca redes cercanas, deja elegir una en un menu y se conecta.
    Regresa el nombre de la red Tello, o None si el usuario decide salir.
    """
    actual = red_actual()
    if actual and actual.startswith(PREFIJO_TELLO):
        return actual

    print(f"No estás conectado a la red del dron (red actual: {actual or 'ninguna'}).")

    while True:
        print("Buscando redes Tello cercanas...")
        redes = buscar_redes_tello()

        if not redes:
            print("No se encontró ninguna red TELLO-. Revisa que el dron esté encendido.")
            if SISTEMA == "Darwin":
                print("En macOS, la terminal necesita permiso de Ubicación para ver los nombres de las redes:")
                print("  Ajustes del Sistema > Privacidad y seguridad > Localización.")
                print("También puedes conectarte manualmente desde el ícono de Wi-Fi.")
            if input("Presiona Enter para buscar de nuevo o 'S' para salir: ").strip().lower() == "s":
                return None
            # Puede que el usuario se haya conectado manualmente mientras tanto
            actual = red_actual()
            if actual and actual.startswith(PREFIJO_TELLO):
                return actual
            continue

        elegida = _elegir_red(redes)
        if elegida is None:
            return None
        if elegida == "REINTENTAR":
            continue

        print(f"Conectando a {elegida}...")
        if conectar(elegida):
            print(f"Conectado a {elegida}.")
            return elegida
        print(f"No se pudo conectar a {elegida}. Intenta de nuevo.")
