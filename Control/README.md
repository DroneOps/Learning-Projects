# Simulación Cinemática e Introducción a Control PID
Esta carpeta contiene un script básico en Python diseñado para introducir los conceptos fundamentales de simulación de sistemas continuos y discreción temporal. Utiliza las ecuaciones de Movimiento Rectilíneo Uniformemente Acelerado (MRUA) en una dimensión como base física antes de la implementación de algoritmos de control realimentado (PID).

El controlador PID es un proceso, en este caso un algoritmo, que nos ayuda a controlar el comportamiento de un proceso. Para nuestra simulación queremos controlar la posición de un sistema imaginario, por lo que el PID medirá el error entre la posición deseada y la posición actual. Finalmente, utilizaremos la acceleración del sistema como entrada para el controlador, así produciremos un cambio en la posición.

La ecuación del sistema considera tres términos, proporcional, integral y derivativo, cada uno con un coeficiente, Kp, Ki y Kd, respectivamente. 

1) **Término proporcional (P):** el error es multiplicado directamente por el constante Kp para obtener el término proporcional

2) **Término integral (I):** suma el error total en el tiempo y lo multiplica por el constante Ki para conseguir el término integral

3) **Término derivativo (D):** calcula el cambio en error comparando el error pasado con el actual, luego lo multiplica por la constante Kd para obtener el término derivativo

Estas constantes se utilizan para modificar la salida del sistema, por lo que es importante probar varios valores que ayuden a la salida aproximarse al punto deseado.

Se requiere `numpy` y `matplotlib`.

Instalación de dependencias:

```bash
pip install -r Control/requirements.txt
```

## Uso y Modificación de Parámetros
- Resolución temporal: Modifique dt para evaluar la precisión de la integración discreta.
- Duración: Ajuste la variable tiempo para simular intervalos más extendidos.
- Condiciones iniciales: Varie los valores de los arreglos vel y a para simular distintas dinámicas de
entrada.

## Guía de Experimentación

| Experimento | Configuración de Ganancias | Comportamiento Esperado |
| ----------- | ---------------------------| ----------------------- |
| 1. Solo Proporcional | "Kp = 2.0, Ki = 0.0, Kd = 0.0" | El sistema oscila alrededor del objetivo o se queda corto por la fricción |
| 2. Añadir Freno (PD)| "Kp = 2.0, Ki = 0.0, Kd = 1.5" | La curva se vuelve suave y se detiene justo en el objetivo sin oscilar. |
| 3. Control Completo (PID) | "Kp = 2.0, Ki = 0.05, Kd = 1.5" | Elimina cualquier error constante residual de forma fluida. |
| 4. Inestabilidad | dt = 1.0 o Ki = 2.0 | ¡El sistema explota! Muestra la importancia de elegír un tiempo de muestreo pequeño y ganancias sintonizadas. |