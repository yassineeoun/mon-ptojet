# -*- coding: utf-8 -*-
import time
import sys
import RPi.GPIO as GPIO
import board
import adafruit_dht
import requests
from hx711 import HX711

# --- Configuration GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- Capteur Ultrason HC-SR04 ---
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# --- Capteur DHT22 ---
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# --- Capteur de poids HX711 ---
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
referenceUnit = 103
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tare HX711 done. Add weight now...")

# --- ThingSpeak ---
THINGSPEAK_API_KEY = "ZVM5FROBS6FXO77B"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

print("Initialisation... Patientez SVP.")
GPIO.output(TRIG, False)
time.sleep(2)

def cleanAndExit():
    print("Cleaning up GPIO...")
    GPIO.cleanup()
    dhtDevice.exit()
    print("Bye!")
    sys.exit()

try:
    while True:
        # --- Mesure de la distance ---
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        pulse_start = time.time()
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        
        pulse_end = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = round(pulse_duration * 17165, 1)
        print("Distance:", distance, "cm")

        # --- Temperature & Humidite ---
        try:
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} C    Humidity: {}%".format(temperature_c, humidity))
        except RuntimeError as error:
            print("Error DHT22 sensor:", error.args[0])
            temperature_c = None
            humidity = None
        except Exception as error:
            dhtDevice.exit()
            raise error

        # --- Poids ---
        try:
            weight = hx.get_weight(5)
            print("Weight: {:.2f} g".format(weight))
        except Exception as e:
            print("Error weight sensor:", e)
            weight = None

        hx.power_down()
        hx.power_up()

        # --- Envoi a ThingSpeak ---
        payload = {
            "api_key": THINGSPEAK_API_KEY,
            "field1": distance,
            "field2": temperature_c if temperature_c is not None else 0,
            "field3": humidity if humidity is not None else 0,
            "field4": weight if weight is not None else 0
        }

        try:
            response = requests.get(THINGSPEAK_URL, params=payload, timeout=5)
            if response.status_code == 200:
                print("Data sent to ThingSpeak.")
            else:
                print("Error sending data:", response.status_code)
        except requests.RequestException as e:
            print("Network error:", e)

        print("-" * 40)
        time.sleep(5)

except (KeyboardInterrupt, SystemExit):
    cleanAndExit()
