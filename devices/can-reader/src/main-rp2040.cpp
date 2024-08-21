#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_MCP2515.h>
#include <Wire.h>
#include <constants.h>
#include <ArduinoJson.h>
#define CS_PIN PIN_CAN_CS
#define INT_PIN PIN_CAN_INTERRUPT
#define START_HEADER "Convoy Agent Commit:" COMMIT_HASH
#define CAN_BAUDRATE (500000)



#define A value[0]
#define B value[1]
#define C value[2]
#define D value[3]



Adafruit_MCP2515 CAN(CS_PIN);

void transmit()
{
  JsonDocument doc;
  doc["batteryVoltage"] = 12.7;
  doc["distanceSinceCodesReset"] = 5000;
  doc["distanceWithMILOn"] = 0;
  doc["timeSinceCodesReset"] = 100.0;
  doc["ambientAirTemp"] = 37.8;
  doc["fuelLevel"] = 100;
  serializeJson(doc, Serial1);
  Serial1.println();
  serializeJson(doc, Serial);
  Serial.println();
}
float parseVINPacket()
{
    return 0.0;
}
void onReceive(int packetSize)
{
    Serial.print("packet with id 0x");

    if (CAN.packetId() == PID_RESPONSE_ID)
    {
        Serial.println("Got OBD Response");
        //parseOBDPacket();
    }
    else if (CAN.packetId() == VIN_CAN_ID)
    {
        Serial.println("Got VIN Response");
    }
}
void initCAN()
{
    Serial.print(F("Initializing CAN Controller..."));

    if (!CAN.begin(CAN_BAUDRATE))
    {
        Serial.println("Error initializing CAN Controller.");
        while (1)
            delay(10);
    }
    Serial.println("CAN initialized!");
    CAN.onReceive(INT_PIN, onReceive);
}
void setup()
{
    Serial.begin(BAUD_RATE);
    Serial1.begin(BAUD_RATE);
    while (!Serial)
        delay(10);
    delay(2000);
    Serial.println(START_HEADER);
    initCAN();
}
int last = millis();
void loop()
{
    if ((millis() - last) > 1000) {
        Serial.println("Writing data to UART");
        transmit();
        last = millis();
    }
}
