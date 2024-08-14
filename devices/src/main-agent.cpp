#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_MCP2515.h>
#include <RadioLib.h>
#include <Wire.h>
#include <config.h>


#define CS_PIN PIN_CAN_CS
#define INT_PIN PIN_CAN_INTERRUPT
#define START_HEADER "Convoy Agent" Commit: COMMIT_HASH
#define CAN_BAUDRATE (500000)

#define PID_RESPONSE_ID 0x7E8
#define VIN_CAN_ID 0x40A
#define PID_REQUEST_ID 0x7Df
#define DISTANCE_TRAVELED_WITH_MIL_ON 0x21
#define DISTANCE_TRAVELED_SINCE_CODES_CLEARED 0x31
#define CONTROL_MODULE_VOLTAGE 0x42
#define DISTANCE_TRAVELED_WITH_MIL_ON 0x21
#define DISTANCE_TRAVELED_SINCE_CODES_CLEARED 0x31
#define CONTROL_MODULE_VOLTAGE 0x42

#define A value[0]
#define B value[1]
#define C value[2]
#define D value[3]

#define CC1101_CS_PIN 10
#define CC1101_GDO0_PIN 2
#define CC1101_GDO2_PIN 3

Adafruit_MCP2515 CAN(CS_PIN);

CC1101 radio = new Module(CC1101_CS_PIN, CC1101_GDO0_PIN, RADIOLIB_NC, CC1101_GDO2_PIN);

volatile bool transmittedFlag = false;
int transmissionState = RADIOLIB_ERR_NONE;
int count = 0;

float distanceTraveled;
float batteryVoltage;
char vin[17];

void setFlag(void)
{
    transmittedFlag = true;
}

float parseOBDPacket()
{
    int canId = 0;
    uint8_t value[4];
    int read = CAN.readBytes((uint8_t*)value, 3);
    switch (canId)
    {
    case CONTROL_MODULE_VOLTAGE:
        return ((A * 256.0 + B) / 1000.0);
    case DISTANCE_TRAVELED_WITH_MIL_ON:
    case DISTANCE_TRAVELED_SINCE_CODES_CLEARED:
        return (A * 256.0 + B);
    default:
        return 0.0;
    }
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
        parseOBDPacket();
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
}
void transmitData()
{
    Serial.print(F("Transmitting data..."));
    String str = "Hello World! #" + String(count++);
    transmissionState = radio.startTransmit(str);
}
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
    }
}