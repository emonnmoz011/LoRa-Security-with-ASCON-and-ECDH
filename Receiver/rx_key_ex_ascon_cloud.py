from machine import Pin, UART, I2C
from time import sleep_ms
import utime
import ascon
import ubinascii
import network
import urequests as requests
import uasyncio as asyncio
import os
import sys

class RYLR896:
    def __init__(self, port_num, baudrate, tx='', rx=''):
        if tx=='' and rx=='':
            self._uart = UART(port_num)
        else:
            self._uart = UART(port_num, baudrate,tx=tx, rx=rx)

    def cmd(self, lora_cmd):
        self._uart.write('{}\r\n'.format(lora_cmd))
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
    
    def send_msg(self, addr, msg):
        self._uart.write('AT+SEND={},{},{}\r\n'.format(addr,len(msg),msg))
        while(self._uart.any()==0):
            pass
        reply = self._uart.readline()
        print(reply.decode().strip('\r\n'))
    
    def read_msg(self):
        msg=''
        if self._uart.any() == 0:
            print('Nothing to show.')
        else:
            
            while self._uart.any():
                msg = msg + self._uart.read(self._uart.any()).decode()
            msg = msg.strip('\r\n')
            msg = msg.split(',')
        if len(msg) > 2:  # Add this check to ensure the list has enough elements
            return msg[2]
        else:
            print('Invalid message format.')
        
    def read_msg_alt(self):
        msg_alt=''
        if self._uart.any() == 0:
            print('Nothing to show.')
        else:
            
            while self._uart.any():
                msg_alt = msg_alt + self._uart.read(self._uart.any()).decode()
            msg_alt = msg_alt.strip('\r\n')
            msg_alt = msg_alt.split(',')
        if len(msg_alt) > 2:  # Add this check to ensure the list has enough elements
            return msg_alt[2]
        else:
            print('Invalid message format.')

    def read_msg_secure(self, key, nonce, associate_data, variant):
        if self._uart.any() == 0:
            print('Nothing to show.')
            return None, None
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
                    return None, None

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
                encrypted_message_bytes = ubinascii.a2b_base64(encrypted_message.encode())
                decrypted_message = ascon.ascon_decrypt(key, nonce, associate_data, encrypted_message_bytes, variant)
                return sender_addr, decrypted_message.decode('ascii')

            except Exception as e:
                print("Error while parsing message:", e)
                return None, None

        sleep_ms(100)  # Add a small delay between read attempts
        


# Adafruit IO credentials
wifi_ssid = "emon"
wifi_password = "emonnmoz011"
aio_key = "aio_alRs400wGmZghdQi5pp9WRtUmdbe"
username = "emonnmoz"
feed_temperature = "temperature"
feed_pressure = "pressure"

async def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(wifi_ssid, wifi_password)
    while not sta_if.isconnected():
        print(".", end = "")
        await asyncio.sleep(1)
    print("Connected to Wi-Fi")

async def send_to_adafruit_io(feed_name, value):
    url = f'https://io.adafruit.com/api/v2/{username}/feeds/{feed_name}/data'
    body = {'value': str(value)}
    headers = {'X-AIO-Key': aio_key, 'Content-Type': 'application/json'}
    try:
        r = requests.post(url, json=body, headers=headers)
        print(f"Sent to {feed_name}: {value}")
    except Exception as e:
        print(f"Error sending to {feed_name}: {e}")

async def main_loop():
    lora = RYLR896(2, 115200, rx=27, tx=26)  # Sets the UART port to be used
    sleep_ms(1000)
    lora.set_addr(3)
    sleep_ms(1000)
    lora.set_rf_parameters(10,7,1,4)
    sleep_ms(1000)
    lora.set_uart_baud_rate(115200)
    sleep_ms(1000)
    lora.set_network_id(3)
    sleep_ms(1000)# Sets the LoRa address

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

    rx_private_key = generate_private_key(p)
    rx_public_key = calculate_public_key(g, rx_private_key, p)

    tx_public_key=None

    while True:
        tx_public_key=lora.read_msg()
        if tx_public_key is None:
            print("No public key found from the transmitter, waiting...")
            utime.sleep(1)
            continue
        else:
            print('Public key found fromt the transmitter sending Acknowledgement')
            print('transmitter public key:', tx_public_key)
            utime.sleep(1)
            lora.send_msg(1,'ACK')
            utime.sleep(1)
            break
            
    final=None

    while True:
        lora.send_msg(1,str(rx_public_key))
        utime.sleep(2.5)
        final=lora.read_msg_alt()
        utime.sleep(1)
        if final is not None:
            print("Receiver public key sent successfully")
            utime.sleep(1)
            break
        else:
            print("ACK not received from the transmitter")
            print("Sending the rx public key again...")
            utime.sleep(1)
            continue
        
        
            
    tx_public_key=int(tx_public_key)

    rx_shared_secret_key = calculate_shared_secret_key(tx_public_key, rx_private_key, p)
    shared_secret_key = rx_shared_secret_key.to_bytes(16, sys.byteorder)
    print("Shared Secret Key:",rx_shared_secret_key)
    print("Converting the secret key to bytes")
    print("Common Secret key for the tx and rx:",shared_secret_key)

    key = shared_secret_key
    nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
    associate_data = b't'
    variant = "Ascon-128"

    
    while True:
        sender_addr, decrypted_message = lora.read_msg_secure(key, nonce, associate_data, variant)
        if sender_addr and decrypted_message:
            if sender_addr == 1:  # Temperature sensor
                print("Received temperature data:", decrypted_message)
                temperature = float(decrypted_message.rstrip('C'))
                asyncio.create_task(send_to_adafruit_io(feed_temperature, temperature))
            elif sender_addr == 2:  # Air pressure sensor
                print("Received air pressure data:", decrypted_message)
                pressure = float(decrypted_message.rstrip('hPa'))
                asyncio.create_task(send_to_adafruit_io(feed_pressure, pressure))
                
            else:
                print("Received data from unknown sender:", decrypted_message)
        await asyncio.sleep(10)
    

asyncio.run(connect_wifi())
asyncio.run(main_loop())

