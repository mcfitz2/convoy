#ifndef BAUD_RATE
#define BAUD_RATE 115200
#endif
#ifndef COMMIT_HASH
#define COMMIT_HASH "UNK"
#endif
#define FREQ 433.0

#define PID_RESPONSE_ID 0x7E8
#define VIN_CAN_ID 0x40A
#define PID_REQUEST_ID 0x7Df
#define DISTANCE_TRAVELED_WITH_MIL_ON 0x21
#define DISTANCE_TRAVELED_SINCE_CODES_CLEARED 0x31
#define CONTROL_MODULE_VOLTAGE 0x42
#define FUEL_TANK_LEVEL_INPUT 0x2f
#define AMBIENT_AIR_TEMPERATURE 0x46
#define TIME_RUN_WITH_MIL_ON 0x4d
#define TIME_SINCE_TROUBLE_CODES_CLEARED 0x4e


#define PORTAL_SSID "convoy"


#define mqtt_server       "xxx.cloudmqtt.com"
#define mqtt_port         "12345"
#define mqtt_user         "mqtt_user"
#define mqtt_pass         "mqtt_pass"
#define topic    "convoy"