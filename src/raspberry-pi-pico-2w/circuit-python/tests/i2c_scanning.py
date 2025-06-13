import board
import busio
import time

# --- Configura el Bus I2C ---
# Para la Raspberry Pi Pico, el bus I2C0 de hardware usa los pines:
# SCL (Reloj) = GP1 (Pin físico 2 del Pico)
# SDA (Datos) = GP0 (Pin físico 1 del Pico)
# Si estás usando el Bus I2C1, sería: busio.I2C(board.GP3, board.GP2)
i2c = busio.I2C(board.GP1, board.GP0)

print("Iniciando escaneo I2C...")

# Intenta bloquear el bus I2C. Esto asegura que ningún otro proceso lo use mientras escaneamos.
while not i2c.try_lock():
    pass # Espera activa hasta que el bus esté disponible

try:
    # Realiza el escaneo del bus I2C
    found_devices = i2c.scan()

    if not found_devices:
        print("No se encontraron dispositivos I2C en el bus. Revisa tus conexiones.")
    else:
        print("¡Dispositivos I2C encontrados en las direcciones (hexadecimal):")
        for address in found_devices:
            print(f"  - 0x{address:x}") # Imprime la dirección en formato hexadecimal

finally:
    # ¡Importante! Siempre desbloquea el bus I2C cuando hayas terminado.
    i2c.unlock()

print("Escaneo I2C completado. Reiniciando en 5 segundos...")
time.sleep(5) # Pausa para que puedas ver la salida antes de que el Pico se reinicie