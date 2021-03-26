
import sys
import os
import json

print("Payload reader")
print("cwd = {}".format(os.getcwd()))

if len(sys.argv) > 1:
    fn = sys.argv[1]
else:
    print ("No filename provided.")
    exit()
    

with open(fn,'r') as payloadFile:
    payloadJSON = payloadFile.read()

obj = json.loads(payloadJSON)

print(type(obj))


# iterate the payloads array
for payload in obj['payloads']['payload']:
    # show the payload description
    print(payload['description'])
    # iterate through the events in the payload
    for event in payload['events']:
        print(event)
        # indicate the event class
        if 'data' in event:
            print("Found event with data")
            if isinstance(event['data'], dict):
                print('\tFound location event')
