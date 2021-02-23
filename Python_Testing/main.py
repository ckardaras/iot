# Initial testing script to invoke the IoT tests
from SerialConnect import SerialConnect
import time

connection = SerialConnect("COM6")

#connection.Initialize_Board()
#connection.Setup_PDP_Context()
connection.Basic_Up_Test()

connection.MQTT_Login_Test("ec2-44-238-142-208.us-west-2.compute.amazonaws.com")