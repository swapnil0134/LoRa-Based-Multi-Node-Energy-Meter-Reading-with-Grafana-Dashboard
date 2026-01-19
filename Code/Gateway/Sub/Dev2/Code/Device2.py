#1. Data request and save 2. Precess received data and save 3. Save data in database-influxdb 4. Reqest data only once
import board
import busio
import digitalio
import adafruit_rfm9x
import time
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import re

# Define radio parameters.
RADIO_FREQ_MHZ = 868.0  # Frequency of the radio in MHz for 868 MHz band

# Define pins connected to the chip, adjust according to your hardware setup
CS = digitalio.DigitalInOut(board.CE1)  # Chip select
RESET = digitalio.DigitalInOut(board.D25)  # Reset

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=100000)

# Set transmit power (in dB)
rfm9x.tx_power = 23

# Set the spreading factor and bandwidth
rfm9x.spreading_factor = 8  # Set the spreading factor to SF=8

# Define log directory
# Current: Code/Gateway/Sub/Dev2/Code/Device2.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Root: Go up 5 levels
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
log_base_dir = os.path.join(root_dir, 'Energy_Meters/Sub/Dev2/Logs')

# InfluxDB configuration
influxdb_url = 'http://localhost:8086'
influxdb_token = 'token'
influxdb_org = 'smdh'
influxdb_bucket = 'Energy_Meter_Device_2'

# Initialize InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def create_daily_log_folder():
    """Create a new folder for today's date if it doesn't already exist."""
    today = time.strftime("%Y-%m-%d", time.localtime())
    log_dir = os.path.join(log_base_dir, today)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def replace_field_names(message):
    """Replace field names in the message with the desired names."""
    replacements = {
        "P1": "Phase 1 line to neutral voltage",
        "P2": "Phase 2 line to neutral voltage",
        "P3": "Phase 3 line to neutral voltage",
        "P4": "Phase 1 current",
        "P5": "Phase 2 current",
        "P6": "Phase 3 current",
        "P7": "Phase 1 active power",
        "P8": "Phase 2 active power",
        "P9": "Phase 3 active power",
        "P10": "Phase 1 power factor",
        "P11": "Phase 2 power factor",
        "P12": "Phase 3 power factor",
        "P13": "Line 1 to Line 2 voltage",
        "P14": "Line 2 to Line 3 voltage",
        "P15": "Line 3 to Line 1 voltage",
        "P16": "Neutral current",
        "P17": "Frequency"
    }
    # Use regular expressions to replace only whole matches of P1, P2, ..., P17
    for old, new in replacements.items():
        message = re.sub(rf'\b{old}\b', new, message)
    return message

def save_log(log_dir, timestamp, message):
    """Save the log message to a text file."""
    log_text_file = os.path.join(log_dir, 'log.txt')
    with open(log_text_file, 'a') as text_file:
        # Replace field names in the message
        processed_message = replace_field_names(message)
        text_file.write(f"[{timestamp}] {processed_message}\n")

def send_handshake():
    """Send the handshaking message."""
    message = "Device2"
    rfm9x.send(bytes(message, "ascii"))

def write_to_influxdb(timestamp, message):
    """Write the processed message to InfluxDB."""
    processed_message = replace_field_names(message)
    fields = dict(item.split(":") for item in processed_message.split(","))
    
    # Create a Point object with timestamp and tags
    point = Point("sensor_data").tag("device", "Device2").time(timestamp, WritePrecision.S)

    # Add each field to the Point object
    for field_name, value in fields.items():
        try:
            # Convert the value to a float
            point.field(field_name, float(value))
        except ValueError:
            # If conversion fails, store the value as a string
            point.field(field_name, value)

    # Write the point to InfluxDB
    write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)

def receive_message():
    """Receive and process a message."""
    packet = rfm9x.receive(timeout=10.0, with_header=True)
    if packet is not None:
        # Decode to ASCII text
        packet_text = str(packet, "latin-1")
        
        # Check if the message contains the keyword "Device2"
        if "Device2" in packet_text:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())  # Use UTC time for consistency
            print(f"[{timestamp}] {packet_text}")

            # Create log folder and save the message
            log_dir = create_daily_log_folder()
            save_log(log_dir, timestamp, packet_text)

            # Write data to InfluxDB
            write_to_influxdb(timestamp, packet_text)
        else:
            print("Received packet does not contain 'Device2'. Ignoring.")


# Main execution
#print("Starting data request...")
send_handshake()
time.sleep(1)  # Wait for a short period to allow the message to be transmitted

# Receive and process any incoming messages
receive_message()
