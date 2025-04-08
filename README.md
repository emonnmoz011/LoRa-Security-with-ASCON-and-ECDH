Project Title:
Secure LoRa-based IoT Communication with ASCON and AES-256, featuring ECDH Key Exchange and Data Visualization

Overview:
This project explores secure and efficient long-range communication for IoT devices using LoRa technology. It incorporates
the newly standardized NIST ASCON encryption, AES-256 encryption, and Elliptic Curve Diffie-Hellman (ECDH) key exchange
to ensure robust security. The system is designed to handle various sensor data and supports three data visualization
methods: real-time updates on an offline web server, local CSV storage, and secure cloud storage on Adafruit IO.
Performance comparisons show that ASCON outperforms AES-256 in terms of SNR, RSSI, latency, power consumption, 
and memory usage.

Key Components:
  1. LoRa RYLR896 Modules
  2. ESP32 (Receiver)
  3. Raspberry Pi Pico (Transmitter)
  4. Environmental Sensors (Temperature and Pressure)
  5. ECDH Key Exchange (using x25519.py)
  6. AES-256 and ASCON Encryption
  7. Data Visualization
     - Offline Webserver
     - Local CSV Files
     - Adafruit IO Cloud Storage

Folder Structure (Example):
  1. Transmitter Code:
     - rpi_uart_ascon.py (Offline Web Server Version)
     - tx_key_ex_ascon_cloud.py (Adafruit IO Cloud Version)
     - tx_key_ex_ascon_csv.py (Local CSV Version)
     - x25519.py (ECDH Implementation)
     - ecdh.py (ECDH Demo)
     - pico_art.py (Pressure Sensor Code Example)
  2. Receiver Code:
     - rx_key_ex_ascon_offline_webpage.py (Offline Web Server Receiver)
     - rx_key_ex_ascon_cloud.py (Adafruit IO Cloud Receiver)
     - rx_key_ex_ascon_csv.py (Local CSV Receiver)
     - weather_station.html (HTML for Offline Web Server)
  3. Documentation and Images:
     - Pinout ESP32
     - Pinout Pico
     - RYLR896_ESP32 Connections
     - RYLR896_RPico Connections
     - BMP 280 with Pico
  4. Hacker Mode (Optional):
     - MITM Attack Scripts
     - Flooding Attack Scripts

Hardware Setup:
  1. Connect the LoRa RYLR896 module to the ESP32 and Raspberry Pi Pico as per the provided pinout diagrams.
     - TX/RX pins
     - 3.3V power supply
     - Ground connections
     - Any specific pins designated for your sensors
  2. For the Temperature Sensor:
     - Use the I2C communication pins on the Pico (GPIO pins typically labeled SDA and SCL).
     - Implement the relevant code from rpi_uart_ascon.py or similar transmitter files.
  3. For the Pressure Sensor (BMP280 or similar):
     - Replace the temperature sensor’s I2C code with the code from pico_art.py, focusing on reading 
       the pressure sensor data instead.
  4. On the ESP32 side:
     - Use the receiver code that matches your chosen data visualization (offline web, CSV storage, or cloud).
     - If using the offline web server, connect to the Wi-Fi hotspot created by the ESP32 and visit the IP address 
       shown in the console.

Key Exchange (Replacing DH with ECDH):
  1. Delete or comment out the existing Diffie-Hellman (DH) code.
  2. Import x25519.py into your main scripts (transmitter and receiver).
  3. Refer to ecdh.py for a usage example:
     - Generate key pairs on both transmitter and receiver.
     - Exchange public keys over LoRa.
     - Derive the shared secret from the received public key.
  4. Use the derived shared secret to strengthen the encryption keys for ASCON or AES-256.

Encryption Details:
  1. ASCON:
     - Newly standardized lightweight AEAD cipher by NIST.
     - Encrypt sensor data on the transmitter using the shared secret from ECDH.
     - Decrypt on the receiver side using the same shared secret.
  2. AES-256:
     - Traditional encryption standard.
     - Use the derived key from ECDH if you want a fallback or comparative testing.

Data Visualization:
  1. Offline Web Server:
     - Use rx_key_ex_ascon_offline_webpage.py.
     - The ESP32 creates a hotspot and displays an IP address in the console.
     - Connect to this Wi-Fi on your computer or mobile device.
     - Enter the IP address in a web browser, then refresh the page to view updated sensor readings.
  2. Local CSV Storage:
     - Use rx_key_ex_ascon_csv.py on the receiver.
     - Data is saved in a CSV file in the ESP32 file system.
     - Download the file using Thonny or a similar IDE to view historical data.
  3. Adafruit IO Cloud:
     - Use rx_key_ex_ascon_cloud.py on the receiver.
     - Sign up for Adafruit IO (https://io.adafruit.com/).
     - Create a feed for your data.
     - Insert your Adafruit IO key, feed name, and username in the script.
     - Ensure the ESP32 is connected to a 2.4 GHz Wi-Fi network.
     - Data will appear on your Adafruit IO dashboard.

Hacker Mode (Optional):
  1. MITM Attack:
     - Create a duplicate receiver without key exchange or encryption.
     - Attempt to intercept LoRa packets from the transmitter.
     - Demonstrates that without the encryption key, the data remains secure.
  2. Flooding Attack:
     - Create a rogue transmitter that sends continuous bogus messages.
     - Attempt to overwhelm the legitimate receiver with spam.
     - The receiver only accepts packets from known addresses with the correct communication parameters 
       and network ID, illustrating robust filtering.

Performance Metrics:
  1. Signal-to-Noise Ratio (SNR)
  2. Received Signal Strength Indicator (RSSI)
  3. Latency
  4. Power Consumption
  5. Memory Usage

Conclusion:
This project demonstrates a secure, long-range IoT communication system using LoRa, ASCON, AES-256, and ECDH. 
It addresses modern IoT requirements by providing multi-layer security, cost-effectiveness, and flexible data visualization. 
The setup and code can be easily adapted for diverse environmental sensors and expanded to accommodate additional functionalities.

Contact:
For questions or clarifications, please reach out to the project contributors or consult the documentation within the repository.
"""

print(content)
