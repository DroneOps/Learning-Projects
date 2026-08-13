'''
Script para detección de personas usando YOLOv11 y OpenCV.
'''

import os
import cv2
from ultralytics import YOLO


def main():
    # Cargar el modelo YOLO 11
    model = YOLO("yolo11n.pt") # aqui manda a llamar el modelo ya preentrenado

    cap = cv2.VideoCapture(0) # abrir la webcam normalmente 0

    print("Q para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error en la cámara.")
            break
        '''
        # Inferencia con YOLO (device='cpu' o device=0 para GPU)
        # classes=[0] usa el dataset COCO https://docs.ultralytics.com/datasets/detect/coco

        '''
       
        results = model(frame, classes=[0], conf=0.25, device="cpu", verbose=False) # conf = umbral de confianza, verbose=False para no mostrar información adicional

        # Dibujar las detecciones sobre el frame
        annotated_frame = results[0].plot()

        # Mostrar el frame en pantalla
        cv2.imshow("Detección de Personas", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"): # cv2.waitKey(1) espera 1 ms para la tecla 'q' para salir
            break

    # Liberar la cámara y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()