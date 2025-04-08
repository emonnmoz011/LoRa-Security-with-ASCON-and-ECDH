from machine import Pin, SPI
import adafruit_rfm9x

# Initialize the RFM9x LoRa radio
spi = SPI(0, baudrate=5000000)
cs = Pin(15, Pin.OUT, value=1)
reset = Pin(14, Pin.OUT, value=1)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)

# Define the message to be sent
message = "Hello from the Raspberry Pi Pico!"

# Send the message
rfm9x.send(message)

# Wait for the message to be sent
while not rfm9x.is_ready():
    pass

# Print a confirmation message
print("Message sent!")