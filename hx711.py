import RPi.GPIO as GPIO
from hx711 import hx711
GPIO.setmode(GPIO.BCM)
hx=hx711(dout_pin=6 ,pd_sck_pin=5)
hx.zero()
input('place know  weight on scale & press enter: ')
reading=hx.get_data_mean(reading=100)
know_weight_grams= input('enter the know weight in grams')
value=float(know_weight_grams)
ratio=reading/value
hx.set_scale_ratio(ratio)
while true:
    weight=hx.get_weight_mean()
    print(weight)
