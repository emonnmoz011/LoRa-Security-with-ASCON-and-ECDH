####################################################
#
# Bringing all the necessary libraries
#
####################################################

from machine import Pin, UART, I2C
from time import sleep_ms
import ahtx0 # importing the temperature sensor library
import uos
import ucryptolib
from ucryptolib import aes
import ubinascii
import ascon
from time import sleep
import os
import sys

#####################################################
#
# Defining class for LoRa module
#
#####################################################

class RYLR896:
    
    def __init__(self, port_num, baudrate, tx_pin='', rx_pin=''): # Settting LoRa Parameters
        if tx_pin=='' and rx_pin=='':
            self._uart = UART(port_num,baudrate)
        else:
            self._uart = UART(port_num, baudrate, tx=tx_pin, rx=rx_pin)
                
    def cmd(self, lora_cmd): # Sending commands to receiver LoRa 
        self._uart.write('{}\r\n'.format(lora_cmd))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
    
    def test(self):
        self._uart.write('AT\r\n')
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        

    def set_addr(self, addr):
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        print('Address set to:{}\r\n'.format(addr))
        


    def send_msg_base64(self, addr, msg):
        msg_base64 = ubinascii.b2a_base64(msg).rstrip(b'\n')
        msg_length = len(msg_base64)
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr, msg_length, msg_base64.decode()))
        while(self._uart.any() == 0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        
        
    def send_msg(self, addr, msg):
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))

    def read_msg(self):
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()
            msg=msg.strip('\r\n')
            msg=msg.split(',')
            print(msg[2])

    def read_msg_secure(self, key, nonce, associate_data, variant):
        if self._uart.any() == 0:
            print('Nothing to show.')
            return None, None, None, None
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()

            msg = msg.strip('\r\n')
            print(msg)

            try:
                # Parsing the received data
                parts = msg.split(',')
                if len(parts) < 5:
                    print("Unexpected message format")
                    return None, None, None, None

                sender_addr = int(parts[0].split('=')[-1])  # Extract sender address
                message_length = parts[1]
                encrypted_message = parts[2]
                rssi = parts[3]
                snr = parts[4]

                # Printing the values separately
                print("Sender Address:", sender_addr)
                print("Message Length:", message_length)
                print("Encrypted Message:", encrypted_message)
                print("SNR:", snr)
                print("RSSI:", rssi)

                # Decrypting the encrypted message
                # Decrypting the encrypted message
                encrypted_message_bytes = ubinascii.a2b_base64(encrypted_message.encode())
                decrypted_message = ascon.ascon_decrypt(key, nonce, associate_data, encrypted_message_bytes, variant)
                print("Decrypted message:", decrypted_message)  # Add this line

                return sender_addr, decrypted_message.decode('utf-8'), snr, rssi

            except Exception as e:
                print("Error while parsing message:", e)
                return None, None, None, None

        sleep_ms(100)  # Add a small delay between read attempts
            
    
sleep_ms(1000)
lora = RYLR896(1, 115200)  # Sets the UART port to be used
sleep_ms(2000)
lora.set_addr(1)  # Sets the LoRa address
sleep_ms(1000)




'''# Define the shared prime (p) and shared base (g)
p = 0xFFFFFFFB  # Large prime number
g = 5  # Primitive root modulo p

# Generate a random private key
def generate_private_key(p):
    return int.from_bytes(os.urandom(16), sys.byteorder) % (p - 1)

# Calculate the public key
def calculate_public_key(g, private_key, p):
    return pow(g, private_key, p)

# Calculate the shared secret key
def calculate_shared_secret_key(public_key, private_key, p):
    return pow(public_key, private_key, p)

tx_private_key = generate_private_key(p)
tx_public_key = calculate_public_key(g, tx_private_key, p)
print('private key:',tx_private_key)
print('public key:',tx_public_key)'''


###############################################################
#
#Determing temperature
#
###############################################################

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(0,scl=Pin(21), sda=Pin(20),freq=400000)

# Create the sensor object using I2C
sensor = ahtx0.AHT10(i2c)
print("Temperature: %0.2f C" % sensor.temperature)
#print("Humidity: %0.2f hPa" % sensor.relative_humidity)



key = b'\x82\xcbh^\xf5\xdfO\xf0\xc2+\xf1\x99\xe0\x9e\xaaV'
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data=b't'
variant="Ascon-128"



while True:
    
   
    plaintext="%0.2f" % sensor.temperature
    plaintext=str(plaintext)
    plaintext=plaintext.encode('utf-8')
    print('Original Data:',plaintext)
    ciphertext= ascon.ascon_encrypt(key,nonce, associate_data, plaintext, variant )
    lora.send_msg_base64(3, ciphertext)
    print('Data after enrcyption:', ciphertext)
    sleep_ms(2000)

    
  

