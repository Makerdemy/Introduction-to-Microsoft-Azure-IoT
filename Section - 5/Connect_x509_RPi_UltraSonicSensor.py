
from paho.mqtt import client as mqtt # be sure to install package paho-mqtt
import ssl
import random
import time
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO                    #Import GPIO library
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering
TRIG = 23                                  #Associate pin 23 to TRIG
ECHO = 24                                  #Associate pin 24 to ECHO
print("Distance measurement in progress")

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

GPIO.output(TRIG, False)                 #Set TRIG as LOW
print("Waitng For Sensor To Settle")
time.sleep(2)                            #Delay of 2 seconds
# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

deviceCert = "REPLACE ME !! Path of your cert.pem file."
deviceCertKey = "REPLACE ME !! Path of your key.pem file."

HubName = "Replace with Host-name of your IoT Hub"
devicename = "Specify the name of your X.509 device registered with your IoT Hub"

MSG_TXT = "{\"distance\": %.2f}"

def iothub_client_telemetry_sample_run():

    try:
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        while True:

            GPIO.output(TRIG, True)                  #Set TRIG as HIGH
            time.sleep(0.00001)                      #Delay of 0.00001 seconds
            GPIO.output(TRIG, False)                 #Set TRIG as LOW

            while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
              pulse_start = time.time()              #Saves the last known time of LOW pulse

            while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
              pulse_end = time.time()                #Saves the last known time of HIGH pulse

            pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

            distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
            distance = round(distance, 2) - 0.5            #Round to two decimal points

            if distance > 2 and distance < 400:
                print("Distance:",distance,"cm")
            else:
                print("Out of range.")

            msg_txt_formatted = MSG_TXT % (distance)
            message = msg_txt_formatted

            # Send the message.
            print( "Sending message: %s" % message)
            client.publish("devices/" + devicename + "/messages/events/", message, qos=1)
            time.sleep(3)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

client = mqtt.Client(client_id=devicename, protocol=mqtt.MQTTv311)
client.username_pw_set(username=HubName + "/" + devicename, password=None)
client.tls_set( certfile=deviceCert, keyfile=deviceCertKey, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.connect(HubName, port=8883)
iothub_client_telemetry_sample_run()
client.loop_forever()
