##########################################################################
#
# Importing the necessary libraries
#
##########################################################################

from machine import Pin, UART, I2C
from time import sleep_ms
import ahtx0 # importing the temperature sensor library
import uos
import ucryptolib
from ucryptolib import aes
import ubinascii
import ascon
import utime
import os
import sys


##########################################################################
#
# Defining working class for duplex LoRa communication
#
##########################################################################
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
    
    def test(self): # Testing if the LoRa module is connected with the raspberry pi
        self._uart.write('AT\r\n')
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        

    def set_addr(self, addr): # Setting the initial address of LoRa
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        print('Address set to:{}\r\n'.format(addr))
        
    def set_rf_parameters(self, sf, bw, cr, pp): #Setting Parameters for LoRa module
        if 7 <= sf <= 12 and 0 <= bw <= 9 and 1 <= cr <= 4 and 4 <= pp <= 7:
            #sf = Spreading Factor ##bw = Bandwidth ###cr = Coding Rate ####pp= Program Preamble 
            self._uart.write('AT+PARAMETER={},{},{},{}\r\n'.format(sf, bw, cr, pp))
            while(self._uart.any()==0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('RF parameters set to: SF={}, BW={}, CR={}, PP={}\r\n'.format(sf, bw, cr, pp))
        else:
            print('Invalid parameters. Please check the values.')
            
    def set_uart_baud_rate(self, baud_rate): # setting up the baudrate for LoRa
        valid_baud_rates = [300, 1200, 4800, 9600, 19200, 28800, 38400, 57600, 115200]
        if baud_rate in valid_baud_rates:
            self._uart.write('AT+IPR={}\r\n'.format(baud_rate))
            while(self._uart.any()==0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('UART baud rate set to: {}\r\n'.format(baud_rate))
        else:
            print('Invalid baud rate. Please use a valid baud rate from the following: {}'.format(valid_baud_rates))
            
    def set_network_id(self, network_id): # Selecting a unique network id to maintain privacy
        if 0 <= network_id <= 16:
            self._uart.write('AT+NETWORKID={}\r\n'.format(network_id))
            while(self._uart.any()==0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('Network ID set to: {}\r\n'.format(network_id))
        else:
            print('Invalid network ID. Please enter a value between 0 and 16.')

            
    def get_unique_id(self): # To display the unique id of the lora module
        self._uart.write('AT+UID?\r\n')
        while(self._uart.any() == 0):
            pass
        reply = self._uart.readline()
        reply = reply.decode().strip('\r\n')
        print('Full response: {}'.format(reply))

        uid = None
        if reply.startswith('+UID='):
            uid = reply.split('=')[1]
            print('Unique ID: {}\r\n'.format(uid))

        return uid
        
    def send_msg_base64(self, addr, msg): # For sending message with base64 encoding
        msg_base64 = ubinascii.b2a_base64(msg).rstrip(b'\n')
        msg_length = len(msg_base64)
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr, msg_length, msg_base64.decode()))
        while(self._uart.any() == 0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))        
        

    def send_msg(self, addr, msg): # This can also send message simply but used for key exchange
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))

    def read_msg(self): # Used for key exchange
        msg = ''
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()
            msg=msg.strip('\r\n')
            msg=msg.split(',')
        if len(msg) > 2:  # Add this check to ensure the list has enough elements
            return msg[2]
        else:
            print('Invalid message format.')

    def read_msg_alt(self): # Used for key exchange
        msg = ''
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode()
            msg=msg.strip('\r\n')
            msg=msg.split(',')
        if len(msg) > 2:  # This check ensures the list has enough elements
            return msg[2]
        else:
            print('Invalid message format.')
            
##########################################################################
#
# Initiating the LoRa module
#
##########################################################################

sleep_ms(1000)
lora = RYLR896(1, 115200)  # 1= UART port, 115200 = Baudrate
sleep_ms(2000)
lora.set_addr(1)  # Sets the LoRa address
sleep_ms(1000)
lora.set_rf_parameters(10,7,1,4)
sleep_ms(1000)  
lora.set_uart_baud_rate(115200)
sleep_ms(1000)
lora.set_network_id(3)
sleep_ms(1000)


##########################################################################
#
# Diffie Hellman Key exchange
#
##########################################################################

# Define the shared prime (p) and shared base (g)
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



ack_msg=None

while True:

    lora.send_msg(3,str(tx_public_key)) # Sending public key to receiver
    sleep_ms(3300)
    ack_msg=lora.read_msg() # Getting the acknowledgement from the receiver that the tx public key is received properly
    if ack_msg is not None:
        print("ACK received")
        utime.sleep(1)
        break
    else:
        print("Acknowledgement not received. Sending the public key again")
        utime.sleep(1)
        continue

rx_public_key=None


while True:
    rx_public_key=lora.read_msg_alt()
    utime.sleep(2)
    if rx_public_key is not None:
        print("Public key received from the receiver")
        sleep_ms(500)
        print("Sedning Acknowledgement to the receiver")
        utime.sleep(7)
        lora.send_msg(3,'ACK')
        print("Receiver public key:", rx_public_key)
        utime.sleep(1)
        break
    else:
        print("Waiting for the public key from the receiver")
        utime.sleep(1)
        continue
    
rx_public_key=int(rx_public_key)

tx_shared_secret_key = calculate_shared_secret_key(rx_public_key, tx_private_key, p)
print('Shared Secret key of Transmitter:',tx_shared_secret_key)
print('Converting the shared secret key to bytes')
shared_secret_key = tx_shared_secret_key.to_bytes(16, sys.byteorder)
print("Common Shared Secret Key:",shared_secret_key)

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(0,scl=Pin(21), sda=Pin(20),freq=400000)

# Create the sensor object using I2C
sensor = ahtx0.AHT10(i2c)
print("Temperature: %0.2f C" % sensor.temperature)
#print("Humidity: %0.2f hPa" % sensor.relative_humidity)

key = shared_secret_key
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data=b't'
variant="Ascon-128"

while True:
    
   
    plaintext="%0.2fC" % sensor.temperature
    plaintext=str(plaintext)
    plaintext=plaintext.encode('utf-8')
    print('Original Data:',plaintext)
    ciphertext= ascon.ascon_encrypt(key,nonce, associate_data, plaintext, variant )
    lora.send_msg_base64(3, ciphertext)
    print('Data after enrcyption:', ciphertext)
    sleep_ms(9000)