#!/bin/bash
sudo apt update
sudo apt install snapd
snap install mosquitto
sudo apt install python3-pip
pip3 install paho-mqtt
#install location
#cd /home/$(whoami)/.local/lib/python3.8/site-packages/paho/mqtt
#if you want wireshark
#sudo apt install wireshark
cd ~/Desktop



#make client
echo 
'import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()' >> eclipse_client.py

python3 eclipse_client.py

#make your own broker
#sudo apt-get install mosquitto mosquitto-clients
