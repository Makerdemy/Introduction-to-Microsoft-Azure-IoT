// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. 

#include <WiFi.h>
#include "DHT.h"
#include "AzureIotHub.h"
#include "Esp32MQTTClient.h"

#define INTERVAL 2000

#define DEVICE_ID "ESP32Device"

#define MESSAGE_MAX_LEN 256

#define DHTPIN 4

#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Please input the SSID and password of WiFi
const char* ssid     = "REPLACE ME !! !@#$%^&*"; // Name of your Wi-Fi Network.
const char* password = "REPLACE ME !! !@#$%^&*"; // Enter your Wi-Fi Network Security Key / Password
//Replace the above placeholders with your WiFi network's credentials.

int messageCount = 1;

/*String containing Hostname, Device Id & Device Key in the format:                         */
/*  "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"                */
/*  "HostName=<host_name>;DeviceId=<device_id>;SharedAccessSignature=<device_sas_token>"    */
static const char* connectionString = "REPLACE ME !! Paste your IoT Device Connection String here...";
//Replace the above placeholder with the primary connection string of your IoT device.

const char *messageData = "{\"deviceId\":\"%s\", \"messageId\":%d, \"Temperature\":%f, \"Humidity\":%f}";

static bool hasWifi = false;

static bool messageSending = true;
static uint64_t send_interval_ms;

// Utilities

static void InitWifi()
{
  Serial.println("Connecting...");

  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  hasWifi = true;
  
  Serial.println("WiFi connected");
  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

//Function definition

static void SendConfirmationCallback(IOTHUB_CLIENT_CONFIRMATION_RESULT result)
{
  if (result == IOTHUB_CLIENT_CONFIRMATION_OK)
  {
    Serial.println("Send Confirmation Callback finished.");
  }
}

// Arduino sketch
void setup()
{
  
  Serial.begin(115200);
  
  Serial.println(F("DHT11 test!"));
  
  dht.begin();
  
  Serial.println("ESP32 Device");
  Serial.println("Initializing...");

  //Initialize the WiFi module
  Serial.println(" > WiFi");
  hasWifi = false;
  
  InitWifi();
  
  if (!hasWifi)
  {
    return;
  }
  
  
  Serial.println(" > IoT Hub");
    
  
  Esp32MQTTClient_Init((const uint8_t*)connectionString);

  //bool Esp32MQTTClient_Init(const uint8_t* deviceConnString, bool hasDeviceTwin = false, bool traceOn = false);
/**
* @brief    Initialize a IoT Hub MQTT client for communication with an existing IoT hub.
*           The connection string is load from the EEPROM.
* @param    deviceConnString   Device connection string.
* @param    hasDeviceTwin   Enable / disable device twin, default is disable.
* @param    traceOn         Enable / disable IoT Hub trace, default is disable.
*
* @return   Return true if initialize successfully, or false if fails.
*/

  Esp32MQTTClient_SetSendConfirmationCallback(SendConfirmationCallback);

//void Esp32MQTTClient_SetSendConfirmationCallback(SEND_CONFIRMATION_CALLBACK send_confirmation_callback);
/**
* @brief    Sets up send confirmation status callback to be invoked representing the status of sending message to IOT Hub.
*/

  send_interval_ms = millis();
}

void loop()
{
  if (hasWifi)
  {
    if (messageSending && 
        (int)(millis() - send_interval_ms) >= INTERVAL)
    {
      
      char messagePayload[MESSAGE_MAX_LEN];
      
      float temperature = dht.readTemperature();
      
      float humidity = dht.readHumidity();
      
      snprintf(messagePayload,MESSAGE_MAX_LEN,messageData, DEVICE_ID, messageCount++, temperature,humidity);
      //snprintf(char *str, size_t size,  const char *format, ...)
      //snprintf(buffer,    maximum size, const char *format (i.e template), other arguments.....)
      
      Serial.println(messagePayload);
      
      EVENT_INSTANCE* message = Esp32MQTTClient_Event_Generate(messagePayload, MESSAGE);

                                //Esp32MQTTClient_Event_Generate(const char *eventString, EVENT_TYPE type);
/**
* @brief    Generate an event with the event string specified by @p eventString.
*
* @param    eventString             The string of event.
*
* @return   EVENT_INSTANCE upon success or an error code upon failure.
*/
      
      Esp32MQTTClient_SendEventInstance(message);

//bool Esp32MQTTClient_SendEventInstance(EVENT_INSTANCE *event);
/**
* @brief    Synchronous call to report the event specified by @p event.
*
* @param    event               The event instance.
*
* @return   Return true if send successfully, or false if fails.
*/
      
      send_interval_ms = millis();
    }
  }
  delay(10);
}
