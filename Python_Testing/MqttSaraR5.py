from SerialConnect import SerialConnect

class MqttSaraR5:
    """
        Simple class constructor for the MqttConnect class

        @param ser (SerialConnect)
            A SerialConnect object passed in to utilize the functions in the SerialConnect
            class for sending AT commands to the SARA R5 board

        @param broker (string)
            The url of the MQTT broker to connect to

        @param port (int)
            The port to be used in the MQTT connection
    """
    def __init__(self, ser: SerialConnect, broker: str, port: int = 1883):
        self.ser = ser
        self.mqtt_server_name = broker
        self.mqtt_port = port

    """
        This function will establish an unsecure connection to an MQTT broker

        @param mqtt_server_name (string)
            denotes the url of the mqtt broker to connect to
    """
    def MQTT_Connect(self):
        # run the command to setup the connection info
        assert "OK" in self.ser.Send_AT_Command('AT+UMQTT=2,"{}",{}'.format(self.mqtt_server_name, self.mqtt_port)), "Connection info failed to set"
        # setup the secure connection to no TLS encryption which runs over port 1883
        assert "OK" in self.ser.Send_AT_Command("AT+UMQTT=11,0,0"), "Failed to set MQTT secure option"
        # try to setup a connection to the MQTT server
        assert "+UUMQTTC: 1,1" in self.ser.Send_AT_Command("AT+UMQTTC=1", True), "login failed"

        print("\n[+] Successfully connected to MQTT broker\n")

    """
        This function will logout from an established MQTT connection
    """
    def MQTT_Disconnect(self):
        assert "+UUMQTTC: 0,1" in self.ser.Send_AT_Command("AT+UMQTTC=0", True), "logout failed"

        print("\n[+] Successfully disconnected from MQTT broker\n")

    """
        This function will send an AT command to subscribe to a topic

        @param topic (string)
            Denotes what topic to subscribe to from the MQTT broker
    """
    def MQTT_Subscribe(self, topic: str):
        assert '+UUMQTTC: 4,1,0,"{}"'.format(topic) in self.ser.Send_AT_Command('AT+UMQTTC=4,0,"{}"'.format(topic), True), "Failed to Subscribe"
 
        print("\n[+] Successfully subscribed to topic: "+ topic +"\n")

    """
        This function will send an AT command to publish to a topic

        @param topic (string)
            Denotes what topic to publish to from the MQTT broker

        @param data (string)
            Denotes what data to publish on the topic

        @param qos (int)
            Denotes what quality of service level to use, defaults to QoS level 0

        @param retain (int)
            Denotes whether or not to retain the messages on the broker across disconnects defaults to 0
    """
    def MQTT_Publish(self, topic: str, data: str, qos: int = 0, retain: int = 0):
        assert "+UUMQTTC: 2,1" in self.ser.Send_AT_Command('AT+UMQTTC=2,{},{},0,"{}","{}"'.format(qos,retain,topic,data), True), "Failed to Publish"

        print("\n[+] Successfully published "+ data +" to topic: "+ topic +"\n")

    """
        This function will read data received as a result of subscribing to a topic
    """
    def MQTT_Read_Data(self):
        assert "OK" in self.ser.Send_AT_Command("AT+UMQTTC=6,0"), "Read Failed"

        print("\n[+] Successfully Read Data from MQTT Subscription\n")

    """********************************************************************
        THE FOLLOWING ARE TESTS TO VALIDATE MQTT ON THE BOARD
    *********************************************************************"""

    """
        Tests the basic MQTT login functionality to make sure the board can make a
        successful connection to the MQTT broker

        @param mqtt_server_name (string)
            Specifies the mqtt server to make the connection
    """
    def MQTT_Login_Test(self, mqtt_server_name: str):
        # reset the buffer to make sure we aren't getting weird residual values
        self.MQTT_Connect(mqtt_server_name)
        self.MQTT_Disconnect()

        print("\n[+] Board successfully made a connection to the MQTT server\n")

    """
        Tests the basic MQTT Pub/Sub functionality to make sure the board can publish and
        subscribe to a topic on the broker

        @param mqtt_server_name (string)
            Specifies the mqtt server to make the connection
    """
    def MQTT_Pub_Sub_Test(self, mqtt_server_name: str):
        # connect to the server
        self.MQTT_Connect(mqtt_server_name)
        # Subscribe to the topic "test"
        self.MQTT_Subscribe("test")
        # publish test data to topic test
        self.MQTT_Publish(topic="test", data="12345")
        # disconnect from the server
        self.MQTT_Disconnect()

        print("\n[+] Board successfully published and subscribed to the MQTT server\n")