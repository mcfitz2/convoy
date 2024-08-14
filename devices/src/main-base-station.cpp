#include <Arduino.h>
#include <RadioLib.h>
#include <Wire.h>
#include <config.h>

#define START_HEADER "Convoy Base Station" Commit: COMMIT_HASH

#define CC1101_CS_PIN 10
#define CC1101_GDO0_PIN 2
#define CC1101_GDO2_PIN 3


CC1101 radio = new Module(CC1101_CS_PIN, CC1101_GDO0_PIN, RADIOLIB_NC, CC1101_GDO2_PIN);

volatile bool receivedFlag = false;


#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
  // we got a packet, set the flag
  receivedFlag = true;
}
void initRadio()
{
    Serial.print(F("Initializing radio... "));
    int state = radio.begin();
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
    radio.setFrequency(FREQ);
}
void setup() {
  Serial.begin(BAUD_RATE);

}
void loop () {

}