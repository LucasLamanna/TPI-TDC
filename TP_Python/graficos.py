import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time

# Constantes del sistema
Kp = 1.0  # Ganancia proporcional
Ki = 0.1  # Ganancia integral
t_setpoint = 30.0  # Temperatura deseada (setpoint)

# Variables iniciales del sistema
t_actual = 20.0  # Temperatura inicial
error = 0.0
integral = 0.0
output_pi = 0.0
perturbacion_e = 2.0  # Perturbación en la entrada
perturbacion_s = 1.0  # Perturbación en la salida
perturbacion = 0.0  # Perturbación adicional

# Parámetros de simulación
ts = 0.1  # Intervalo de muestreo (segundos)

# Almacenamiento de datos para el gráfico
tiempo = []
temperaturas_actuales = []
temperaturas_deseadas = []
errores = []
salidas_pi = []
perturbaciones = []

# Función para el controlador PI
def controlador_pi(setpoint, temperatura_actual):
    global integral

    # Cálculo del error
    error = setpoint - temperatura_actual

    # Componente integral
    integral += error * ts

    # Salida del controlador PI
    salida = Kp * error + Ki * integral
    return salida, error

# Función para permitir entrada de datos por teclado
def entrada_datos():
    global t_actual, Kp, Ki, perturbacion
    while True:
        try:
            opcion = input("Ingrese 'T' para nueva temperatura, 'KP' para nuevo Kp, 'KI' para nuevo Ki: ").strip().upper()
            if opcion == 'T':
                nueva_temp = float(input("Ingrese nueva temperatura: "))
                t_actual = nueva_temp
            elif opcion == 'KP':
                nuevo_kp = float(input("Ingrese nuevo valor de Kp: "))
                Kp = nuevo_kp
            elif opcion == 'KI':
                nuevo_ki = float(input("Ingrese nuevo valor de Ki: "))
                Ki = nuevo_ki
            else:
                print("Opción no válida. Intente nuevamente.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

# Función para reiniciar la perturbación a cero tras 3 segundos
def reset_perturbacion():
    global perturbacion
    time.sleep(3)
    perturbacion = 0.0

# Configuración del gráfico
fig, ax = plt.subplots()
ax.set_title("Controlador PI - Temperatura en tiempo real")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Valor")
ax.set_ylim(-10, 40)  # Ajuste del rango para incluir error y salida PI
linea_temp_actual, = ax.plot([], [], label="Temperatura actual")
linea_temp_deseada, = ax.plot([], [], label="Temperatura deseada")
linea_error, = ax.plot([], [], label="Error")
linea_salida_pi, = ax.plot([], [], label="Salida PI")
linea_perturbacion, = ax.plot([], [], label="Perturbación")
ax.legend()

# Función de actualización para el gráfico
def actualizar(frame):
    global t_actual, output_pi, perturbacion

    # Simulación del controlador PI
    output_pi, error = controlador_pi(t_setpoint, t_actual)

    # Variación de la temperatura actual cada 1 segundo
    if frame % int(1 / ts) == 0:
        t_actual += np.random.uniform(-0.5, 0.5)  # Pequeña variación aleatoria

    # Actualización de la perturbación
    perturbacion = abs(t_setpoint - t_actual)
    threading.Thread(target=reset_perturbacion, daemon=True).start()

    # Actualización de la temperatura actual (simulación del sistema)
    t_actual += (output_pi - perturbacion_s + perturbacion) * ts

    # Registro de datos
    tiempo.append(frame * ts)
    temperaturas_actuales.append(t_actual)
    temperaturas_deseadas.append(t_setpoint)
    errores.append(error)
    salidas_pi.append(output_pi)
    perturbaciones.append(perturbacion)

    # Actualización de las líneas del gráfico
    linea_temp_actual.set_data(tiempo, temperaturas_actuales)
    linea_temp_deseada.set_data(tiempo, temperaturas_deseadas)
    linea_error.set_data(tiempo, errores)
    linea_salida_pi.set_data(tiempo, salidas_pi)
    linea_perturbacion.set_data(tiempo, perturbaciones)

    # Ajuste dinámico del eje x
    ax.set_xlim(0, max(tiempo) + 1)

    return linea_temp_actual, linea_temp_deseada, linea_error, linea_salida_pi, linea_perturbacion

# Iniciar hilo para entrada de datos por teclado
threading.Thread(target=entrada_datos, daemon=True).start()

# Animación en tiempo real
anim = FuncAnimation(fig, actualizar, interval=ts * 1000, blit=True)
plt.show()
