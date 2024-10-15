// Different LoRa Parameters Configured to avoid interference between two setups. Complete code. Hidden Key =Device1
// Code working perfectly.
#include <SPI.h>
#include <LoRa.h>
#include <ModbusMaster.h>
#include <HardwareSerial.h>


// LoRa settings
#define LORA_SS_PIN 5
#define LORA_RST_PIN 14
#define LORA_DIO0_PIN 2

// Matching the transmitter's settings
#define RF_FREQUENCY        868E6    // 868 MHz
#define LORA_BANDWIDTH      125E3    // 125 kHz
#define LORA_SPREADING_FACTOR 8      // new SF. old setup has SF=7.
#define LORA_CODINGRATE     5        // 4/5 Coding rate
#define LORA_PREAMBLE_LENGTH 8
#define BUFFER_SIZE         256      // Payload size

float V1 = 0; //phase-1 voltage
float V2 = 0; //phase-2 voltage
float V3 = 0; //phase-3 voltage
float I1 = 0; //phase-1 Current
float I2 = 0; //phase-1 Current
float I3 = 0; //phase-1 Current
float W1 = 0; //Phase 1 active power
float W2 = 0; //Phase 2 active power
float W3 = 0; //Phase 3 active power
float PF1 = 0; //Phase 1 Power Factor
float PF2 = 0; //Phase 1 Power Factor
float PF3 = 0; //Phase 1 Power Factor
float Vab = 0; //phase 1 to phase 2 voltage
float Vbc = 0; //phase 2 to phase 3 voltage
float Vca = 0; //phase 3 to phase 1 voltage
float In = 0; //Neutral current
float F = 0; //Frequency of Supply Voltages

#define RS485_TX 17   // TX pin of ESP32 connected to DI of HW-097
#define RS485_RX 16   // RX pin of ESP32 connected to RO of HW-097
#define RS485_DE_RE 4 // GPIO pin controlling DE/RE of HW-097 DO NOT CONNECT DE
#define MODBUS_ADDR 1 // Modbus address of SDM72D-M

HardwareSerial SerialMod(1); // Serial1 for RS485

ModbusMaster node;

void preTransmission() {
  digitalWrite(RS485_DE_RE, HIGH); // Enable RS485 Transmit
}

void postTransmission() {
  digitalWrite(RS485_DE_RE, LOW); // Enable RS485 Receive
}


void setup() {
  pinMode(RS485_DE_RE, OUTPUT);
  digitalWrite(RS485_DE_RE, LOW);

  Serial.begin(115200); // Debug serial port
  SerialMod.begin(9600, SERIAL_8N1, RS485_RX, RS485_TX); // RS485 serial port
  delay(2000);
  Serial.println("Ready");

  node.begin(MODBUS_ADDR, SerialMod);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);


  // Initialize LoRa
  LoRa.setPins(LORA_SS_PIN, LORA_RST_PIN, LORA_DIO0_PIN);
  if (!LoRa.begin(868E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  // Set parameters to match the transmitter
  LoRa.setSpreadingFactor(LORA_SPREADING_FACTOR); // SF7
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);        // 125 kHz
  LoRa.setCodingRate4(LORA_CODINGRATE);           // 4/5
  LoRa.setPreambleLength(LORA_PREAMBLE_LENGTH);   // Preamble length
  Serial.println("LoRa Initializing OK!");
}

float reform_uint16_2_float32(uint16_t u1, uint16_t u2) {
  uint32_t num = ((uint32_t)u1 & 0xFFFF) << 16 | ((uint32_t)u2 & 0xFFFF);
  float numf;
  memcpy(&numf, &num, 4);
  return numf;
}

float getRTU(uint16_t m_startAddress) {
  uint8_t m_length = 2;
  uint16_t result;
  float value = 0.0;

  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
  result = node.readInputRegisters(m_startAddress, m_length);

  if (result == node.ku8MBSuccess) {
    value = reform_uint16_2_float32(node.getResponseBuffer(0), node.getResponseBuffer(1));
  }

  return value;
}



void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incomingMessage = "";
    while (LoRa.available()) {
      incomingMessage += (char)LoRa.read();
    }

////    Serial.print("Received raw bytes: ");
    for (int i = 0; i < incomingMessage.length(); i++) {
////      Serial.print((int)incomingMessage[i], HEX);
////      Serial.print(" ");
    }
////    Serial.println();

    // Extract meaningful part of the message (ignoring the first 4 bytes)
    if (incomingMessage.length() > 4) {
      String message = incomingMessage.substring(4);
      message.trim();  // Clean up any extra whitespace
////      Serial.print("Extracted message: ");
////      Serial.println(message);

      // Check if the message matches "Device1"
      if (message == "Device1") {
////        Serial.println("Keyword 'Device1' found.");

        delay(2000);
        collectAndSendData();
      }
    }
  }
}

void collectAndSendData() {
  V1 = getRTU(0x0000);
  V2 = getRTU(0x0002);
  V3 = getRTU(0x0004);
  I1 = getRTU(0x0006);
  I2 = getRTU(0x0008);
  I3 = getRTU(0x000A);
  W1 = getRTU(0x000C);
  W2 = getRTU(0x000E);
  W3 = getRTU(0x0010);
  PF1 = getRTU(0x001E);
  PF2 = getRTU(0x0020);
  PF3 = getRTU(0x0022);
  Vab = getRTU(0x00C8);
  Vbc = getRTU(0x00CA);
  Vca = getRTU(0x00CC);
  In = getRTU(0x00E0);
  F = getRTU(0x0046);

  // Send data via LoRa
  sendToLoRa(V1, V2, V3, I1, I2, I3, W1, W2, W3, PF1, PF2, PF3, Vab, Vbc, Vca, In, F);

////  Serial.println("Data sent via LoRa.");
}

void sendToLoRa(float P1, float P2, float P3, float P4, float P5, float P6, float P7, float P8, float P9, float P10, float P11, float P12, float P13, float P14, float P15, float P16, float P17) {
  // Create a single string with all the data
  String dataToSend = "ID:Device1, P1:" + String(P1) +
                      ", P2:" + String(P2) +
                      ", P3:" + String(P3) +
                      ", P4:" + String(P4) +
                      ", P5:" + String(P5) +
                      ", P6:" + String(P6) +
                      ", P7:" + String(P7) +
                      ", P8:" + String(P8) +
                      ", P9:" + String(P9) +
                      ", P10:" + String(P10) +
                      ", P11:" + String(P11) +
                      ", P12:" + String(P12) +
                      ", P13:" + String(P13) +
                      ", P14:" + String(P14) +
                      ", P15:" + String(P15) +
                      ", P16:" + String(P16) +
                      ", P17:" + String(P17);

  // Send the entire string via LoRa
  LoRa.beginPacket();
  LoRa.print(dataToSend);
///  Serial.println(dataToSend);
  LoRa.endPacket();
}
