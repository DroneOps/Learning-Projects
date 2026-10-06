# En esta seccion importamos la libreria tiempo y la libreria tello que nos permitira comunicarnos con el dron
import time
from djitellopy import Tello, TelloException
from wifi_tello import asegurar_red_tello

# Definimos la funcion principal
def principal():
    # 0. Verificar que estemos en la red Wi-Fi del dron (si no, buscarla y elegirla)
    red = asegurar_red_tello()
    if red is None:
        print("Sin conexión al dron. Vuelo cancelado.")
        return

    # 1. Creamos la instancia de la herramienta que se conecta con el dron
    tello = Tello()

    print(f"Conectando con el dron Tello (red {red})...")
    
    # 2. Establecer la conexión vía Wi-Fi
    tello.connect()

    # 3. Consultar y mostrar el nivel de batería actual
    # importante comprobar la batería antes de volar!!!!!1
    bateria = tello.get_battery()
    print(f"Nivel de batería: {bateria}%")

    # Regla de seguridad simple: no despegar si la batería es baja
    if bateria < 20:
        print("Batería demasiado baja para un vuelo seguro. Carga el dron e intenta de nuevo.")
        return

    # El Tello se calienta rapido encendido en el suelo y no despega si esta muy caliente
    temperatura = tello.get_temperature()
    print(f"Temperatura: {temperatura}°C")
    if temperatura >= 85:
        print("El dron está demasiado caliente para despegar. Apágalo y déjalo enfriar unos minutos.")
        return

    print("\n--- INICIANDO SECUENCIA DE VUELO ---")
    
    # 4. Despegue automático
    # El dron subirá automáticamente y se mantiene suspendido
    print("Despegando...")
    try:
        tello.takeoff()
    except TelloException:
        print("El dron rechazó el despegue. Causas comunes:")
        print("  - Está caliente: apágalo unos minutos antes de volver a intentar.")
        print("  - El piso es oscuro, brilloso, liso o hay poca luz: ponlo en un piso plano con textura.")
        print("  - Necesita calibrar la IMU: app Tello > Ajustes > Calibración.")
        print("  - Una hélice está doblada o roza con el protector.")
        return

    # 5. Pausa de espera
    # Dejamos que el dron se quede flotando (hovering) en el aire durante 5 segundos
    # Mientras vuela mostramos la red y una cuenta regresiva en una sola linea
    for restantes in range(5, 0, -1):
        print(f"\r  En el aire  ·  Red: {red}  ·  Aterrizando en {restantes}s ", end="", flush=True)
        time.sleep(1)
    print()

    # 6. Aterrizaje automático
    # El dron bajara suavemente hasta el suelo y apagara los motores
    print("Aterrizando...")
    tello.land()

    print("Mision accomplished baby!")

# Punto de entrada del programa
if __name__ == "__main__":
    principal()
