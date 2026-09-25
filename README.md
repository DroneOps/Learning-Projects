# Curso Inicial de DroneOps: Learning Projects 

¡Bienvenido a DroneOps! 

Si alguna vez quisiste programar robótica real, ver a un dron tomar sus propias decisiones en el aire o dominar las tecnologías más demandadas en la industria aeroespacial y de automatización, estás en el lugar correcto.

Este curso inicial es tu puerta de entrada rápida. Aquí no te vas a quedar en la teoría: aprenderás desde los fundamentos del control de drones hasta visión por computadora y robótica avanzada.

---
## ¿Por qué estar aquí?

- Proyectos Reales: A partir de ahora comenzaras a trabajar con problemas reales y prepararemos en equipo el terreno para competir o desarrollar proyectos de gran impacto.
- Curriculum de Alto Nivel: Dominar herramientas como ROS y OpenCV te pone pasos adelante en la industria de la robótica, automatización y software.
- Ventaja en tus Materias: Adelántate a los temas más complejos de tu carrera con un enfoque 100% práctico y mentoría entre compañeros.

---
## Proyectos del curso

- Control y Pilotaje de Drones
- Visión por Computadora
- Robótica Avanzada

---
## Paso 0: Instalar Git y Terminal

Antes de empezar cualquier proyecto, necesitas configurar la terminal y el control de versiones. 

### 🪟 En Windows

La terminal nativa de Windows da problemas con nuestros scripts. Instala Git Bash.

1. Descarga el instalador en [git-scm.com](https://git-scm.com/downloads).
2. Abre el archivo descargado.
3. Avanza en el instalador dejando todas las opciones por defecto.
4. Abre la aplicación "Git Bash" desde el menú de inicio.
5. Usa esta terminal para descargar repositorios y correr código.

### 🍎 En Mac

Mac ya trae una terminal Unix. Solo hace falta instalar Git.

1. Abre la aplicación "Terminal".
2. Verifica si ya tienes Git:
   ```bash
   git --version
   ```
3. Si no está instalado, el sistema pedirá instalar las herramientas de línea de comandos. Confirma la instalación.
4. Si no aparece el mensaje, fuerza la instalación ejecutando:
   ```bash
   xcode-select --install
   ```
5. Cierra la terminal y vuelve a abrirla.

**Para comprobar:** Abre tu terminal y ejecuta `git --version`. Si ves la versión, todo está listo.

---
## ¿Por dónde empiezo?

Para llevar un aprendizaje paso a paso y no saltarte conceptos clave, te recomendamos avanzar en este orden:

```text
[ 1. Tello ] ──> [ 2. Vision ] ──> [ 3. Control ] ──> [ 4. KalmanFilter ] ──> [ 5. Ros2 ]
  (Hardware)       (Percepción)       (Matemáticas)       (Estimación)       (Robótica Pro)
```
