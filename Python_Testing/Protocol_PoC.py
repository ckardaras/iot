# Main program to simulate the different protocols

from SerialConnect import SerialConnect
from MqttSaraR5 import MqttSaraR5
from CoapSaraR5 import CoapSaraR5

import time
import argparse
import json

def main():
	# option to read in a file for sending data
	# consistent source to be able to compare the different protocols

	parser = argparse.ArgumentParser(description='SARA R5 Simulation Program')
	parser.add_argument("--com_port", default="COM6", help="Defines which COM port to use via serial")
	parser.add_argument("--wait_time", default=5, help="Defines how long to wait in seconds in between each data transfer", type=int)
	parser.add_argument("--protocol", default="mqtt", choices=['mqtt', 'coap', 'all'], help="Defines which protocol to simulate")
	parser.add_argument("--mqtt_topic", default="test", help="The topic to send data to via MQTT")
	parser.add_argument("--init", action='store_true', help="Use this switch if board needs to be setup and have the PDP context initialized")
	parser.add_argument("--datafile", help="JSON events data to send via specified IoT protocol")

	args = parser.parse_args()

	# ingest the data file into a dictionary using the json library
	datafile = open(args.datafile, "r")
	json_data = json.load(datafile)
	datafile.close()

	payloads = None

	if "payloads" in json_data:
		payloads = json_data["payloads"]

	if payloads == None:
		print("[-] title 'payloads' not found in json data!")
		return

	# setup the serial connection over the specified com port
	connection = SerialConnect(args.com_port)

	if(args.init):
		# Setup the board and verify its connection
		connection.Initialize_Board()
		connection.Setup_PDP_Context()
		connection.Basic_Up_Test()

	# MQTT testing
	if((args.protocol == "mqtt") or (args.protocol == "all")):
		mqtt = MqttSaraR5(connection,"ec2-44-238-142-208.us-west-2.compute.amazonaws.com", 1883)

		mqtt.MQTT_Connect()
		for payload in payloads["payload"]:
			print("Payload Description: " + payload["description"])
			# iterate through each of the events and send the data
			for event in payload["events"]:
				mqtt.MQTT_Publish(topic=args.mqtt_topic, data=str(event))
			time.sleep(args.wait_time)
		mqtt.MQTT_Disconnect()

	# CoAP testing
	if((args.protocol == "coap") or (args.protocol == "all")):
		# Simulate the CoAP protocol using the CoapSaraR5 class
		coap = CoapSaraR5(connection, "coap://44.238.142.208:5683/")

		coap.Coap_Configure()
		count = 0
		for payload in payloads["payload"]:
			print("Payload Description: " + payload["description"])
			# iterate through each of the events and send the data
			for event in payload["events"]:
				# the only resource configured right now is /test
				coap.Coap_POST(resource_uri="test/device0-"+str(count), data=str(event), use_con = False)
				count += 1
			time.sleep(args.wait_time)

if __name__ == "__main__":
	main()