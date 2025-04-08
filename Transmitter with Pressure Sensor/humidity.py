from machine import Pin, I2C
import time
import bme280
from time import sleep_ms
 
i2c=I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)    #initializing the I2C method 

 

bme = bme280.BME280(i2c=i2c)
pressure = bme.values[1]
print(pressure)