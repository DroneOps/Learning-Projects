# Antes de hacer cualquier cosa, asegúrate de tener:

```bash
pip install -r Vision/requirements.txt
```
El script de *Aruco.py* detecta marcadores ArUco en tiempo real usando la cámara del tello.

El script de *Yolo.py* detecta objetos en tiempo real usando la cámara web y el modelo preentrenado YOLOv11.

---

# Guía de ejecución de scripts

Para aprender de forma segura y ordenada, ejecuta los archivos en el siguiente orden:

```text
[ 1. Yolo.py ]  ─────────► [ 2. Aruco.py ]
(Detección en Webcam)       (Seguimiento y Distancia con Tello)
