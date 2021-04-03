# Main program to simulate the different protocols
from SerialConnect import SerialConnect
from MqttSaraR5 import MqttSaraR5
from CoapSaraR5 import CoapSaraR5

import time
import argparse
import json

"""
 basic chunking of payloads since there is a limit of 1024 bytes in the AT commands
 if the desired payload exceeds @param chunk_size, the payload will be split up and sent
 individually

 !important this method relies on the assumption that a single event does not exceed
 the desired @param chunk_size
"""
def get_payload_chunks(json_events, chunk_size):
	events_list = []
	next_event = []
	# iterate through all of the events and add 'chunk_size' byte chunks to the events list
	for event in json_events:
		if (len(str(next_event)) + len(str(event))) < chunk_size:
			next_event.append(event)
		else:
			events_list.append(next_event)
			next_event = []
	events_list.append(next_event)

	return events_list

def main():
	# option to read in a file for sending data
	# consistent source to be able to compare the different protocols

	parser = argparse.ArgumentParser(description='SARA R5 Simulation Program')
	parser.add_argument("--com_port", default="COM6", help="Defines which COM port to use via serial")
	parser.add_argument("--wait_time", default=8, help="Defines how long to wait in seconds in between each data transfer", type=int)
	parser.add_argument("--protocol", default="mqtt", choices=['mqtt', 'coap', 'amqp', 'all'], help="Defines which protocol to simulate")
	parser.add_argument("--mqtt_topic", default="test", help="The topic to send data to via MQTT")
	parser.add_argument("--init", action='store_true', help="Use this switch if board needs to be setup and have the PDP context initialized")
	parser.add_argument("--datafile", help="JSON events data to send via specified IoT protocol", required=True)
	parser.add_argument("--serial_number", help="The serial number associated with the device", required=True)

	args = parser.parse_args()

	# ingest the data file into a dictionary using the json library
	datafile = open(args.datafile, "r")
	json_data = json.load(datafile)
	datafile.close()

	# Pull payloads from the json input file
	payloads = None

	if "payloads" in json_data:
		payloads = json_data["payloads"]

	if payloads == None:
		print("[-] title 'payloads' not found in json data!")
		return

	# check if we want to test the AMQP protocol which has to be done via pc client
	if (args.protocol == "amqp") or (args.protocol == "all"):
		import pika

		# setup the channel connection with the setup user 'test_device'
		creds = pika.PlainCredentials('test_device', 'THISi5@T3stP@ssW0rD')
		connection = pika.BlockingConnection(
	    	pika.ConnectionParameters('44.238.142.208', 5672, '/', creds))
		channel = connection.channel()

		# publish data to the events queue
		channel.queue_declare(queue='events')

		for payload in payloads["payload"]:
			print("Payload Description: " + payload["description"])
			payload_chunks = get_payload_chunks(payload["events"], 1000)
			for chunk in payload_chunks:
				# append the serial number to the beginning of the json packet
				packet = {args.serial_number : chunk}
				# publish all of the events in the payload
				channel.basic_publish(exchange='', routing_key='events', body=str(packet))
			# allow some time to sleep to gather current measurements
			time.sleep(args.wait_time)
		
		connection.close()

	# setup the serial connection only if we need to use mqtt or coap
	if(args.protocol != "amqp"):
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
			# give some sleep time to be visible in the current consumption testing
			time.sleep(2)
			for payload in payloads["payload"]:
				print("Payload Description: " + payload["description"])
				payload_chunks = get_payload_chunks(payload["events"], 1000)
				for chunk in payload_chunks:
					# append the serial number to the beginning of the json packet
					packet = {args.serial_number : chunk}
					# publish all of the events in the payload with qos level 1
					mqtt.MQTT_Publish(topic=args.mqtt_topic, data=str(packet), qos=1)
				# allow some time to sleep to gather current measurements
				time.sleep(args.wait_time)
			mqtt.MQTT_Disconnect()

		# CoAP testing
		if((args.protocol == "coap") or (args.protocol == "all")):
			# Simulate the CoAP protocol using the CoapSaraR5 class
			coap = CoapSaraR5(connection, "coap://44.238.142.208:5683/")

			coap.Coap_Configure()
			# give some sleep time to be visible in the current consumption testing
			time.sleep(2)
			count = 0
			for payload in payloads["payload"]:
				print("Payload Description: " + payload["description"])
				# maximum octet string is 512 bytes for the coap commands so must be limited here
				payload_chunks = get_payload_chunks(payload["events"], 400)
				for chunk in payload_chunks:
					# append the serial number to the beginning of the json packet
					packet = {args.serial_number : chunk}
					# the only resource configured right now is /test
					# use a count iterator to specify different resources for each payload (simulates a timestamp)
					resource = "test/{}-{}".format(args.serial_number, count)
					coap.Coap_POST(resource_uri=resource, data=str(packet), use_con = False)
					count += 1
				# allow some time to sleep to gather current measurements
				time.sleep(args.wait_time)

if __name__ == "__main__":
	main()