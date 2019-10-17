import json
import RPi.GPIO as GPIO
from azure.servicebus.control_client import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

bus_service = ServiceBusService(
    service_namespace='***REPLACE ME, with your Service Bus Namespace Name***',
    shared_access_key_name='***REPLACE ME, with your Shared Access Policy Name***',
    shared_access_key_value='***REPLACE ME, with your Shared Access Key Value***')

while True:
	msg = bus_service.receive_subscription_message('***REPLACE ME with your Service Bus Topic Name***', '***REPLACE ME with your Service Bus Topic Subscription Name***', peek_lock=True)
	if msg.body is not None:
		value = json.loads(msg.body.decode("utf-8"))
		print(value["status"])
		if value["status"]==1:
			GPIO.output(8,GPIO.HIGH)
			print('The LED has been turned ON.')
		elif value["status"]==0:
			GPIO.output(8,GPIO.LOW)
			print('The LED has been turned OFF.')
		else:
			print("Please enter a valid value.")
	msg.delete()
