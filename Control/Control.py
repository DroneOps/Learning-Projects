"""
Un scrip en el que aprenderas el control más básico PID.
"""

import numpy as np
import matplotlib.pyplot as plt
"""
Primero tenemos que simular un sistema, usaremos unas ecuaciones muy simples de MRUA 
en una sola dirección para que sea entendible.
"""
#Estados iniciales y saltos de tiempo

tiempo = 10 # cambia aqui para aumentar el numero de pasos que quieres ver
tiempo += 1 # le sumamos uno para de verdad plotear hasta el numero deseado si no se quedaria uno antes

dt = 1

tiempo = int(tiempo/dt)

pos = [0] * tiempo # definimos la posicion inicial lo hacemos vector para plotear más adelante
vel  = [1] * tiempo # velocidad 
a =  [2] * tiempo # aceleración

# Iniciamos el buclo para calcular la posicion en el tiempo definido arriba
t = 0

while t+1 < tiempo:
    pos[t+1] = pos[t] + vel[t]*dt + (a[t]*0.5*dt**2) # Esta es la ecuacion de MRUA
    vel[t+1] = vel[t] + a[t]*dt 
    t += 1


print(pos)
# Ploteamos con los valores iniciales

plt.plot(np.arange(0, tiempo, 1), pos)
plt.show()
