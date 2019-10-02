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

from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# The device connection string to authenticate the device with your IoT hub.
CONNECTION_STRING = "Paste your IoT Device Primary Connection String here..."

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

MSG_TXT = "{\"distance\": %.2f}"

def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

def iothub_client_telemetry_sample_run():

    try:
        client = iothub_client_init()
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

            message = IoTHubMessage(msg_txt_formatted)

            # Send the message.
            print( "Sending message: %s" % message.get_string() )
            client.send_event_async(message, send_confirmation_callback, None)
            time.sleep(3)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()
