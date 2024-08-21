#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#define WIFI_SSID "IOT"
#define WIFI_PASS "fancyunicorn486"
#define POST_URL "https://echo.free.beeceptor.com"
#define RXD 18
#define TXD 19
#define RP2040 Serial1
const char *ssid = WIFI_SSID;
const char *password = WIFI_PASS;

// Your Domain name with URL path or IP address with path
String serverName = POST_URL;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;
// Timer set to 10 minutes (600000)
// unsigned long timerDelay = 600000;
// Set timer to 5 seconds (5000)
unsigned long timerDelay = 5000;

void setup()
{
    Serial.begin(115200);
    RP2040.begin(115200, SERIAL_8N1, RXD, TXD);
    WiFi.begin(ssid, password);
    Serial.println("Connecting");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to WiFi network with IP Address: ");
    Serial.println(WiFi.localIP());

    Serial.println("Timer set to 5 seconds (timerDelay variable), it will take 5 seconds before publishing the first reading.");
}
String readJson()
{
    String buffer;
    while (RP2040.available())
    {
        String c = String(RP2040.read());
        if (c.equals("\r"))
        {
            String c2 = String(RP2040.read());
            if (c2.equals("\n"))
            {
                return buffer;
            }
        }
        buffer += c;
    }
}
void loop()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        if (RP2040.available())
        {
            StaticJsonDocument<300> doc;

            // Read the JSON document from the "link" serial port
            DeserializationError err = deserializeJson(doc, RP2040);

            if (err == DeserializationError::Ok)
            {
                WiFiClientSecure client;
                HTTPClient http;

                String serverPath = POST_URL;

                // Your Domain name with URL path or IP address with path
                http.begin(client, serverPath.c_str());

                // If you need Node-RED/server authentication, insert user and password below
                // http.setAuthorization("REPLACE_WITH_SERVER_USERNAME", "REPLACE_WITH_SERVER_PASSWORD");

                // Send HTTP GET request
                String json;
                serializeJson(doc, json);
                int httpResponseCode = http.POST(json);

                if (httpResponseCode > 0)
                {
                    Serial.print("HTTP Response code: ");
                    Serial.println(httpResponseCode);
                    String payload = http.getString();
                    Serial.println(payload);
                }
                else
                {
                    Serial.print("Error code: ");
                    Serial.println(httpResponseCode);
                }
                // Free resources
                http.end();
            }
            else
            {
                // Print error to the "debug" serial port
                Serial.print("deserializeJson() returned ");
                Serial.println(err.c_str());

                // Flush all bytes in the "link" serial port buffer
                while (Serial1.available() > 0)
                    Serial1.read();
            }
        }
    }
    else
    {
        Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
}
