# Basic Unit Testing Suite for IoT Evaluation on the SARA R5 EVK board from UBLOX
import serial
import time


"""
    Helper function for the Send_AT_Command function to parse through the results
    and check for a certain value

    @param ser_response (list)
        the results list from the serial readlines() function which is 
        used to parse through searching for token

    @param token (string)
        the token to search ser_response for and remove it

    @param wait_for_result (boolean)
        specifies whether or not we are waiting for an extra result other than OK

    @return (list)
        returns an updated list of the serial response
"""

def Clean_Results(ser_response: list(), token: str, wait_for_result: bool) -> list:
    i = 0
    while i < len(ser_response):
        # make sure the value is not in the list
        response = ser_response[i].decode('utf-8').strip()
        if (response == token) | (wait_for_result & ((response == "OK") | (response == ""))):
            ser_response.pop(i)
        else:
            i += 1

    return ser_response

"""
    Class definition and method declaration for the SerialConnect class.
    This class defines all of the necessary components to make connections to
    the SARA R5 board and run automated testing to verify connection is being established
"""

class SerialConnect:
    """
        Simple class constructor for the SerialConnect class
        @param com_port (string)
            specifies which communication port to open a serial connection to
        @param baud_rate (int)
            Used in setting up the baud rate to use for the serial connection
            default to 115200 which is the standard baud rate for the SARA R5 EVK board
    """
    def __init__(self, com_port: str, baud_rate: int = 115200):
        self.ser = serial.Serial(com_port, baud_rate, timeout=1)   # initialize serial connection

    """
        Simple class destructor for the SerialConnect class
            tears down the serial connection gracefully
    """
    def __del__(self):
        self.ser.flush()
        self.ser.close()

    """
        Handles the sending of AT commands via Serial connection
        @param cmd (string)
            specifies what AT command to send to the device
            defaults to the string AT which should just return an OK

        @param wait_for_result (bool)
            Used for commands that have an extra output other than OK which may return
            a little later.  Waits for the desired result instead of the immediate OK
            that will return first.

        @return
            returns a string from the serial connection as a result from the AT command
    """
    def Send_AT_Command(self, cmd: str = "AT", wait_for_result: bool = False) -> str:
        print ('Writing: ' + cmd)
        assert len(cmd) > 0, "Sent an empty string as AT command"

        # check if cmd is a properly \r terminated string
        if cmd[-1] != '\r':
            cmd = cmd + '\r'
        self.ser.write(str.encode(cmd))     # send the command
        
        # get data from the in buffer
        ser_response = self.ser.readlines()
        # check and strip the first response if it is the command we sent
        ser_response = Clean_Results(ser_response, cmd[:-1], wait_for_result)

        # wait until we get some data in the in_buffer
        while (ser_response == []):
            ser_response = self.ser.readlines()
            # make sure we don't include the command in our result list
            ser_response = Clean_Results(ser_response, cmd[:-1], wait_for_result)

        # read from the in_buffer and append them to the response_list
        print("AT Response: ")
        response_list = []
        for line in ser_response:
            line = line.decode('utf-8').strip()
            response_list.append(line)
            print(line)

        # filter out occurrences of '' from the list of responses
        response_list = list(filter(lambda x: x != '', response_list))
        return response_list

    """
        This function will run all of the necessary commands to setup the SARA R5 board
        with the proper values to connect to the cell network.  Run this command at first board
        startup to establish the required values to connect to the AT&T network.  This requires
        the use of an AT&T SIM card.
    """

    def Initialize_Board(self):
        # reset the buffer to make sure we aren't getting weird residual values
        self.ser.reset_input_buffer()
        # turn the cell functionality off 
        assert "OK" in self.Send_AT_Command("AT+CFUN=0"), "Cell functionality failed to turn off"
        # set the MNO profile to 2 for AT&T
        assert "OK" in self.Send_AT_Command("AT+UMNOPROF=2"), "MNO profile failed to set to AT&T"
        # setup the PDP context to use the AT&T apn_name of m2m.com.attz
        assert "OK" in self.Send_AT_Command('AT+CGDCONT=1,"IPV4V6","m2m.com.attz"'), "PDP context failed to set"
        # reset the modem for the new attributes to take place
        assert "OK" in self.Send_AT_Command("AT+CFUN=16"), "Board failed to reset"
        time.sleep(5)
        # check that the modem has properly retained values
        assert "+UMNOPROF: 2" in self.Send_AT_Command("AT+UMNOPROF?"), "MNO settings failed to retain"
        # turn the radio functionality back on so we can connect to the network
        assert "OK" in self.Send_AT_Command("AT+CFUN=1"), "Cell functionality failed to turn on"
        # Wait until the board is connected to the cellular network
        while("+COPS: 0" in self.Send_AT_Command("AT+COPS?")):
            print("[-] waiting and retrying until board has cell connection")
            time.sleep(10)

        print("\n[+] Board is setup and ready to function\n")

    """
        This function will setup the PDP Context for the board to operate on the AT&T network
    """
    def Setup_PDP_Context(self):
        # reset the buffer to make sure we aren't getting weird residual values
        self.ser.reset_input_buffer()
        assert "OK" in self.Send_AT_Command("AT+UPSD=0,100,1"), "PDP Profile setup failed"
        assert "OK" in self.Send_AT_Command("AT+UPSD=0,0,2"), "PDP type configuration failed"
        assert "OK" in self.Send_AT_Command("AT+UPSDA=0,3"), "PSD profile activation failed"
        
        print("\n[+] PDP Context successfully setup\n")

    """********************************************************************
                MQTT FUNCTIONS TO INTERACT WITH A BROKER
    *********************************************************************"""

    """
        This function will establish an unsecure connection to an MQTT broker

        @param mqtt_server_name (string)
            denotes the url of the mqtt broker to connect to
    """
    def MQTT_Connect(self, mqtt_server_name: str):
        # run the command to setup the connection info
        assert "OK" in self.Send_AT_Command('AT+UMQTT=2,"'+ mqtt_server_name +'",1883'), "Connection info failed to set"
        # setup the secure connection to no TLS encryption which runs over port 1883
        assert "OK" in self.Send_AT_Command("AT+UMQTT=11,0,0"), "Failed to set MQTT secure option"
        # try to setup a connection to the MQTT server
        assert "+UUMQTTC: 1,1" in self.Send_AT_Command("AT+UMQTTC=1", True), "login failed"

        print("\n[+] Successfully connected to MQTT broker\n")

    """
        This function will logout from an established MQTT connection
    """
    def MQTT_Disconnect(self):
        assert "+UUMQTTC: 0,1" in self.Send_AT_Command("AT+UMQTTC=0", True), "logout failed"

        print("\n[+] Successfully disconnected from MQTT broker\n")

    """
        This function will send an AT command to subscribe to a topic

        @param topic (string)
            Denotes what topic to subscribe to from the MQTT broker
    """
    def MQTT_Subscribe(self, topic: str):
        assert '+UUMQTTC: 4,1,0,"{}"'.format(topic) in self.Send_AT_Command('AT+UMQTTC=4,0,"{}"'.format(topic), True), "Failed to Subscribe"
 
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
        assert "+UUMQTTC: 2,1" in self.Send_AT_Command('AT+UMQTTC=2,{},{},0,"{}","{}"'.format(qos,retain,topic,data), True), "Failed to Publish"

        print("\n[+] Successfully published "+ data +" to topic: "+ topic +"\n")

    """
        This function will read data received as a result of subscribing to a topic
    """
    def MQTT_Read_Data(self):
        assert "OK" in self.Send_AT_Command("AT+UMQTTC=6,0"), "Read Failed"

        print("\n[+] Successfully Read Data from MQTT Subscription\n")

    """********************************************************************
        THE FOLLOWING ARE TESTS TO VALIDATE THE FUNCTIONALITY OF THE BOARD
    *********************************************************************"""

    """
        This function will run all of the tests in the suite to verify everything

        @param mqtt_server_name (string)
            used in the MQTT_Login_Test function
    """
    def Run_All_Tests(self, mqtt_server_name: str):
        self.Basic_Up_Test()
        self.MQTT_Pub_Sub_Test(mqtt_server_name)

    """
        This is a basic initial test to make sure that the board is up and operational
    """
    def Basic_Up_Test(self):
        # reset the buffer to make sure we aren't getting weird residual values
        self.ser.reset_input_buffer()
        # Ensure that the board is at least responding and connected via serial
        assert "OK" in self.Send_AT_Command("AT"), "AT command failed"
        # Verify that the board is connected to the cellular network
        assert "+COPS: 0" not in self.Send_AT_Command("AT+COPS?"), "Board not connected to cell network"
        # Verify that the board has a PDP context setup to ping google
        assert "+UUPINGER: 17" not in self.Send_AT_Command('AT+UPING="www.google.com"', True), "PDP Context not properly setup"

        # this will only print if all of the above tests pass
        print("\n[+] Passed all Basic_Up_Test tests, board is functional\n")

    """
        Tests the basic MQTT login functionality to make sure the board can make a
        successful connection to the MQTT broker

        @param mqtt_server_name (string)
            Specifies the mqtt server to make the connection
    """
    def MQTT_Login_Test(self, mqtt_server_name: str):
        # reset the buffer to make sure we aren't getting weird residual values
        self.ser.reset_input_buffer()
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