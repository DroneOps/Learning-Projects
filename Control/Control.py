"""
Un script en el que aprenderas el control más básico PID.
"""

import numpy as np
import matplotlib.pyplot as plt

"""
Primero tenemos que simular un sistema, usaremos unas ecuaciones muy simples de MRUA 
en una sola dirección para que sea entendible.
"""
# Estados iniciales y saltos de tiempo

tiempo_total = 10 
dt           = 1
pasos        = int(tiempo_total/dt)

setpoint = 100.0        # definimos la posición que tenemos como objetivo 

pos = [0] * pasos       # definimos la posicion inicial lo hacemos vector para plotear más adelante
vel = [1] * pasos       # velocidad 
a   = [0] * pasos       # aceleración
time_axis = np.linspace(0, tiempo_total, pasos)

# Ganancias PID (ajusta estos parametros para ver como cambia el comportamiento)
Kp = 0.0                # Ganancia proporcional
Ki = 0.0                # Ganancia integral
Kd = 0.0                # Ganancia derivativa

# Variables de seguimiento para parte derivativa e integral
error_integral   = 0.0
error_derivativo = 0.0
error_previo     = 0.0

# Definimos variable de tiempo
t = 0

# Bucle principal
while t in range(pasos - 1):
    # Calcular error del paso actual
    error = setpoint - pos[t]

    # Actualizar componentes integral y derivativo
    error_integral += error * dt
    error_derivativo = (error - error_previo) / dt

    # Utilizamos la formula PID; calculamos señales de control
    a[t] = (Kp * error) + (Ki * error_integral) + (Kd * error_derivativo)

    # Actualizamos las ecuaciones de cinematica (MRUA)
    pos[t+1] = pos[t] + (vel[t] * dt) + (0.5 * a[t] * (dt**2)) # Esta es la ecuacion de MRUA
    vel[t+1] = vel[t] + (a[t] * dt)

    # Guardamos el error actual para el siguiente paso
    error_previo = error

# Calculamos la acceleración para el ultimo paso para mantener el tamaño del arreglo
a[-1] = a[-2]
    
# Ploteamos con los valores iniciales
plt.figure(figsize=(10, 5))
plt.plot(time_axis, pos, label="Current Position", color="blue", linewidth=2)
plt.axhline(y=setpoint, color="red", linestyle="--", label="Setpoint (Target)")
plt.title("PID Controller Position Simulation")
plt.xlabel("Time (seconds)")
plt.ylabel("Position")
plt.legend()
plt.grid(True)
plt.show()
