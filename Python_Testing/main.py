# Initial testing script to invoke the IoT tests
from SerialConnect import SerialConnect
import time

connection = SerialConnect("COM6")

#connection.Initialize_Board()
#connection.Setup_PDP_Context()
#connection.Basic_Up_Test()

# Simulate the MQTT protocol
connection.MQTT_Connect("ec2-44-238-142-208.us-west-2.compute.amazonaws.com")
connection.MQTT_Subscribe("test")
connection.MQTT_Publish(topic="test", data="Hello World")
connection.MQTT_Read_Data()
connection.MQTT_Disconnect()