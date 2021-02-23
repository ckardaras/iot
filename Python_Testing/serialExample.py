# quick and dirty happy path AT command issuer
import serial
import time

def ATCmdResp(cmd,resp):
    if len(cmd) > 0:
        ok = False
        retryCnt = 0
        print ('Writing: ' + str(cmd))
        while not ok and retryCnt < 3:
            if type(cmd) == str:
                ser.write(str.encode(cmd))      # send the cmd
            else:
                ser.write(cmd)      # send the cmd
            ok = readBuf(resp)  # read the response. readBuf assumes there will be a response.
            if ok:
                return
            retryCnt += 1
            time.sleep(1)
            
def readBuf(resp):
    x = ser.readlines()
    
    ok = False
    for ln in x:
        ln=ln.decode('utf-8').strip()
        if len(ln) > 0:
            if resp in ln:
                ok = True
                print(ln)
            else:
                print(ln)
        else:
            print('No resp recvd')
            
    return ok

# simple program to test writing and reading AT commands to the u-blox modem
ser = serial.Serial('COM6', 115200, timeout=1)
#ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ATCmdResp('AT\r', 'OK')

ATCmdResp('ATE0\r', 'OK')

ATCmdResp('AT+CSQ\r', 'OK')

print( 'Trying a byte array')

data = bytearray([65,84,13])
ATCmdResp(data, 'OK')     # send "AT\r" as a byte array

ATCmdResp('AT+CSQ\r','OK')

ATCmdResp('ATI9\r','OK')

ATCmdResp('AT+UPSD=0,100,1\r','OK')
ATCmdResp('AT+UPSD=0,0,2\r','OK')
ATCmdResp('AT+UPSDA=0,3\r','OK')
ATCmdResp('AT+UPING="www.google.com"\r','')

ATCmdResp('AT+USOCR=6\r','OK')
ATCmdResp('AT+UDNSRN=0,"echo.u-blox.com"\r', 'OK')
ATCmdResp('AT+USOCO=0,"195.34.89.241",7\r','OK') 
time.sleep(2)
ATCmdResp('AT+USORD=0,32\r','OK') 
ATCmdResp('AT+USOWR=0,4,"Test"\r','OK') 
time.sleep(2)
ATCmdResp('AT+USORD=0,4\r','OK') 
ATCmdResp('AT+USOCL=0\r','OK')

ser.flush()
ser.close()
