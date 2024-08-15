#include <Arduino.h>
#include <RadioLib.h>
#include <Wire.h>
#include <constants.h>
#include <data.h>
#include <ArduinoJson.h>
#define START_HEADER "Convoy Base Station Commit: " COMMIT_HASH

#define CC1101_CS_PIN SS
#define CC1101_GDO0_PIN 16
#define CC1101_GDO2_PIN 17

CC1101 radio = new Module(CC1101_CS_PIN, CC1101_GDO0_PIN, RADIOLIB_NC, CC1101_GDO2_PIN);

volatile bool receivedFlag = false;

void handlePacket(Packet packet)
{
  JsonDocument doc;
  doc["batteryVoltage"] = (float)((highByte(packet.batteryVoltage) * 256.0 + lowByte(packet.batteryVoltage)) / 1000.0);
  doc["distanceSinceCodesReset"] = (float)(highByte(packet.distanceSinceCodesReset) * 256.0 + lowByte(packet.distanceSinceCodesReset));
  doc["distanceWithMILOn"] = (float)(highByte(packet.distanceWithMILOn) * 256.0 + lowByte(packet.distanceWithMILOn));
  doc["timeSinceCodesReset"] = (float)(highByte(packet.timeSinceCodesReset) * 256.0 + lowByte(packet.timeSinceCodesReset));
  doc["ambientAirTemp"] = (float)(packet.ambientAirTemp - 40.0);
  doc["fuelLevel"] = (float)(packet.fuelLevel / 2.55);
  serializeJson(doc, Serial);
}
#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void setFlag(void)
{
  // we got a packet, set the flag
  receivedFlag = true;
}
void initRadio()
{
  Serial.print(F("Initializing radio... "));
  int state = radio.begin();
  state = radio.setNodeAddress(0x01, 1);
  radio.setPacketReceivedAction(setFlag);
  if (state == RADIOLIB_ERR_NONE)
  {
    Serial.println(F("Radio initialized!"));
  }
  else
  {
    Serial.println(F("Error initializing radio."));
    Serial.print("Error code: ");
    Serial.println(state);
    while (true)
      ;
  }
  radio.setPacketReceivedAction(setFlag);
  //radio.setFrequency(FREQ);

}
void setup()
{
  Serial.begin(BAUD_RATE);
  delay(2000);
  Serial.println(START_HEADER);
  initRadio();
  Serial.print("MOSI: ");
  Serial.println(MOSI);
  Serial.print("MISO: ");
  Serial.println(MISO);
  Serial.print("SCK: ");
  Serial.println(SCK);
  Serial.print("SS: ");
  Serial.println(SS);  
}
void loop()
{
  // check if the flag is set
  if (receivedFlag)
  {
    // reset flag
    receivedFlag = false;

    // you can read received data as an Arduino String
    String str;
    int state = radio.readData(str);

    if (state == RADIOLIB_ERR_NONE)
    {
      // packet was successfully received
      Serial.println(F("[CC1101] Received packet!"));

      // print data of the packet
      Serial.print(F("[CC1101] Data:\t\t"));
      Serial.println(str);

      // print RSSI (Received Signal Strength Indicator)
      // of the last received packet
      Serial.print(F("[CC1101] RSSI:\t\t"));
      Serial.print(radio.getRSSI());
      Serial.println(F(" dBm"));

      // print LQI (Link Quality Indicator)
      // of the last received packet, lower is better
      Serial.print(F("[CC1101] LQI:\t\t"));
      Serial.println(radio.getLQI());
    }
    else if (state == RADIOLIB_ERR_CRC_MISMATCH)
    {
      // packet was received, but is malformed
      Serial.println(F("CRC error!"));
    }
    else
    {
      // some other error occurred
      Serial.print(F("failed, code "));
      Serial.println(state);
    }

    // put module back to listen mode
    radio.startReceive();
  }
}