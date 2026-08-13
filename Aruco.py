import cv2
import cv2.aruco as aruco
import numpy as np
from djitellopy import Tello

# --- PARÁMETROS BÁSICOS ---
# Ancho real del marcador ArUco impreso (en centímetros)
ANCHO_REAL_ARUCO_CM = 15.0  # Se cambia en base al tamaño del papel
# Distancia focal aproximada de la cámara del Tello para estimar distancia simple
FOCAL_TELLO = 600.0

def detectar_y_dibujar(frame, detector):
    """Detecta marcadores ArUco, dibuja su borde, su centro y estima la distancia."""
    # Convertir a escala de grises para que OpenCV trabaje más rápido
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Buscar los ArUcos en la imagen
    corners, ids, rejected = detector.detectMarkers(gray)

    # Si se detectó al menos un marcador ArUco
    if ids is not None:
        # 1. Dibujar los bordes estándar del ArUco
        aruco.drawDetectedMarkers(frame, corners, ids)

        # Recorrer cada ArUco detectado
        for i, corner in enumerate(corners):
            # 'corner' tiene las 4 esquinas del marcador: [Top-Left, Top-Right, Bottom-Right, Bottom-Left]
            pts = corner[0]

            # 2. Calcular el centro del marcador en píxeles
            center_x = int(np.mean(pts[:, 0]))
            center_y = int(np.mean(pts[:, 1]))

            # Dibujar un punto rojo en el centro
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # 3. Calcular el ancho del ArUco en píxeles (distancia entre esquina 0 y 1)
            ancho_px = np.linalg.norm(pts[0] - pts[1])

            # 4. Estimar la distancia simple (Fórmulas básicas de semejanza de triángulos)
            # Distancia (cm) = (Ancho Real * Distancia Focal) / Ancho en Píxeles
            if ancho_px > 0:
                distancia_cm = (
                    ANCHO_REAL_ARUCO_CM * FOCAL_TELLO
                ) / ancho_px

                # Mostrar la distancia en pantalla encima del ArUco
                cv2.putText(
                    frame, #Imagen donde va a colocar el texto
                    f"Dist: {distancia_cm:.1f} cm", #El texto que muestra en la imagen
                    (center_x - 50, center_y - 20), #La posicion
                    cv2.FONT_HERSHEY_SIMPLEX, # el tipo de fuente
                    0.6, # Tamaño de la letra
                    (0, 255, 0), # Color en BGR
                    2, # Grosor
                )

            print(
                f"ArUco ID: {ids[i][0]} | Centro: ({center_x}, {center_y}) | Distancia: {distancia_cm:.1f} cm"
            )

    else:
        # Texto en pantalla cuando no hay detecciones
        cv2.putText(
            frame, 
            "BUSCANDO ARUCO...", 
            (20, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 0, 255), 
            2, 
        )

    return frame


def main():
    # Inicializar el dron
    tello = Tello()

    try:
        tello.connect()
        tello.streamon()
    except Exception as e:
        print(f"Error al conectar con el Tello: {e}")
        return

    # Crear el detector ArUco (Usando el diccionario 6x6_50)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    frame_read = tello.get_frame_read()

    print("\nIniciando transmisión. Presiona 'Q' para salir.")

    while True:
        frame = frame_read.frame
        if frame is None:
            continue

        # La cámara del Tello entrega las imágenes en formato RGB, las pasamos a BGR para OpenCV
        img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Procesar el fotograma
        frame_procesado = detectar_y_dibujar(img_bgr, detector)

        # Mostrar en pantalla
        cv2.imshow("Deteccion ArUco - Tello", frame_procesado)

        # Salir con la tecla 'Q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Limpieza al cerrar
    tello.streamoff()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
