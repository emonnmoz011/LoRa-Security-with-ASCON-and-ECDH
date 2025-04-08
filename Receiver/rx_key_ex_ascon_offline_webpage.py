from machine import Pin, UART, I2C
import utime
import ascon
import ubinascii
import network
import urequests as requests
import os
import sys
import socket

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

                encrypted_message_bytes = ubinascii.a2b_base64(encrypted_message.encode())
                decrypted_message = ascon.ascon_decrypt(key, nonce, associate_data, encrypted_message_bytes, variant)
                print("Decrypted message:", decrypted_message)  # Add this line

                return sender_addr, decrypted_message.decode('utf-8'), snr, rssi

            except Exception as e:
                print("Error while parsing message:", e)
                return None, None, None, None

        sleep_ms(100)  # Add a small delay between read attempts

lora = RYLR896(2, 115200, rx=27, tx=26)  # Sets the UART port to be used
utime.sleep(1)
lora.set_addr(3)
utime.sleep(7)



key = b'\x82\xcbh^\xf5\xdfO\xf0\xc2+\xf1\x99\xe0\x9e\xaaV'
nonce = b'W\n\xf8\x1c\x91((\xbe;\x1d\x10\xc3`\xf2R-'
associate_data = b't'
variant = "Ascon-128"

utime.sleep(3)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-WeatherStation', password='commonpurpose123')
print('network config:', ap.ifconfig())

utime.sleep(3)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80)) 
s.listen(5)  

utime.sleep(3)
def web_page(temp):
    with open('weather_station.html', 'r') as f:
        html_page = f.read()
        html_page = html_page.format(temp=temp)
    return html_page

temp_data = "N/A"

utime.sleep(3)

while True:
    # Socket accept()
    conn, addr = s.accept()
    print("Got connection from %s" % str(addr))

    # Socket receive()
    request = conn.recv(1024)
    print("")
    print("Content %s" % str(request))

    # Socket send()
    request = str(request)
    update = request.find('/getSensors')
    if update == 6:
        response = temp_data 
    else:
        response = web_page(temp_data)

    
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response.encode())  

    
    conn.close()

    sender, decrypted_message, snr, rssi = lora.read_msg_secure(key, nonce, associate_data, variant)

    if sender is not None and decrypted_message is not None:
        temp_data = decrypted_message
        print(f'Temperature: {temp_data}, SNR: {snr}, RSSI: {rssi}')