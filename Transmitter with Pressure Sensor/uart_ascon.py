###############################################################
#
#Importing Necessary Libraries
#
###############################################################
from machine import Pin, UART, I2C
from time import sleep_ms
import bme280 # For temperature sensor
import uos
import ucryptolib
from ucryptolib import aes
import uhashlib
import ascon

###############################################################
#
#Defining UART Class, remember to include the baudrate always
#
###############################################################
class RYLR896:
    def __init__(self, port_num, baudrate, tx_pin='', rx_pin=''):
        if tx_pin=='' and rx_pin=='':
            self._uart = UART(port_num,baudrate)
        else:
            self._uart = UART(port_num, baudrate, tx=tx_pin, rx=rx_pin)
                
    def cmd(self, lora_cmd):
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
                msg = msg + self._uart.read(self._uart.any()).decode('utf-8')
            print(msg.strip('\r\n'))
            
    
sleep_ms(500)
lora = RYLR896(1,115200) #Sets the UART port to be use
sleep_ms(500)
lora.set_addr(2)  # Sets the LoRa address


###############################################################
#
#Determing temperature
#
###############################################################

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(0,scl=Pin(21), sda=Pin(20),freq=400000)

# Create the sensor object using I2C
bme = bme280.BME280(i2c=i2c)
pres = bme.values[1]
print(pres)


###############################################################
#
# AES 256
#
###############################################################
#########ECB###########  
'''key = b'1234567890123456'
MODE_ECB=1
enc = ucryptolib.aes(key, MODE_ECB)
data=str(sensor.temperature)
data_bytes = data.encode()
encrypted=enc.encrypt(data_bytes + b'\x00' * ((16 - (len(data_bytes) % 16)) % 16))'''
#########################CHAT GPT#############################

key = b'\x82\xcbh^\xf5\xdfO\xf0\xc2+\xf1\x99\xe0\x9e\xaaV'
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data=b't'
variant="Ascon-128"

def encrypt_and_mac(plaintext, key, iv):
    plaintext = plaintext.encode('utf-8')
    padding = (block_size - len(plaintext) % block_size) * chr(block_size - len(plaintext) % block_size).encode('utf-8')
    plaintext = plaintext + padding
    cipher = ucryptolib.aes(key, MODE_CBC, iv)
    ciphertext = cipher.encrypt(plaintext)

    return (ciphertext)




def decrypt_and_verify(ciphertext, key, iv):

    cipher = ucryptolib.aes(key, MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    padding_len = plaintext[-1]
    plaintext = plaintext[:-padding_len]

    return plaintext.decode('utf-8')





while True:
    
    pressure = bme.values[1]
    plaintext=str(pressure)
    print('plaintext=',plaintext)
    plaintext=plaintext.encode('utf-8')
    ciphertext= ascon.ascon_encrypt(key,nonce, associate_data, plaintext, variant )
    lora.send_msg(3,str(ciphertext))
    print('ciphertext:',ciphertext)
    sleep_ms(7500)

    
  


