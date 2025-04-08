from machine import Pin, UART, I2C
from time import sleep_ms
import utime
import ascon
import ubinascii
import network
import urequests as requests
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
            
            msg = msg.strip('\r\n')
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

key = b'\x82\xcbh^\xf5\xdfO\xf0\xc2+\xf1\x99\xe0\x9e\xaaV'
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data = b't'
variant = "Ascon-128"

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

rx_private_key = generate_private_key(p)
rx_public_key = calculate_public_key(g, rx_private_key, p)
rx_shared_secret_key = calculate_shared_secret_key(tx_public_key, rx_private_key, p)
shared_secret_key = rx_shared_secret_key.to_bytes(16, sys.byteorder)


# Set the name of the CSV file
csv_file_name = "data.csv"

# Check if the CSV file exists, create it if not
try:
    with open(csv_file_name, 'r') as f:
        pass
except OSError:
    with open(csv_file_name, 'w') as f:
        f.write("sender,decrypted_message\n")

expected_data_type = 1

while True:
    sender, decrypted_message, snr, rssi = lora.read_msg_secure(key, nonce, associate_data, variant)

    if sender is not None and decrypted_message is not None:
        if sender == expected_data_type:
            # Save the data to the CSV file
            with open(csv_file_name, 'a') as f:
                f.write(f"{sender},{decrypted_message}\n")

            # Print the data to the REPL
            if sender == 1:  # Transmitter 1
                print("Received temperature data:", decrypted_message)
                print("################################################")
                expected_data_type = 2  # Switch to expecting air pressure data
            elif sender == 2:  # Transmitter 2
                print("Received air pressure data:", decrypted_message)
                print("################################################")
                expected_data_type = 1  # Switch to expecting temperature data

    sleep_ms(4700)


