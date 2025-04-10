import RPi.GPIO as GPIO
import time
import board
import adafruit_dht

# --- Configuration GPIO pour le capteur HC-SR04 ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# --- Initialisation du capteur DHT22 ---
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

print("Initialisation... Patientez SVP.")
GPIO.output(TRIG, False)
time.sleep(2)

try:
    while True:
        # --- Mesure distance avec HC-SR04 ---
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17165
        distance = round(distance, 1)

        print("Distance:", distance, "cm")

        # --- Mesure temperature et humidite avec DHT22 ---
        try:
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} F / {:.1f} C    Humidite: {}%".format(
                temperature_f, temperature_c, humidity
            ))
        except RuntimeError as error:
            print("Erreur capteur DHT22:", error.args[0])
        except Exception as error:
            dhtDevice.exit()
            raise error

        print("-" * 40)
        time.sleep(5)

except KeyboardInterrupt:
    print("Arret du script par l'utilisateur.")
    GPIO.cleanup()
    dhtDevice.exit()
