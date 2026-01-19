# LoRa-Based Multi-Node Energy Meter Reading

This repository contains a comprehensive solution for remotely monitoring energy usage across multiple nodes using LoRa (Long Range) technology. The system monitors energy parameters (Voltage, Current, Power, Power Factor, Frequency, etc.) from multiple energy meter nodes and transmits them to a central gateway, which forwards the data to AWS IoT Core and a local InfluxDB instance for visualization in Grafana.

## System Overview

The system is designed for efficient communication between Modbus-enabled energy meters and a central gateway. It uses LoRa for long-range, low-power wireless communication, making it suitable for industrial or distributed environments.

**Key Features:**
*   **Multi-Node Support:** Monitors multiple energy meters simultaneously.
*   **LoRa Communication:** Reliable long-range wireless data transmission.
*   **Dual Data Publishing:** Publishes data to **AWS IoT Core** (cloud) and **InfluxDB** (local/remote time-series database).
*   **Real-time Visualization:** Grafana dashboard for monitoring Voltage, Current, Power, Energy Consumption, etc.
*   **Modbus Compatibility:** Works with SDM72D-M and similar Modbus RTU energy meters.

## Architecture

**Data Flow:**
```
[Energy Meter] <--(RS485/Modbus)--> [Node (ESP32 + LoRa)] <--(LoRa Wireless)--> [Gateway (RPi + LoRa)]
                                                                                      |
                                                                       +--------------+--------------+
                                                                       |                             |
                                                                 [AWS IoT Core]                 [InfluxDB]
                                                                       |                             |
                                                                 (Cloud Analysis)                [Grafana]
                                                                                             (Visualization)
```

## Hardware Components

1.  **Sensor Nodes (End Devices):**
    *   **Microcontroller:** ESP32
    *   **Communication:** LoRa Module (e.g., RFM95/SX1276) operating at 868 MHz.
    *   **Sensor:** Energy Meter (e.g., SDM72D-M) communicating via RS485 (Modbus RTU).
    *   **Role:** Reads data from the meter upon request and transmits it via LoRa.

2.  **Gateway:**
    *   **Host:** Raspberry Pi or Linux-based Single Board Computer.
    *   **Communication:** LoRa Module (e.g., RFM95/SX1276) connected via SPI.
    *   **Role:** Polling master. It requests data from each node sequentially, receives the response, and publishes it to MQTT (AWS IoT) and InfluxDB.

## Software Components

*   **Node Firmware (`Code/Nodes/`):**
    *   Written in C++ (Arduino Framework).
    *   Uses `LoRa` library for wireless and `ModbusMaster` for meter communication.
*   **Gateway Software (`Code/Gateway/`):**
    *   **`Main.py`**: The orchestrator script. It loops through defined devices, triggers their respective handler scripts, and publishes formatted JSON data to AWS IoT Core.
    *   **`DeviceX.py`**: Device-specific scripts that handle the low-level LoRa handshake ("DeviceX" request -> Data response) and write data to InfluxDB.
*   **Visualization (`Dashboard/`):**
    *   **`Dashboard.json`**: A Grafana dashboard JSON model file to visualize the energy metrics.

## Configuration & Setup

### 1. Prerequisites
*   Python 3.7+ installed on the Gateway.
*   Arduino IDE for flashing Nodes.
*   InfluxDB (running on `localhost:8086` or configurable).
*   AWS IoT Core account and provisioned Things.

### 2. Gateway Setup

1.  **Install Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```
    *Required libraries: `awscrt`, `awsiot`, `adafruit-circuitpython-rfm9x`, `influxdb-client`, `adafruit-blinka`, `board`.*

2.  **Configure AWS IoT Certificates:**
    *   Place your AWS IoT certificates and keys in the `Code/Gateway/Sub/DevX/Keys/` directories.
    *   Ensure filenames match those expected in `Code/Gateway/Main/Main.py` (or update `Main.py` to match your filenames).

3.  **Configure InfluxDB:**
    *   Ensure InfluxDB is running.
    *   Update `Code/Gateway/Sub/DevX/Code/DeviceX.py` with your InfluxDB credentials (URL, Token, Org, Bucket).

### 3. Node Setup

1.  **Open Firmware:** Open `Code/Nodes/Device1/Device1.ino` in Arduino IDE.
2.  **Libraries:** Install `LoRa` by Sandeep Mistry and `ModbusMaster` libraries.
3.  **LoRa Settings:** Ensure Frequency (868E6), Spreading Factor (8), and Bandwidth (125E3) match the Gateway settings in `DeviceX.py`.
4.  **Flash:** Upload the code to your ESP32 boards. *Note: Ensure each node listens for its unique ID (e.g., "Device1", "Device2").*

### 4. Grafana Dashboard

1.  Login to your Grafana instance.
2.  Add **InfluxDB** as a data source (Flux language).
3.  Import `Dashboard/Dashboard.json`.

## Usage

To start the Gateway application:

```bash
python3 Code/Gateway/Main/Main.py
```

The system will start polling Device 1, then Device 2, etc., in a loop. Logs will be printed to the console and saved in `Code/Gateway/Sub/DevX/Logs/`.

## Directory Structure

*   `Code/Gateway/`: Python code for the Gateway.
    *   `Main/`: Contains the main execution script.
    *   `Sub/`: Contains device-specific scripts, keys, and logs.
*   `Code/Nodes/`: Arduino firmware for the sensor nodes.
*   `Dashboard/`: Grafana dashboard configuration.
*   `Circuit Diagrams/`: Hardware schematics.
