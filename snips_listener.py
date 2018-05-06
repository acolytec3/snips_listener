#!/usr/bin/python3

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from importlib import import_module
import snipsDefaults as snips


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("hermes/intent/#")
	client.subscribe("hermes/nlu/#")
	client.subscribe("hermes/asr/#")
	client.subscribe("hermes/dialogueManager/#")
	client.subscribe('hermes/hotword/default/detected')
	client.subscribe('hermes/tts/#')

def asr(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))
	data = json.loads(msg.payload.decode())
	print(data)

def tts(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))
	data = json.loads(msg.payload.decode())
	print(data)

		
def dialogueManager(client, userdata, msg):
	data = json.loads(msg.payload.decode())
	print(data)
	print(msg.topic+" "+str(msg.payload.decode()))

# The callback for when a PUBLISH message is received from the server.
def handle_intent(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))
	data = json.loads(msg.payload.decode())
	snips.previousIntent = msg
	print("data.sessionId"+data['sessionId'])
	print("data.intent"+str(data['intent']))
	print("data.slots"+str(data['slots']))
	me,funcName = data['intent']['intentName'].split(':')
	try:
		func = import_module(funcName)  # Looks in sub-directory of the current directory to find the appropriate skill/module
		response = func.run(data)
		payload = {'sessionId': data.get('sessionId', ''),'text':response}
		publish.single('hermes/dialogueManager/endSession',payload=json.dumps(payload),hostname=snips.mqtt_host,port=snips.mqtt_port)
	except:
		payload = {'sessionId': data.get('sessionId', ''),'text': "I do not know how to do that yet"}
		publish.single('hermes/dialogueManager/endSession',payload=json.dumps(payload),hostname=snips.mqtt_host,port=snips.mqtt_port)		
	
def intentNotRecognized(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))
	data = json.loads(msg.payload.decode())
	print(data)
# Intent isn't recognized so session will already have ended
# so we send a notification instead.
	
	if 'sessionId' in data:
		payload = {'sessionId': data.get('sessionId', ''),'text': "I am not sure what to do"}
		publish.single('hermes/dialogueManager/endSession',payload=json.dumps(payload),hostname=snips.mqtt_host,port=snips.mqtt_port)

def nlu(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))
    data = json.loads(msg.payload.decode())
    print(data)

def hotword(client, usrdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))
		
def parse_slots(msg):
	data = json.loads(msg.payload.decode())
	return dict((slot['slotName'], slot['value']['value']) for slot in data['slots'])


client = mqtt.Client()
client.on_connect = on_connect

# These are here just to print random info for you
client.message_callback_add("hermes/asr/#", asr)
client.message_callback_add("hermes/dialogueManager/#", dialogueManager)
client.message_callback_add("hermes/nlu/#", nlu)
client.message_callback_add("hermes/nlu/intentNotRecognized", intentNotRecognized)
client.message_callback_add("hermes/hotword/default/detected", hotword)
client.message_callback_add("hermes/tts/say", tts)

# This function responds to all intents
client.message_callback_add("hermes/intent/#", handle_intent)

client.connect(snips.mqtt_host, snips.mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
