#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_MCP2515.h>
#include <RadioLib.h>
#include <Wire.h>
#include <constants.h>
#include <data.h>

#define CS_PIN PIN_CAN_CS
#define INT_PIN PIN_CAN_INTERRUPT
#define START_HEADER "Convoy Agent Commit:" COMMIT_HASH
#define CAN_BAUDRATE (500000)



#define A value[0]
#define B value[1]
#define C value[2]
#define D value[3]

#define CC1101_CS_PIN 25
#define CC1101_GDO0_PIN 24
#define CC1101_GDO2_PIN 4

Adafruit_MCP2515 CAN(CS_PIN);

CC1101 radio = new Module(CC1101_CS_PIN, CC1101_GDO0_PIN, RADIOLIB_NC, CC1101_GDO2_PIN);

volatile bool transmittedFlag = false;
int transmissionState = RADIOLIB_ERR_NONE;
int count = 0;

Packet currentValues;

void setFlag(void)
{
    transmittedFlag = true;
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
void initRadio()
{
    Serial.print(F("Initializing radio... "));
    int state = radio.begin();
    state = radio.setNodeAddress(0x01, 1);
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
    radio.setPacketSentAction(setFlag);
    radio.setFrequency(FREQ);
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
    Serial.begin(115200);
    while (!Serial)
        delay(10);
    delay(2000);
    Serial.println(START_HEADER);
    initCAN();
    initRadio();
}
void transmitData()
{
    Serial.print(F("Transmitting data..."));
    String str = "Hello World! #" + String(count++);
    transmissionState = radio.startTransmit(str);
}
int last = millis();
void loop()
{
    if (transmittedFlag)
    {
        transmittedFlag = false;
        if (transmissionState == RADIOLIB_ERR_NONE)
        {
            Serial.println(F("Transmission finished!"));
        }
        else
        {
            Serial.print(F("Transmission failed, code "));
            Serial.println(transmissionState);
        }
        radio.finishTransmit();
        delay(1000);
    } else {
        if ((millis() - last) > 5000) {
            last = millis();
            transmitData();
        }
    }
}