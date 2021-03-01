# Initial testing script to invoke the IoT tests
from SerialConnect import SerialConnect
from MqttSaraR5 import MqttSaraR5
from CoapSaraR5 import CoapSaraR5

import time

connection = SerialConnect("COM6")

# Setup the board and the PDP context to connect to the internet
# then test that the board can ping google.com
#**********************************************************************
# Only need to run this section once to get the board working, comment
# this section out when board is operational on the network/internet
connection.Initialize_Board()
connection.Setup_PDP_Context()
connection.Basic_Up_Test()
#**********************************************************************

# Simulate the MQTT protocol using the MqttSaraR5 class
mqtt = MqttSaraR5(connection,"ec2-44-238-142-208.us-west-2.compute.amazonaws.com", 1883)

mqtt.MQTT_Connect()
mqtt.MQTT_Subscribe("test")
mqtt.MQTT_Publish(topic="test", data="Hello World")
mqtt.MQTT_Read_Data()
mqtt.MQTT_Disconnect()

# Simulate the CoAP protocol using the CoapSaraR5 class
coap = CoapSaraR5(connection, "coap://44.238.142.208:5683/")

#coap.Coap_Configure()
# the only resource configured right now is /basic 
coap.Coap_PUT(resource_uri = "basic", data = "TESTING the resource" , use_con = False)
coap.Coap_GET(resource_uri = "basic", use_con = False)