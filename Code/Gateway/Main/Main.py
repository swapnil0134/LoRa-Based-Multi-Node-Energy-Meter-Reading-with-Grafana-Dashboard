from datetime import datetime, timezone
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import subprocess
import time
import json
import re
import os

# Get directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get parent directory (Code/Gateway)
gateway_dir = os.path.dirname(current_dir)

# Helper function to get paths
def get_path(path_suffix):
    return os.path.join(gateway_dir, path_suffix)

# Device 1 AWS IoT configuration
aws_endpoint_1 = "endpoint"
aws_publish_topic_1 = "Energy_Meter/Energy_Meter_1"
cert_filepath_1 = get_path("Sub/Dev1/Keys/Energy_Meter_1.crt")
key_filepath_1 = get_path("Sub/Dev1/Keys/Energy_Meter_1.key")
ca_filepath_1 = get_path("Sub/Dev1/Keys/rootCA.pem")

# Device 2 AWS IoT configuration
aws_endpoint_2 = "endpoint"
aws_publish_topic_2 = "Energy_Meter/Energy_Meter_2"
cert_filepath_2 = get_path("Sub/Dev2/Keys/Energy_Meter_2.crt")
key_filepath_2 = get_path("Sub/Dev2/Keys/Energy_Meter_2.key")
ca_filepath_2 = get_path("Sub/Dev2/Keys/rootCA.pem")

# Device 3 AWS IoT configuration
aws_endpoint_3 = "endpoint"
aws_publish_topic_3 = "Energy_Meter/Energy_Meter_3"
cert_filepath_3 = get_path("Sub/Dev3/Keys/Energy_Meter_3.crt")
key_filepath_3 = get_path("Sub/Dev3/Keys/Energy_Meter_3.key")
ca_filepath_3 = get_path("Sub/Dev3/Keys/rootCA.pem")

# Device 4 AWS IoT configuration
aws_endpoint_4 = "endpoint"
aws_publish_topic_4 = "Energy_Meter/Energy_Meter_4"
cert_filepath_4 = get_path("Sub/Dev4/Keys/Energy_Meter_4.crt")
key_filepath_4 = get_path("Sub/Dev4/Keys/Energy_Meter_4.key")
ca_filepath_4 = get_path("Sub/Dev4/Keys/rootCA.pem")

# AWS IoT MQTT connection setup for Device 1
mqtt_connection_1 = mqtt_connection_builder.mtls_from_path(
    endpoint=aws_endpoint_1,
    cert_filepath=cert_filepath_1,
    pri_key_filepath=key_filepath_1,
    ca_filepath=ca_filepath_1,
    client_id="Energy_Meter_1",
    clean_session=False,
    keep_alive_secs=30
)

# AWS IoT MQTT connection setup for Device 2
mqtt_connection_2 = mqtt_connection_builder.mtls_from_path(
    endpoint=aws_endpoint_2,
    cert_filepath=cert_filepath_2,
    pri_key_filepath=key_filepath_2,
    ca_filepath=ca_filepath_2,
    client_id="Energy_Meter_2",
    clean_session=False,
    keep_alive_secs=30
)

# AWS IoT MQTT connection setup for Device 3
mqtt_connection_3 = mqtt_connection_builder.mtls_from_path(
    endpoint=aws_endpoint_3,
    cert_filepath=cert_filepath_3,
    pri_key_filepath=key_filepath_3,
    ca_filepath=ca_filepath_3,
    client_id="Energy_Meter_3",
    clean_session=False,
    keep_alive_secs=30
)

# AWS IoT MQTT connection setup for Device 4
mqtt_connection_4 = mqtt_connection_builder.mtls_from_path(
    endpoint=aws_endpoint_4,
    cert_filepath=cert_filepath_4,
    pri_key_filepath=key_filepath_4,
    ca_filepath=ca_filepath_4,
    client_id="Energy_Meter_4",
    clean_session=False,
    keep_alive_secs=30
)

def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. Error: {error}")

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. Return code: {return_code}, Session present: {session_present}")

def on_publish(topic, payload, **kwargs):
    print(f"Published to topic {topic}: {payload}")

# Add connection callbacks to all connections
mqtt_connection_1.on_interrupted = on_connection_interrupted
mqtt_connection_1.on_resumed = on_connection_resumed

mqtt_connection_2.on_interrupted = on_connection_interrupted
mqtt_connection_2.on_resumed = on_connection_resumed

mqtt_connection_3.on_interrupted = on_connection_interrupted
mqtt_connection_3.on_resumed = on_connection_resumed

mqtt_connection_4.on_interrupted = on_connection_interrupted
mqtt_connection_4.on_resumed = on_connection_resumed

# Connect to AWS IoT for Device 1
print(f"Connecting Device 1 to AWS IoT endpoint {aws_endpoint_1}...")
connect_future_1 = mqtt_connection_1.connect()

# Connect to AWS IoT for Device 2
print(f"Connecting Device 2 to AWS IoT endpoint {aws_endpoint_2}...")
connect_future_2 = mqtt_connection_2.connect()

# Connect to AWS IoT for Device 3
print(f"Connecting Device 3 to AWS IoT endpoint {aws_endpoint_3}...")
connect_future_3 = mqtt_connection_3.connect()

# Connect to AWS IoT for Device 4
print(f"Connecting Device 4 to AWS IoT endpoint {aws_endpoint_4}...")
connect_future_4 = mqtt_connection_4.connect()

# Wait for the connections to be established
try:
    connect_future_1.result()
    print("Device 1 connected to AWS IoT!")
except Exception as e:
    print(f"Failed to connect Device 1: {e}")
    exit(1)

try:
    connect_future_2.result()
    print("Device 2 connected to AWS IoT!")
except Exception as e:
    print(f"Failed to connect Device 2: {e}")
    exit(1)
    
try:
    connect_future_3.result()
    print("Device 3 connected to AWS IoT!")
except Exception as e:
    print(f"Failed to connect Device 3: {e}")
    exit(1)

try:
    connect_future_4.result()
    print("Device 4 connected to AWS IoT!")
except Exception as e:
    print(f"Failed to connect Device 4: {e}")
    exit(1)
    
    
def parse_output1(output):
    pattern = re.compile(r'\[(.*?)\] ID:(.*?), P1:(.*?), P2:(.*?), P3:(.*?), P4:(.*?), P5:(.*?), P6:(.*?), P7:(.*?), P8:(.*?), P9:(.*?), P10:(.*?), P11:(.*?), P12:(.*?), P13:(.*?), P14:(.*?), P15:(.*?), P16:(.*?), P17:(.*?)$')
    match = pattern.match(output)
    
    if match:
        timestamp_str, device_id, V1, V2, V3, I1, I2, I3, W1, W2, W3, PF1, PF2, PF3, L12, L23, L31, NC, HZ = match.groups()
        
        # Parse the timestamp string and convert it to UTC
        timestamp_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
        timestamp_utc = timestamp_naive.replace(tzinfo=timezone.utc)
        
        # Convert UTC datetime to epoch time
        timestamp = int(timestamp_utc.timestamp())
        
        return {
            "ID": "Energy_Meter_1",
            "timestamp": timestamp,
            "V1_Volt": float(V1),
            "V2_Volt": float(V2),
            "V3_Volt": float(V3),
            "I1_Amp": float(I1),
            "I2_Amp": float(I2),
            "I3_Amp": float(I3),
            "W1_Watt": float(W1),
            "W2_Watt": float(W2),
            "W3_Watt": float(W3),
            "PF1": float(PF1),
            "PF2": float(PF2),
            "PF3": float(PF3),
            "L1V-L2V_Volt": float(L12),
            "L2V-L3V_Volt": float(L23),
            "L3V-L1V_Volt": float(L31),
            "NC_Amp": float(NC),
            "Hz": float(HZ),
        }
    else:
        raise ValueError("Device 1 Output format is incorrect")
    
def run_program1():
    # Path to the program
    node1_path = get_path('Sub/Dev1/Code/Device1.py')
    
    # Run the program using subprocess
    result = subprocess.run(['python3', node1_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout.strip()
        try:
            json_data = parse_output1(output)
            json_payload = json.dumps(json_data)
            print("Publishing to AWS IoT:", json_payload)
            
            # Publish JSON payload to AWS IoT
            publish_future, _ = mqtt_connection_1.publish(
                topic=aws_publish_topic_1,
                payload=json_payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Wait for the publish operation to complete
            publish_future.result()
            print("Message published successfully!")
        except ValueError as e:
            print(f"Error parsing output: {e}")
        except Exception as e:
            print(f"Failed to publish message: {e}")
    else:
        print(f"Error running Device1.py: {result.stderr}")

def parse_output2(output):
    pattern = re.compile(r'\[(.*?)\] ID:(.*?), P1:(.*?), P2:(.*?), P3:(.*?), P4:(.*?), P5:(.*?), P6:(.*?), P7:(.*?), P8:(.*?), P9:(.*?), P10:(.*?), P11:(.*?), P12:(.*?), P13:(.*?), P14:(.*?), P15:(.*?), P16:(.*?), P17:(.*?)$')
    match = pattern.match(output)
    
    if match:
        timestamp_str, device_id, V1, V2, V3, I1, I2, I3, W1, W2, W3, PF1, PF2, PF3, L12, L23, L31, NC, HZ = match.groups()
        
        # Parse the timestamp string and convert it to UTC
        timestamp_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
        timestamp_utc = timestamp_naive.replace(tzinfo=timezone.utc)
        
        # Convert UTC datetime to epoch time
        timestamp = int(timestamp_utc.timestamp())
        
        return {
            "ID": "Energy_Meter_2",
            "timestamp": timestamp,
            "V1_Volt": float(V1),
            "V2_Volt": float(V2),
            "V3_Volt": float(V3),
            "I1_Amp": float(I1),
            "I2_Amp": float(I2),
            "I3_Amp": float(I3),
            "W1_Watt": float(W1),
            "W2_Watt": float(W2),
            "W3_Watt": float(W3),
            "PF1": float(PF1),
            "PF2": float(PF2),
            "PF3": float(PF3),
            "L1V-L2V_Volt": float(L12),
            "L2V-L3V_Volt": float(L23),
            "L3V-L1V_Volt": float(L31),
            "NC_Amp": float(NC),
            "Hz": float(HZ),
        }
    else:
        raise ValueError("Device 2 Output format is incorrect")
    
    
def run_program2():
    # Path to the program
    node1_path = get_path('Sub/Dev2/Code/Device2.py')
    
    # Run the program using subprocess
    result = subprocess.run(['python3', node1_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout.strip()
        try:
            json_data = parse_output2(output)
            json_payload = json.dumps(json_data)
            print("Publishing to AWS IoT:", json_payload)
            
            # Publish JSON payload to AWS IoT
            publish_future, _ = mqtt_connection_2.publish(
                topic=aws_publish_topic_2,
                payload=json_payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Wait for the publish operation to complete
            publish_future.result()
            print("Message published successfully!")
        except ValueError as e:
            print(f"Error parsing output: {e}")
        except Exception as e:
            print(f"Failed to publish message: {e}")
    else:
        print(f"Error running Device2.py: {result.stderr}")
        
def parse_output3(output):
    pattern = re.compile(r'\[(.*?)\] ID:(.*?), P1:(.*?), P2:(.*?), P3:(.*?), P4:(.*?), P5:(.*?), P6:(.*?), P7:(.*?), P8:(.*?), P9:(.*?), P10:(.*?), P11:(.*?), P12:(.*?), P13:(.*?), P14:(.*?), P15:(.*?), P16:(.*?), P17:(.*?)$')
    match = pattern.match(output)
    
    if match:
        timestamp_str, device_id, V1, V2, V3, I1, I2, I3, W1, W2, W3, PF1, PF2, PF3, L12, L23, L31, NC, HZ = match.groups()
        
        # Parse the timestamp string and convert it to UTC
        timestamp_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
        timestamp_utc = timestamp_naive.replace(tzinfo=timezone.utc)
        
        # Convert UTC datetime to epoch time
        timestamp = int(timestamp_utc.timestamp())
        
        return {
            "ID": "Energy_Meter_3",
            "timestamp": timestamp,
            "V1_Volt": float(V1),
            "V2_Volt": float(V2),
            "V3_Volt": float(V3),
            "I1_Amp": float(I1),
            "I2_Amp": float(I2),
            "I3_Amp": float(I3),
            "W1_Watt": float(W1),
            "W2_Watt": float(W2),
            "W3_Watt": float(W3),
            "PF1": float(PF1),
            "PF2": float(PF2),
            "PF3": float(PF3),
            "L1V-L2V_Volt": float(L12),
            "L2V-L3V_Volt": float(L23),
            "L3V-L1V_Volt": float(L31),
            "NC_Amp": float(NC),
            "Hz": float(HZ),
        }
    else:
        raise ValueError("Device 3 Output format is incorrect")
    
    
def run_program3():
    # Path to the program
    node1_path = get_path('Sub/Dev3/Code/Device3.py')
    
    # Run the program using subprocess
    result = subprocess.run(['python3', node1_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout.strip()
        try:
            json_data = parse_output3(output)
            json_payload = json.dumps(json_data)
            print("Publishing to AWS IoT:", json_payload)
            
            # Publish JSON payload to AWS IoT
            publish_future, _ = mqtt_connection_3.publish(
                topic=aws_publish_topic_3,
                payload=json_payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Wait for the publish operation to complete
            publish_future.result()
            print("Message published successfully!")
        except ValueError as e:
            print(f"Error parsing output: {e}")
        except Exception as e:
            print(f"Failed to publish message: {e}")
    else:
        print(f"Error running Device3.py: {result.stderr}")
        
        
def parse_output4(output):
    pattern = re.compile(r'\[(.*?)\] ID:(.*?), P1:(.*?), P2:(.*?), P3:(.*?), P4:(.*?), P5:(.*?), P6:(.*?), P7:(.*?), P8:(.*?), P9:(.*?), P10:(.*?), P11:(.*?), P12:(.*?), P13:(.*?), P14:(.*?), P15:(.*?), P16:(.*?), P17:(.*?)$')
    match = pattern.match(output)
    
    if match:
        timestamp_str, device_id, V1, V2, V3, I1, I2, I3, W1, W2, W3, PF1, PF2, PF3, L12, L23, L31, NC, HZ = match.groups()
        
        # Parse the timestamp string and convert it to UTC
        timestamp_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
        timestamp_utc = timestamp_naive.replace(tzinfo=timezone.utc)
        
        # Convert UTC datetime to epoch time
        timestamp = int(timestamp_utc.timestamp())
        
        return {
            "ID": "Energy_Meter_4",
            "timestamp": timestamp,
            "V1_Volt": float(V1),
            "V2_Volt": float(V2),
            "V3_Volt": float(V3),
            "I1_Amp": float(I1),
            "I2_Amp": float(I2),
            "I3_Amp": float(I3),
            "W1_Watt": float(W1),
            "W2_Watt": float(W2),
            "W3_Watt": float(W3),
            "PF1": float(PF1),
            "PF2": float(PF2),
            "PF3": float(PF3),
            "L1V-L2V_Volt": float(L12),
            "L2V-L3V_Volt": float(L23),
            "L3V-L1V_Volt": float(L31),
            "NC_Amp": float(NC),
            "Hz": float(HZ),
        }
    else:
        raise ValueError("Device 4 Output format is incorrect")
    
def run_program4():
    # Path to the program
    node1_path = get_path('Sub/Dev4/Code/Device4.py')
    
    # Run the program using subprocess
    result = subprocess.run(['python3', node1_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        output = result.stdout.strip()
        try:
            json_data = parse_output4(output)
            json_payload = json.dumps(json_data)
            print("Publishing to AWS IoT:", json_payload)
            
            # Publish JSON payload to AWS IoT
            publish_future, _ = mqtt_connection_4.publish(
                topic=aws_publish_topic_4,
                payload=json_payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Wait for the publish operation to complete
            publish_future.result()
            print("Message published successfully!")
        except ValueError as e:
            print(f"Error parsing output: {e}")
        except Exception as e:
            print(f"Failed to publish message: {e}")
    else:
        print(f"Error running Device4.py: {result.stderr}")


def main_loop():
    while True:
        run_program1()
      
        time.sleep(1)
        
        run_program2()
        
        time.sleep(1)

        run_program3()
        
        time.sleep(1)
        
        run_program4()
      
        time.sleep(1)
if __name__ == "__main__":
    main_loop()
