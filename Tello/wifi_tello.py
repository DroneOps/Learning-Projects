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


# App auxiliar de macOS: se compila una sola vez fuera del repositorio (ver escaner_wifi_mac.swift)
_FUENTE_ESCANER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "escaner_wifi_mac.swift")
_APP_ESCANER = os.path.expanduser("~/Library/Application Support/TelloWiFi/TelloWiFi.app")
_INFO_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleIdentifier</key><string>mx.droneops.tellowifi</string>
  <key>CFBundleName</key><string>TelloWiFi</string>
  <key>CFBundleExecutable</key><string>TelloWiFi</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSUIElement</key><true/>
  <key>NSLocationUsageDescription</key><string>Para ver los nombres de las redes Wi-Fi del dron Tello.</string>
  <key>NSLocationWhenInUseUsageDescription</key><string>Para ver los nombres de las redes Wi-Fi del dron Tello.</string>
</dict></plist>"""


def _compilar_escaner_mac():
    """Compila la app auxiliar si no existe o si el codigo cambio. Regresa True si esta lista."""
    binario = os.path.join(_APP_ESCANER, "Contents", "MacOS", "TelloWiFi")
    if os.path.exists(binario) and os.path.getmtime(binario) >= os.path.getmtime(_FUENTE_ESCANER):
        return True

    print("Preparando el escáner de Wi-Fi para macOS (solo la primera vez)...")
    os.makedirs(os.path.dirname(binario), exist_ok=True)
    with open(os.path.join(_APP_ESCANER, "Contents", "Info.plist"), "w") as archivo:
        archivo.write(_INFO_PLIST)
    compilado = subprocess.run(["swiftc", "-O", _FUENTE_ESCANER, "-o", binario], capture_output=True, text=True)
    if compilado.returncode != 0:
        print("No se pudo compilar el escáner (instala las herramientas con: xcode-select --install).")
        return False
    # macOS solo guarda permisos de apps firmadas; una firma local ("-") es suficiente
    _ejecutar("codesign", "--force", "--sign", "-", _APP_ESCANER)
    return True


def _escanear_mac():
    """
    Escanea redes en macOS. Desde macOS 14, el sistema oculta los nombres de las redes
    (<redacted>) a los scripts de terminal; solo una app con permiso de Localización
    puede verlos, así que usamos una pequeña app auxiliar para escanear.
    """
    if not _compilar_escaner_mac():
        # Sin la app auxiliar: system_profiler (solo muestra nombres si la terminal ya tiene permiso)
        return re.findall(r"^\s+(.+?):\s*$", _ejecutar("system_profiler", "SPAirPortDataType"), re.M)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as archivo:
        salida = archivo.name
    try:
        # La primera vez, macOS pide permiso de Localización para "TelloWiFi"
        subprocess.run(["open", "-W", "-n", _APP_ESCANER, "--args", salida], timeout=90)
        with open(salida) as archivo:
            return archivo.read().splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return []
    finally:
        os.remove(salida)


def redes_tello_guardadas():
    """Redes TELLO- a las que esta computadora ya se conectó antes (el sistema nunca oculta estos nombres)."""
    if SISTEMA == "Darwin":
        salida = _ejecutar("networksetup", "-listpreferredwirelessnetworks", _interfaz_wifi_mac())
    elif SISTEMA == "Linux":
        salida = _ejecutar("nmcli", "-t", "-f", "name", "connection", "show")
    elif SISTEMA == "Windows":
        salida = _ejecutar("netsh", "wlan", "show", "profiles")
    else:
        salida = ""
    # Funciona con cualquier idioma del sistema: solo buscamos los nombres TELLO-
    return sorted(set(re.findall(rf"({PREFIJO_TELLO}\S+)", salida)))


def buscar_redes_tello():
    """Escanea las redes cercanas y regresa las que empiezan con TELLO- (ordenadas, sin repetir)."""
    if SISTEMA == "Darwin":
        nombres = _escanear_mac()
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


def _elegir_red(redes, guardadas=()):
    """Muestra un menu numerado con las redes Tello y regresa la elegida (None para salir)."""
    print("\nRedes Tello disponibles:")
    for numero, nombre in enumerate(redes, start=1):
        nota = "  (guardada, no detectada en el escaneo)" if nombre in guardadas else ""
        print(f"  [{numero}] {nombre}{nota}")
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
        cercanas = buscar_redes_tello()
        # Agregamos las redes Tello ya usadas antes, por si el escaneo no pudo ver sus nombres
        guardadas = [r for r in redes_tello_guardadas() if r not in cercanas]
        redes = cercanas + guardadas

        if not redes:
            print("No se encontró ninguna red TELLO-. Revisa que el dron esté encendido.")
            if SISTEMA == "Darwin":
                print("En macOS, la app donde corres el script (VS Code, Terminal...) necesita permiso de")
                print("Localización para ver los nombres de las redes, y hay que reiniciarla tras darlo:")
                print("  Ajustes del Sistema > Privacidad y seguridad > Localización.")
            elif SISTEMA == "Windows":
                print("En Windows 11, activa la Ubicación para poder ver las redes cercanas:")
                print("  Configuración > Privacidad y seguridad > Ubicación.")
            print("También puedes conectarte manualmente desde el ícono de Wi-Fi.")
            if input("Presiona Enter para buscar de nuevo o 'S' para salir: ").strip().lower() == "s":
                return None
            # Puede que el usuario se haya conectado manualmente mientras tanto
            actual = red_actual()
            if actual and actual.startswith(PREFIJO_TELLO):
                return actual
            continue

        elegida = _elegir_red(redes, guardadas)
        if elegida is None:
            return None
        if elegida == "REINTENTAR":
            continue

        print(f"Conectando a {elegida}...")
        if conectar(elegida):
            print(f"Conectado a {elegida}.")
            return elegida
        print(f"No se pudo conectar a {elegida}. Intenta de nuevo.")
