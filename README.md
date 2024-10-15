# LoRa-Based-Multi-Node-Energy-Meter-Reading-with-Grafana-Dashboard
This repository contains a comprehensive solution for remotely monitoring energy usage across multiple nodes using LoRa (Long Range) technology. The system is designed for efficient communication between energy meters and a central gateway, allowing users to access real-time data through a Grafana dashboard.

Key Features:

    Multi-Node Support: Multiple energy meters can be monitored simultaneously, making the system scalable for various applications.
    LoRa Communication: Utilizes LoRa technology for long-range data transmission, ensuring reliable connectivity even in challenging environments.
    Data Visualization: Integrated with Grafana for intuitive and insightful data visualization, enabling users to track energy consumption trends and patterns over time.
    Modbus Protocol: Compatible with Modbus-enabled energy meters, allowing seamless integration with existing infrastructure.

Project Structure:

    Node Code: The firmware for each energy meter node, responsible for collecting data and transmitting it via LoRa.
    Gateway Code: The firmware for the central gateway, which receives data from nodes and forwards it to the Grafana dashboard.
    Grafana Dashboard Configuration: Instructions for setting up the Grafana dashboard to visualize the data collected from the energy meters.

Gateway Code Overview:

    The gateway code is responsible for connecting to AWS IoT and publishing energy data from multiple energy meter nodes. It employs the AWS IoT Core MQTT protocol for reliable message delivery. Here’s a breakdown of the key components of the gateway code:
    AWS IoT Configuration

Each energy meter node has its own AWS IoT configuration, including:

    Endpoint: The AWS IoT endpoint to which the gateway connects.
    Publish Topic: The topic under which the energy meter data will be published.
    Certificates: Each device has its own certificate, private key, and CA file for secure communication.

MQTT Connection Setup:

    The code establishes an MQTT connection for each energy meter node using the mqtt_connection_builder provided by the AWS IoT SDK. It includes connection callbacks to handle connection interruptions and resumptions.


Data Processing:

    The gateway retrieves data from each energy meter by executing a Python script (DeviceX.py) using the subprocess module. It parses the output using regular expressions to extract relevant metrics such as voltage, current, power factor, and frequency.

Publishing Data:

    The parsed data is then formatted into JSON and published to the respective AWS IoT topic. The gateway handles potential errors during the publishing process and logs the results.

Main Loop:

    The main_loop function runs indefinitely, continuously polling data from each energy meter at specified intervals.
