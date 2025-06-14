# --- LIBRERÍAS MÍNIMAS ---
import board
import digitalio
import time

# --- CONFIGURACIÓN DE PINES ---
# Interruptor: Un lado a GP14, el otro a GND.
# El pin GP14 se configurará con una resistencia pull-up interna.
SWITCH_PIN = board.GP11

# LED a controlar: Usaremos el LED incorporado del Raspberry Pi Pico 1.
# El LED incorporado se encuentra en board.LED (generalmente GP25).
# No se necesita un pin para un LED externo en este caso.
ONBOARD_LED_PIN = board.LED # Se mantiene para claridad, aunque se usa directamente abajo.

# --- INICIALIZACIÓN ---

# Configuración del interruptor como ENTRADA con pull-up interno.
switch = digitalio.DigitalInOut(SWITCH_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP # Esto activa la resistencia pull-up interna

# Configuración del LED incorporado como SALIDA.
# Ahora controlamos el LED incorporado directamente.
onboard_led = digitalio.DigitalInOut(ONBOARD_LED_PIN)
onboard_led.direction = digitalio.Direction.OUTPUT
onboard_led.value = False # Asegúrate de que el LED esté apagado al inicio

print("Pico: Listo. Presiona el interruptor en GP14 para encender el LED incorporado.")

# --- BUCLE PRINCIPAL ---
while True:
    # Lee el estado del interruptor.
    # Con pull-up: True (HIGH) si no presionado, False (LOW) si presionado.
    if not switch.value: # Si el interruptor está PRESIONADO (es decir, el valor es False)
        onboard_led.value = True  # Enciende el LED incorporado
        # print("Interruptor PRESIONADO - LED ENCENDIDO") # Opcional para depurar
    else: # Si el interruptor está SOLTADO (es decir, el valor es True)
        onboard_led.value = False # Apaga el LED incorporado
        # print("Interruptor SOLTADO - LED APAGADO") # Opcional para depurar

    time.sleep(0.01) # Pequeña pausa para debouncing y eficiencia (ajusta si es necesario)

