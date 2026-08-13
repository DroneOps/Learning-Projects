'''
Un paquete de ros2 para controlar la simulación turlesim con un controlador PI
'''

import math # libreria matemática de python.
#librerias de ROS2 para Python
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose # tipo de mensaje personalizado que contiene la posición y orientación de la tortuga. 
from geometry_msgs.msg import Twist # tipo de mensaje que contiene velocidad lineal y angular. Es util para cualquier robot que se mueva en un plano, como la tortuga de turtlesim. 


class ControlTurtleSim(Node): #Primero decimos que la clase hereda de Node, que es la clase base para todos los nodos en ROS2
    def __init__(self): #definimos el constructor.
        super().__init__('Control') # Llamamos al constructor de la clase base Node con el nombre del nodo 'Control'

        ''' Suscribirse a la posición de la tortuga y publicar comandos de velocidad '''
        self.position = self.create_subscription(
            Pose, "/turtle1/pose", self.control_callback, 10 # aqui le pasas el tipo de mensaje, el topic al que te suscribes, la función de callback y el tamaño del buffer
        ) 
        self.vel = self.create_publisher(Twist, '/turtle1/cmd_vel', 10) # aqui le pasas el tipo de mensaje, el topic al que publicas y el tamaño del buffer

        # Definir la posición objetivo de la tortuga
        self.goal_x = 0.0
        self.goal_y = 0.0

        # Ganancias del controlador PI
        self.kp_lin = 1.0 # ganancia proporcional para la velocidad lineal ajusta esto ayuda a la fuerza de la tortuga para moverse hacia el objetivo.
        self.ki_lin = 0.2 # ganancia integral para la velocidad lineal ajusta esto ayuda a la tortuga a corregir el error acumulado y evitar que se quede atascada en un punto.
        self.kp_ang = 4.0 # ganancia proporcional para la velocidad angular ajusta esto ayuda a la tortuga a girar hacia el objetivo.

        # Inicializamos las variables para la integral
        self.integral = 0.0 #inicializamos en 0.0 para ir acumulando el error
        self.prev_time = self.get_clock().now() # usamos el tiempo para calcular la diferencia de tiempo para la integral

    def control_callback(self, msg):
        x = msg.x # descomprimimos del mensaje las variables de posición y orientación de la tortuga
        y = msg.y
        theta = msg.theta # este es el angulo de orientación de la tortuga en radianes

        dx = self.goal_x - x # aqui calculamos la distancia entre la posición actual y la posición objetivo
        dy = self.goal_y - y
        distance = math.hypot(dx, dy) # se calcula la distancia euclidiana entre la posición actual y la posición objetivo esto es el error de posición

        angle_to_goal = math.atan2(dy, dx) # aqui calculamos el ángulo entre la posición actual y la posición objetivo, esto es el error de orientación
        angle_error = self._normalize_angle(angle_to_goal - theta) # el angulo de error es el angulo del objetivo menos el angulo de la tortuga.

        '''
        Nota: todo esto se saca con trigonometría, se usa atan2 y no atan porque atan2 devuelve el ángulo en el cuadrante correcto, 
        mientras que atan solo devuelve el ángulo en el primer y cuarto cuadrante.

        Se normaliza el ángulo de error para que esté entre -pi y pi, esto es importante porque si el ángulo de error es mayor que pi o menor que -pi,
        la tortuga girará en la dirección equivocada. Por ejemplo, si el ángulo de error es 3.14 radianes, la tortuga girará en sentido antihorario, cuando debería girar en sentido horario.
        
        '''

        now = self.get_clock().now() # ahora obtenemos el tiempo actual
        dt = (now - self.prev_time).nanoseconds / 1e9 
        '''
        El diferencial de tiempo siguiendo la regla de la integral que es el tiempo actual menos el tiempo anterior.
        Esto es importante para la integral, ya que la integral es el área bajo la curva del error, y el área bajo la curva es el error multiplicado por el tiempo.
        Esto puede ser costoso computacionalmente, pero es necesario para que el controlador PI funcione correctamente.
        Se pueden usar otras técnicas para calcular la integral, como métodos numéricos para reducir el costo computacional.

        '''
        if dt <= 0.0: # si el diferencial de tiempo es menor o igual a 0, lo establecemos en un valor muy pequeño para evitar la división por cero.
            dt = 1e-6

        self.integral += distance * dt # calculamos la integral del error de posición, que es el acumulado de los errores por el tiempo.

        linear_speed = self.kp_lin * distance + self.ki_lin * self.integral # ahora es momento de calcular la velociad lineal siguiendo la formula de un contol PI V = Kp * error + Ki * integral(error).
        angular_speed = self.kp_ang * angle_error # lo mismo para la velocidad angular.

        if distance < 0.05: # este es un threshold para que no oscile al rededor del punto, se puede ajustar para intentar que la tortuga se detenga en el punto objetivo, pero si es muy pequeño, la tortuga puede oscilar alrededor del punto objetivo.
            linear_speed = 0.0
            angular_speed = 0.0

        cmd = Twist() # finalmente armamos el mensaje para mandarlo por medio del topic /turtle1/cmd_vel, que es el topic que la tortuga escucha para moverse.
        cmd.linear.x = float(linear_speed) # el mensaje Twist tiene dos componentes, la lineal y la angular.
        cmd.angular.z = float(angular_speed)
        self.vel.publish(cmd) # publicamos el mensaje por medio del publicador vel que definimos en el constructor.

        self.get_logger().info(
            f'dist={distance:.3f} ang_err={angle_error:.3f} lin={linear_speed:.3f} ang={angular_speed:.3f}' # mostramos el mensaje en la terminal para ver el error de posición, el error de orientación, la velocidad lineal y la velocidad angular.
        )

        self.prev_time = now # actualizamos el tiempo anterior para la siguiente iteración del callback.

    def _normalize_angle(self, angle) : # esta es la funcion para normalizar el ángulo. Esto hace que la corrección sea más rapida evitando giros complejos.
        while angle > math.pi: # si el angulo es mayor a pi, le restamos 2*pi hasta que esté entre -pi y pi. 
            angle -= 2 * math.pi 
        while angle <= -math.pi:
            angle += 2 * math.pi
        return angle # retornamos un angulo posible para la totuga.


def main(args=None): # este es el main del nodo, que es el que se ejecuta cuando se corre el nodo.
    rclpy.init(args=args) # rcply es la libreria de ROS2 para Python, y se inicializa con los argumentos que se le pasen al nodo.

    control_turtlesim = ControlTurtleSim() # creamos una instancia de la clase ControlTurtleSim, que es el nodo que controla la tortuga.

    rclpy.spin(control_turtlesim) # le pasamos la instancia del nodo a rclpy.spin, que es el que mantiene el nodo en ejecución hasta que se cierre.

    # cuando termine la ejecución del nodo, se destruye la instancia del nodo y se cierra rclpy. 
    ControlTurtleSim.destroy_node() # destruimos el nodo para liberar los recursos que se usaron para crearlo, esto es importante para evitar fugas de memoria y otros problemas.

    rclpy.shutdown() 


if __name__ == '__main__': # si este archivo se ejecuta como un script, se llama a la función main() para iniciar el nodo.
    main() # esta funcion se pone en el setup.py para que se pueda ejecutar el nodo desde la terminal con el comando ros2 run ControlTurtlesim control.
