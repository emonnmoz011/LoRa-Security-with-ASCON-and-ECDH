###############################################################
#
#Importing Necessary Libraries
#
###############################################################
from machine import Pin, UART, I2C
from time import sleep_ms
import bme280 # For atm pressure sensor
import uos
import ucryptolib
from ucryptolib import aes
import uhashlib
import ascon
import ubinascii

###############################################################
#
#Defining UART Class, remember to include the baudrate always
#
###############################################################
class RYLR896:
    def __init__(self, port_num, baudrate, tx_pin='', rx_pin=''): #function for initiating lora
        if tx_pin=='' and rx_pin=='':
            self._uart = UART(port_num,baudrate)
        else:
            self._uart = UART(port_num, baudrate, tx=tx_pin, rx=rx_pin)
                
    def cmd(self, lora_cmd): #function for sending command to check the UART for rx lora
        self._uart.write('{}\r\n'.format(lora_cmd))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
    
    def test(self): #testing if the lora module is functioning
        self._uart.write('AT\r\n')
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))

    def set_addr(self, addr): #defining the address of the lora module
        self._uart.write('AT+ADDRESS={}\r\n'.format(addr))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        print('Address set to:{}\r\n'.format(addr))
        
    def set_rf_parameters(self, sf, bw, cr, pp):
        if 7 <= sf <= 12 and 0 <= bw <= 9 and 1 <= cr <= 4 and 4 <= pp <= 7:
            self._uart.write('AT+PARAMETER={},{},{},{}\r\n'.format(sf, bw, cr, pp))
            while(self._uart.any()==0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('RF parameters set to: SF={}, BW={}, CR={}, PP={}\r\n'.format(sf, bw, cr, pp))
        else:
            print('Invalid parameters. Please check the values.')

    def set_network_id(self, network_id):
        if 0 <= network_id <= 16:
            self._uart.write('AT+NETWORKID={}\r\n'.format(network_id))
            while(self._uart.any()==0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('Network ID set to: {}\r\n'.format(network_id))
        else:
            print('Invalid network ID. Please enter a value between 0 and 16.')
            
    def set_uart_baud_rate(self, baud_rate):
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

    def set_output_power(self, power):
        if 0 <= power <= 22:
            self._uart.write('AT+CRFOP={}\r\n'.format(power))
            while(self._uart.any() == 0):
                pass
            reply = self._uart.readline()
            print(reply.decode().strip('\r\n'))
            print('Output power set to: {} dBm\r\n'.format(power))
        else:
            print('Invalid output power. Please enter a value between 0 and 22.')
            
            
    def get_unique_id(self):
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


    def send_msg_base64(self, addr, msg): #sending message
        msg_base64 = ubinascii.b2a_base64(msg).rstrip(b'\n')
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr, len(msg_base64), msg_base64.decode()))
        while(self._uart.any() == 0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
        
    def read_msg(self): #receiving message
        if self._uart.any()==0:
            print('Nothing to show.')
        else:
            msg = ''
            while(self._uart.any()):
                msg = msg + self._uart.read(self._uart.any()).decode('utf-8')
            print(msg.strip('\r\n'))
            
    
sleep_ms(1000)
lora = RYLR896(1,115200) #Sets the UART port to be use
sleep_ms(2000)
lora.set_addr(2)
sleep_ms(1000)
lora.set_rf_parameters(10,7,1,4)
sleep_ms(1000)
lora.set_uart_baud_rate(115200)
sleep_ms(1000)
lora.set_network_id(3)
sleep_ms(1000)
#lora.set_output_power(20)
#sleep_ms(1000)


###############################################################
#
#Determing temperature
#
###############################################################

i2c = I2C(0,scl=Pin(21), sda=Pin(20),freq=400000) # creating an I2C object on GPIO 21 and 20


bme = bme280.BME280(i2c=i2c) # Create the sensor object using I2C
pres = bme.values[1]
print(pres)

###############################################################
#
# Setting the parameters for ASCON encryption
#
###############################################################

key = b'\x82\xcbh^\xf5\xdfO\xf0\xc2+\xf1\x99\xe0\x9e\xaaV'
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data=b't'
variant="Ascon-128"

###############################################################
#
# sending data in an infinite loop
#
###############################################################


'''while True:
    
    pressure = bme.values[1]
    plaintext=str(pressure)
    plaintext=plaintext.encode('utf-8')
    print('plaintext=',plaintext)
    ciphertext= ascon.ascon_encrypt(key,nonce, associate_data, plaintext, variant )
    lora.send_msg_base64(3, ciphertext)
    print('ciphertext:', ciphertext)
    sleep_ms(9000)'''
