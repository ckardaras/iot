from SerialConnect import SerialConnect


"""
	Helper function for extracting and converting the hex data that gets returned
	from the CoAP server

	@param response (list(string))
		The response that comes back from reading the lines from the SerialConnect class

	@returns
		the hex converted string that resulted from the Coap request
"""
def extract_hex_data(response: list) -> str:
	hex_response = None
	for res in response:
		if "+UCOAPCD:" in res:
			hex_result = res.split(',')[2][1:-1]
			hex_response = bytearray.fromhex(hex_result).decode()
			break
	
	return hex_response

class CoapSaraR5:

	"""
	    Simple class constructor for the CoapConnect class

	    @param ser (SerialConnect)
	        A SerialConnect object passed in to utilize the functions in the SerialConnect
	        class for sending AT commands to the SARA R5 board

	    @param base_uri (string)
	    	The base uri info which will contain the server 
	"""
	def __init__(self, ser: SerialConnect, base_uri: str):
	    self.ser = ser
	    self.base_uri = base_uri

	"""
	    This will setup the proper CoAP configuration on the SARA-R5 board
	"""
	def Coap_Configure(self):
		# set verbose error result codes
	    assert "OK" in self.ser.Send_AT_Command("AT+CMEE=2"), "Setting verbose error result codes failed"
	    # set current profile as valid
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=4,1"), "Setting current profile as valid failed"
	    # enables automatic recognition of URI_HOST, URI_PORT, URI_PATH, and URI_QUERY directly from the URI
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,0,1"), "Enabling automatic recognition of URI_HOST failed"
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,1,1"), "Enabling automatic recognition of URI_PORT failed"
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,2,1"), "Enabling automatic recognition of URI_PATH failed"
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,3,1"), "Enabling automatic recognition of URI_QUERY failed"
	    # Sets the content format for the PUT/POST requests as "Plain/Text"
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,4,1"), "Setting content format for PUT/POST as plain text failed"

	    # Store the current profile to be stored as profile number 0
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=6,0"), "Storing current CoAP profile failed"
	    # Restore the profile number 0 as the current profile
	    assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=5,0"), "Restoring profile 0 for CoAP failed"

	    print("\n[+] Successfully configured the board to use the CoAP protocol\n")

	"""
		This function will make a GET request to the CoAP server specified within the server_uri arg

		@param server_uri (string)
			The uri to be used in the coap connection to make a GET request

		@param use_con (bool)
			specifies whether to use CONfirmable (true) or NON confirmable (false) messages
	"""
	def Coap_GET(self, resource_uri: str, use_con: bool = False):
		con = 0
		if use_con:
			con = 1
		# Set the URI to be used in the GET request
		assert "OK" in self.ser.Send_AT_Command('AT+UCOAP=1,"{}"'.format(self.base_uri+resource_uri)), "Setting URI failed"
		# set whether or not to use confirmable message
		assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,5,{}".format(con)), "Setting confirmable option failed"
		# Make the GET request to the CoAP server
		response = self.ser.Send_AT_Command("AT+UCOAPC=1", True)
		assert "+UCOAPCR: 1,1" in response, "Coap GET request failed, check connection and coap server"
		print("\n[+] GET Data Response: {}\n".format(extract_hex_data(response)))

	"""
		This function will make a PUT request to the CoAP server
		A PUT request will create/replace the resource in its entirety at the URI

		@param server_uri (string)
			The uri to be used in the coap connection to make a GET request

		@param data (string)
			ASCII data to send to the CoAP server, this will get hex encoded before sending

		@param use_con (bool)
			specifies whether to use CONfirmable (true) or NON confirmable (false) messages
	"""
	def Coap_PUT(self, resource_uri: str, data: str, use_con: bool = False):
		con = 0
		if use_con:
			con = 1
		hex_data = ""
		for char in data:
			hex_data += str(hex(ord(char))[2:]).upper()
		# Set the URI to be used in the GET request
		assert "OK" in self.ser.Send_AT_Command('AT+UCOAP=1,"{}"'.format(self.base_uri+resource_uri)), "Setting URI failed"
		# set whether or not to use confirmable message
		assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,5,{}".format(con)), "Setting confirmable option failed"
		# Make the PUT request to the CoAP server
		response = self.ser.Send_AT_Command('AT+UCOAPC=3,"{}",0'.format(hex_data), True)
		assert "+UCOAPCR: 3,1" in response, "Coap PUT request failed, check connection and coap server"
		print("\n[+] PUT Response: {}\n".format(extract_hex_data(response)))

	"""
		This function will make a POST request to the CoAP server
		A POST request will create a child resource at the uri

		@param server_uri (string)
			The uri to be used in the coap connection to make a GET request

		@param data (string)
			ASCII data to send to the CoAP server, this will get hex encoded before sending

		@param use_con (bool)
			specifies whether to use CONfirmable (true) or NON confirmable (false) messages
	"""
	def Coap_POST(self, resource_uri: str, data: str, use_con: bool = False):
		con = 0
		if use_con:
			con = 1
		hex_data = ""
		for char in data:
			hex_data += str(hex(ord(char))[2:]).upper()
		# Set the URI to be used in the GET request
		assert "OK" in self.ser.Send_AT_Command('AT+UCOAP=1,"{}"'.format(self.base_uri+resource_uri)), "Setting URI failed"
		# set whether or not to use confirmable message
		assert "OK" in self.ser.Send_AT_Command("AT+UCOAP=2,5,{}".format(con)), "Setting confirmable option failed"
		# Make the POST request to the CoAP server
		response = self.ser.Send_AT_Command('AT+UCOAPC=4,"{}",0'.format(hex_data), True)
		assert "+UCOAPCR: 4,1" in response, "Coap PUT request failed, check connection and coap server"
		print("\n[+] PUT Response: {}\n".format(extract_hex_data(response)))