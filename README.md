# 📡 Secure LoRa-based IoT Communication with ASCON & AES-256  
### Featuring ECDH Key Exchange & Data Visualization

---

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Folder Structure](#folder-structure)
5. [Hardware Setup](#hardware-setup)
6. [ECDH Key Exchange](#ecdh-key-exchange)
7. [Encryption Details](#encryption-details)
8. [Data Visualization](#data-visualization)
9. [Hacker Mode](#hacker-mode)
10. [Performance Metrics](#performance-metrics)
11. [Conclusion](#conclusion)
12. [Contact](#contact)

---

## Introduction
This repository provides a secure IoT system using LoRa technology for long-range, low-power communication. It integrates advanced security measures including:

- **NIST ASCON**: A lightweight AEAD cipher.
- **AES-256**: Robust encryption.
- **ECDH Key Exchange**: Secure key derivation over LoRa.

---

## Features
- **LoRa Communication**: RYLR896 modules for reliable wireless connections.
- **Transmitter**: Raspberry Pi Pico with temperature and pressure sensors.
- **Receiver**: ESP32 supporting offline web server and cloud integrations.
- **Security**: Combines ASCON, AES-256, and ECDH.
- **Data Visualization**: Offline web interface, local CSV logging, and Adafruit IO cloud support.

---

## Architecture
- **Communication**: LoRa provides long-range, low-power wireless data transfer.
- **Encryption & Key Exchange**: Data is encrypted using keys derived via ECDH, ensuring confidentiality.
- **Visualization**: Real-time and logged data available through various modes.

---

## Folder Structure
.
├── Transmitter
│   ├── rpi_uart_ascon.py         # Offline web server transmitter
│   ├── tx_key_ex_ascon_cloud.py    # Cloud (Adafruit IO) transmitter
│   ├── tx_key_ex_ascon_csv.py      # CSV file transmitter
│   ├── x25519.py                 # ECDH implementation
│   ├── ecdh.py                   # ECDH demo
│   └── pico_art.py               # Pressure sensor example
├── Receiver
│   ├── rx_key_ex_ascon_offline_webpage.py  # Offline web receiver
│   ├── rx_key_ex_ascon_cloud.py            # Cloud receiver
│   ├── rx_key_ex_ascon_csv.py              # CSV file receiver
│   └── weather_station.html                # Web UI layout
└── Documentation
    ├── Pinout_ESP32.png
    ├── Pinout_Pico.png
    ├── RYLR896_ESP32.png
    ├── RYLR896_RPico.png
    └── BMP280_with_Pico.jpg


---

## Hardware Setup
1. **Wiring**:  
   - Connect LoRa RYLR896 modules to the ESP32 and Pico (ensure TX/RX, 3.3V, and GND are correctly connected).  
   - Refer to the pinout diagrams in the Documentation folder.

2. **Sensors**:  
   - **Temperature Sensor**: Connect via I2C (SDA & SCL) on the Pico.
   - **Pressure Sensor**: Utilize the code from `pico_art.py` with proper I2C configuration.

3. **Receiver**:  
   - Choose the appropriate receiver script based on your visualization needs (offline web, CSV logging, or Adafruit IO cloud).

---

## ECDH Key Exchange
1. Remove traditional DH implementation.
2. Import `x25519.py` into both transmitter and receiver scripts.
3. Refer to `ecdh.py` to:
   - Generate key pairs.
   - Exchange public keys via LoRa.
   - Compute the shared secret.
4. Derive encryption keys using the shared secret.

---

## Encryption Details
- **ASCON**:  
  - Lightweight and efficient encryption for IoT.
  - Encrypts sensor data with the key derived from ECDH.

- **AES-256**:  
  - Offers robust encryption for performance comparison.

---

## Data Visualization
1. **Offline Web Server**:  
   - Execute `rx_key_ex_ascon_offline_webpage.py` on the ESP32.
   - Connect to the Wi-Fi hotspot provided by the ESP32 and navigate to the given IP.

2. **Local CSV Storage**:  
   - Run `rx_key_ex_ascon_csv.py` to log sensor data into a CSV file stored on the ESP32.
   - Access the file via Thonny or similar tools.

3. **Adafruit IO Cloud**:  
   - Use `rx_key_ex_ascon_cloud.py` after configuring your Adafruit IO account and feed.
   - Ensure the ESP32 is connected to a 2.4 GHz Wi-Fi network for proper cloud integration.

---

## Hacker Mode
- **MITM Attack Simulation**:  
  - Duplicate receiver setup without key exchange/encryption.
  - Attempts to intercept data will fail without the correct keys.

- **Flooding Attack Simulation**:  
  - Rogue transmitter sends bogus LoRa messages.
  - The receiver only validates messages from authorized transmitters based on IDs and parameters.

---

## Performance Metrics
- **SNR (Signal-to-Noise Ratio)**
- **RSSI (Received Signal Strength Indicator)**
- **Latency**
- **Power Consumption**
- **Memory Usage**

---

## Conclusion
Integrating LoRa with NIST ASCON, AES-256, and ECDH provides a secure and cost-effective IoT communication system. The flexible design supports multiple data visualization methods and ensures robust security for modern IoT applications.

---

## Contact
For inquiries, contributions, or support, please refer to the repository documentation or contact the project maintainers.

---

**End of README**
