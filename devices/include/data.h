
#include <Arduino.h>
struct Packet
{
   char     vin[17];
   uint16_t batteryVoltage;
   uint16_t distanceSinceCodesReset;
   uint16_t distanceWithMILOn;
   uint16_t timeSinceCodesReset;
   uint8_t  ambientAirTemp;
   uint8_t  fuelLevel;
};