# coding: UTF-8

import unittest



import json
import socket
import threading
import urllib2

import time


class NibeWP_14107_14107():
    

    def _set_output_value(self, pin, value):
        print("### Out \tPin " + str(pin) + ", Value: " + str(value))
        return ("### Out \tPin " + str(pin) + ", Value: " + str(value))

    def _get_input_value(self, pin):
        if(pin==self.PIN_I_N_HSPORT):
            return 9999
        elif(pin==self.PIN_I_N_GWPORTGET):
            return 9999
        elif(pin==self.PIN_I_N_GWPORTSET):
            return 10000
        elif(pin == self.PIN_I_S_GWIP):
            return "192.168.143.18"
        else:
            return "0"


################################################
    class DebugHelper():
        def set_value(self, p_sCap, p_sText):
            print ("DEBUG value\t" + str(p_sCap) + ": " + str(p_sText))
            
        def add_message(self, p_sMsg):
            print ("Debug Msg\t" + str(p_sMsg))

    DEBUG = DebugHelper()

    class FrameworkHelper():
        def get_homeserver_private_ip(self):
            return "192.168.143.30"

        def create_debug_section(self):
            pass

    FRAMEWORK = FrameworkHelper()

############################################

    #hsl20_3.BaseModule.__init__(self, homeserver_context, "14107_NibeWP")
    #self.FRAMEWORK = self._get_framework()
    #self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
    PIN_I_S_GWIP=1
    PIN_I_N_GWPORTGET=2
    PIN_I_N_GWPORTSET=3
    PIN_I_N_HSPORT=4
    PIN_I_S_CMDSET=5
    PIN_I_S_CMDGET=6
    PIN_I_S_REG01=7
    PIN_I_S_REG02=8
    PIN_I_S_REG03=9
    PIN_I_S_REG04=10
    PIN_I_S_REG05=11
    PIN_I_S_REG06=12
    PIN_I_S_REG07=13
    PIN_I_S_REG08=14
    PIN_I_S_REG09=15
    PIN_I_S_REG10=16
    PIN_I_S_REG11=17
    PIN_I_S_REG12=18
    PIN_I_S_REG13=19
    PIN_I_S_REG14=20
    PIN_I_S_REG15=21
    PIN_I_S_REG16=22
    PIN_I_S_REG17=23
    PIN_I_S_REG18=24
    PIN_I_S_REG19=25
    PIN_I_S_REG20=26
    PIN_O_S_VALUES=1
    PIN_O_S_MODEL=2
    PIN_O_N_VER=3
    PIN_O_N_GETREG=4
    PIN_O_N_REG01=5
    PIN_O_N_REG02=6
    PIN_O_N_REG03=7
    PIN_O_N_REG04=8
    PIN_O_N_REG05=9
    PIN_O_N_REG06=10
    PIN_O_N_REG07=11
    PIN_O_N_REG08=12
    PIN_O_N_REG09=13
    PIN_O_N_REG10=14
    PIN_O_N_REG11=15
    PIN_O_N_REG12=16
    PIN_O_N_REG13=17
    PIN_O_N_REG14=18
    PIN_O_N_REG15=19
    PIN_O_N_REG16=20
    PIN_O_N_REG17=21
    PIN_O_N_REG18=22
    PIN_O_N_REG19=23
    PIN_O_N_REG20=24
    #self.FRAMEWORK._run_in_context_thread(self.on_init)

############################################

    g_msg = 0
    g_register = {}
    g_out = {}

    g_bigendian = False

    # Re-ordering / inversing the byte order
    def shiftBytes(self, msg):
        res = []
        for x in msg[::-1]:
            res.append(x)
        return res


    # Main server loop, listening for incomming messages
    def listen(self):
        ## declare our serverSocket upon which
        ## we will be listening for UDP messages
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ## One difference is that we will have to bind our declared IP address
        ## and port number to our newly declared serverSock
        UDP_IP_ADDRESS = self.FRAMEWORK.get_homeserver_private_ip()
        UDP_PORT_NO = self._get_input_value(self.PIN_I_N_HSPORT)

        self.DEBUG.add_message("listen: Start listening for incomming msgs at" 
                               + str(UDP_IP_ADDRESS) + ":" + str(UDP_PORT_NO))

        try:
            serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
            data = ""

            while True:
                    data = data + serverSock.recv(1024)
                    msg, ret = self.chkMsg(data)
                    if (ret == True):
                        self.parseData(msg)
                        data = ""
                    else:
                        if (msg == None):
                            data = ""

        except Exception as e:
            self.DEBUG.add_message("ERROR listen: " + str(e) + " (abort)")
        finally:
            serverSock.close()


    # Reads the Modbus Manager export file which is provided to the HS, 
    # see HS help for "hsupload"
    def readExport(self):
        try:
            target_url = 'http://127.0.0.1:65000/logic/14107/export.csv'
            datafile = urllib2.urlopen(target_url)
            self.parseExport(datafile)
        except Exception as e:
            self.DEBUG.add_message("ERROR readExport: " + str(e))


    # Parses the Modbus Manager export file and stores the content to self.g_register
    def parseExport(self, datafile):
        #print("Running parseExport")
        self.g_register = {}
        i = 0

        for row in datafile:
            row = row.replace('"', '')
            data = row.split(';')
            if (len(data) < 10):
                continue

            # Title;Info;ID;Unit;Size;Factor;Min;Max;Default;Mode
            # 0     1    2  3    4    5      6   7   8       9
            try:
                self.g_register[int(data[2])] = {"Title": data[0], "Size": data[4], "Factor": float(data[5]), "Mode": data[9]}
                i = i + 1
            except Exception as e:
                self.DEBUG.add_message("parseExport: " + str(e) + " with '" + str(data) + "'")

        self.DEBUG.add_message("parseExport: Read Modbus Manager file with " + str(i) + " entries.")


    # Checks the integrity of a received message
    # Example:
    # 5c 00 20 6d 0e 01 24 18 46 31 31 34 35 2d 31 30 20 44 45 34
    #                |---------- Bytes vor len count --------| 
    #    |------------ Bytes for checksum calculation -------|
    def chkMsg(self, msg):
        try:
            #print("Running chkMsg")
            inMsg = bytearray(msg)
            outMsg = []

            # check for start byte
            for i in range(len(inMsg)):
                if (inMsg[i] == 0x5c) and (i < len(inMsg) - 1):
                    outMsg = inMsg[i+1:]
                    break

            # check if msg is complete
            if(len(outMsg) < 4):
                return outMsg, False

            msgLen = int(outMsg[3])
            cntLen = len(outMsg[4:-1])

            if (cntLen < msgLen):
                return outMsg, False

            outMsg = outMsg[:4 + msgLen + 1]

            # check checksum
            msgChkSm = outMsg[msgLen + 4]
            chksm = self.calcChkSm(outMsg[:-1])
            if (chksm != msgChkSm):
                self.DEBUG.add_message("chkMsg: Checksum error, msg was " + self.printByteArray(inMsg))
                self.DEBUG.set_value("Last failed msg", self.printByteArray(inMsg))
                return None, False

            return outMsg, True

        except Exception as e:
            self.DEBUG.add_message("ERROR chkMsg: " + str(e))


    # Calculates XOR checksum
    def calcChkSm(self, msg):
        chkSm = 0x00
        for x in (msg):
            chkSm = chkSm ^ x
        return chkSm

    # Parses the data block of an incomming message
    def parseRegister(self, data, cmd6a = False):
        try:
            reg = 0
            res = {}
            i = 0
            while i < len(data):

                # register
                reg = self.hex2int(data[i: i + 2])
                #self.DEBUG.add_message("Register received: " + str(self.printByteArray(data[i: i + 2]) + " ~ " + str(reg)))

                # reg = 0xffff -> skip and following data
                if (reg == 65535 or reg == 0):
                    #print("- Next register 0xffff or 0x0, skipping 4 byte")
                    i = i + 4
                    continue
    
                i = i + 2
    
                if reg not in self.g_register:
                    self.DEBUG.add_message("Register " + str(reg) + " not known. Abort parse.")
                    return False, res
    
                # value
                size = self.g_register[reg]["Size"]
                if(cmd6a == True):
                    size = size[0] + "32"

                factor = self.g_register[reg]["Factor"]

                if (size == "s8") or (size == "u8"):
                    if (data[i+1] & 0x80 == 0x80) and (size == "s8"):
                        val = self.complement2(data[i:i + 2]) / factor
                    else:
                        val = self.hex2int(data[i:i + 2]) / factor
                    i = i + 2

                elif (size == "s16") or (size == "u16"):
                    if (data[i+1] & 0x80 == 0x80) and (size == "s16"):
                        val = self.complement2(data[i:i + 2]) / factor
                    else:
                        val = self.hex2int(data[i:i + 2]) / factor
                    i = i + 2
    
                elif (size == "s32") or (size == "u32"):
                    #check next register
                    reg_next = self.hex2int(data[i + 2:i + 4])
    
                    if (reg_next - reg == 1):
                        #print("- next register is split register")
                        # x32 uses next register for full value
                        val1 = data[i:i + 2]
                        i = i + 4
    
                        val2 = data[i:i + 2]
                        data32 = val1.append(val2)
    
                        val = self.hex2int(data32) / factor
                        #print("- Value: " + str(val))
                        i = i + 2
                    else:
                        #print("- next register is 0xffff, skip")
                        val = self.hex2int(data[i:i + 2]) / factor
                        #print("- Value: " + str(val))
                        i = i + 6
    
                else:
                    self.DEBUG.add_message("ERROR parseRegister: size of value unknown.")
    
                # write value
                res[str(reg)]= {}
                res[str(reg)]["Title"] = self.g_register[reg]["Title"]
                res[str(reg)]["value"] = val
                #self.DEBUG.set_value(str(reg), str(val))

                if ("out" in self.g_register[reg]):
                    outPin = self.g_register[reg]["out"]
                    if (outPin != 0):
                        self._set_output_value(outPin, val)

            return True, res

        except Exception as e:
            self.DEBUG.add_message("ERROR parseRegister: " + str(e))
            return False, None


    def parseData(self, msg):
        try:
            #sender = msg[0]
            #addr = msg[1]
            cmd = msg[2]
            #length = msg[3]
            data = msg[4:-2]
            #crc = msg[-1]
            
            self.DEBUG.set_value("last raw msg " + str(hex(cmd)), 
                           str(hex(0x5c)) + " " + self.printByteArray(msg))

            # remove escaping of startbyte 0x5c
            i = 0
            while i < len(data) - 1:
                if (data[i] == 0x5c) and (data[i + 1] == 0x5c):
                    data.pop(i)
                    print("- Removed 0x5c escaping")
                i = i + 1

            # 20 value register msg
            if (cmd == 0x68):
                ok, ret = self.parseRegister(data)
                if (ok == False):
                    self.DEBUG.add_message("Error reading msg " + str(hex(0x5c)) + " " + self.printByteArray(msg))
                    return None
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
                return jsn
    
            # response for single register request
            elif(cmd == 0x6a):
                # @todo value always 32bit!
                ok, ret = self.parseRegister(data, True)
                if (ok == False):
                    self.DEBUG.add_message("Error reading msg " + str(hex(0x5c)) + " " + self.printByteArray(msg))
                    return None
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
                return jsn
    
            # ignore, seems to be a confirmation of an executed command
            # 5c00206c01014c
            elif (cmd == 0x6c): # and $msg eq "5c00206c01014c") {
                pass
            #print("- Msg 0x6c not implemented")

            # readingsBulkUpdate
            elif (cmd == 0x6d): #and substr($msg, 10, 2*$length) =~ m/(.{2})(.{4})(.*)/) {
                #ver = self.hex2int(data[0:3])
                ver = self.hex2int(data[1:3])
                prod = data[3:]
                self._set_output_value(self.PIN_O_N_VER, ver)
                self._set_output_value(self.PIN_O_S_MODEL, prod)
                return str(str(prod) + " / " + str(ver))

            # 0x5c 0x0 0x20 0xee 0x0 0xce
            elif (cmd == 0xee):
                pass
                #print("- Msg 0xee not implemented")

            else:
                pass
                #print("- unknown msg")

        except Exception as e:
            self.DEBUG.add_message("ERROR parseData: " + str(e) + " with msg " + self.printByteArray(msg))


    def getHexValue(self, value, size):
        if (size=="s8" or size=="u8"):
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8
            val = chr(val2) + chr(val1)

        elif (size=="s16" or size=="u16"):
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8
            val = chr(val2) + chr(val1)

        elif (size=="s32" or size=="u32"):
            val1 = value & 0x000000FF
            val2 = value & 0x0000FF00
            val3 = value & 0x00FF0000
            val4 = value & 0xFF000000
            val2 = val2 >> 8
            val3 = val3 >> 16
            val4 = val4 >> 24

            val = chr(val4) + chr(val3) + chr(val2) + chr(val1)

        return val

    def sendData(self, port, data):
        ipaddr = str(self._get_input_value(self.PIN_I_S_GWIP))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # connect the socket, think of it as connecting the cable to the address location
        s.connect((ipaddr, port))
        self.DEBUG.set_value("last send", "Sending " + self.printByteArray(bytearray(data)) + "to " + ipaddr + ":" + str(port))
        s.send(data)
        s.close()


    def readRegister(self, register):
        try:    
            msg = "\xc0\x69\x02"
            reg = self.getHexValue(register, "u8")
            msg = msg + reg
            chksm = self.calcChkSm(bytearray(msg))
            msg = msg + chr(chksm)

            port = int(self._get_input_value(self.PIN_I_N_GWPORTGET))
            self.sendData(port, msg)
        except Exception as e:
            self.DEBUG.add_message("ERROR readRegister: " + str(e))


    def writeRegister(self, register, value):
        try:
            msg = "\xc0\x6b\x06"

            reg = self.getHexValue(register, "u8")
            msg = msg + reg

            mode = self.g_register[register]["Mode"]
            if ("W" not in mode) and ("w" not in mode):
                self.DEBUG.add_message("writeRegister: Register " + str(register) + " is read only. Aborting send.")
                return
    
            factor = self.g_register[register]["Factor"]
            value = int(value * factor)
            #size = self.g_register[register]["Size"]
            value = self.getHexValue(value, "u32")
            msg = msg + value

            chksm = self.calcChkSm(bytearray(msg))
            msg = msg + chr(chksm)

            port = int(self._get_input_value(self.PIN_I_N_GWPORTSET))
            self.sendData(port, msg)
        except Exception as e:
            self.DEBUG.add_message("ERROR writeRegister: " + str(e))


    def printByteArray(self, data):
        s = ""
        for i in range(len(data)):
            s = s + " " + str(hex(data[i]))
        s = s[1:]
        return s


    def hex2int(self, msg):
        if (self.g_bigendian == False):
            msg = self.shiftBytes(msg)

        val = 0
        val = val | msg[0]
        for byte in msg[1:]:
            val = val << 8
            val = val | byte

        return int(val)


    # data shall not yet be re-ordered (use orig byte order)
    def complement2(self, data):
        for i in range(len(data)):
            data[i] ^= 0xFF

        val = self.hex2int(data)
        val = val + 1
        return -val


    def testEndian(self):
        data = bytearray("\x80\x00")
        val = 0
        val = val | data[0]
        for byte in data[1:]:
            val = val << 8
            val = val | byte

        self.DEBUG.add_message(self.printByteArray(data) + " -> " + str(val) + 
                             "(32768 little endian, 8 big endian)")


    def initExportCsv(self):
        self.readExport()

        for i in range(self.PIN_I_S_REG20 - self.PIN_I_S_REG01):
            outId = self.PIN_O_N_REG01 + i
            reg = self._get_input_value(self.PIN_I_S_REG01 + i)
            if (reg == 0):
                continue
            if (reg in self.g_register):
                self.g_register[reg]["out"] = outId
            else:
                self.DEBUG.add_message("initExportCsv: Register " + str(reg) + " at EW" + 
                                       str(self.PIN_I_S_REG01 + i) + 
                                       " not defined in Mobus Manager Export." )


    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.testEndian()
        self.initExportCsv()
        x = threading.Thread(target=self.listen)
        x.start()


    def on_input_value(self, index, value):
        if (index == self.PIN_I_S_CMDGET):
            self.readRegister(value)

        elif (index == self.PIN_I_S_CMDSET):
            val = value.split(':')
            register = int(val[0])
            val = float(val[1])
            self.writeRegister(register, val)

        elif (index >= self.PIN_I_S_REG01):
            outId = index - self.PIN_I_S_REG01 + self.PIN_O_N_REG01
            self.g_register[value]["out"] = outId
            oldReg = 0

            if (outId in self.g_out):
                oldReg = self.g_out[outId]
                self.g_register[oldReg]["out"] = 0
                self.g_out[outId] = value


############################################


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def cmpBytearray(self, data1, data2):
        if len(data1) != len(data2):
            return False
    
        for i in range(len(data1)):
            if data1[i] != data2[i]:
                return False
        
        return True

    def test_cmpBytearray(self):
        tst = NibeWP_14107_14107()
        data1 = tst.shiftBytes(bytearray("\x9c\x44\x56"))
        data2 = bytearray("\x56\x44\x9c")
        self.assertTrue(self.cmpBytearray(data1, data2))

    def test_hex2int_bigEndian(self):
        tst = NibeWP_14107_14107()
        tst.g_bigendian = True
        val1 = tst.hex2int(bytearray("\x9c\x44\x56"))
        self.assertEqual(val1, 10241110)

    def test_hex2int_littleEndian(self):
        tst = NibeWP_14107_14107()
        tst.g_bigendian = False
        val1 = tst.hex2int(bytearray("\x9c\x44\x56"))
        self.assertEqual(val1, 5653660)

    def test_complement2(self):
        tst = NibeWP_14107_14107()
        tst.g_bigendian = False
        data1 = bytearray("\x76\x85\x81")
        val1 = tst.complement2(data1)
        self.assertEqual(val1, -8288906)

    def test_printByteArray(self):
        tst = NibeWP_14107_14107()
        data1 = bytearray("\xab\xcd\xef")
        res = tst.printByteArray(data1)
        self.assertEqual(res, "0xab 0xcd 0xef")

    def test_getHexValue(self):
        tst = NibeWP_14107_14107()
        data1 = tst.getHexValue(156, 'u8')
        self.assertEqual(data1, "\x00\x9c")
        data1 = tst.getHexValue(40004, 'u16')
        self.assertEqual(data1, "\x9c\x44")
        data1 = tst.getHexValue(2621733731, 'u32')
        self.assertEqual(data1, "\x9c\x44\x7b\x63")

    def test_parseData_x68(self):
        tst = NibeWP_14107_14107()
        tst.g_bigendian = False
        #msg1 = "\x5c\x00\x20\x68\x50\x44\x9c\xca\xff\x48\x9c\xab\x01\x4c\x9c\x3c\x01\x4e\x9c\x8f\x01\x87\x9c\x37\x01\x4f\x9c\x65\x00\x50\x9c\x38\x00\x88\x9c\x94\x00\xc9\xaf\x00\x00\x5b\xa4\x00\x80\xff\xff\x00\x00\x33\xa4\x00\x00\xff\xff\x00\x00\xa3\xa9\x3c\x00\xab\xbb\x00\x00\xc1\xb7\x04\x00\x31\xa1\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\x9f"
        msg1 = "\x00\x20\x68\x50\x44\x9c\xca\xff\x48\x9c\xab\x01\x4c\x9c\x3c\x01\x4e\x9c\x8f\x01\x87\x9c\x37\x01\x4f\x9c\x65\x00\x50\x9c\x38\x00\x88\x9c\x94\x00\xc9\xaf\x00\x00\x5b\xa4\x00\x80\xff\xff\x00\x00\x33\xa4\x00\x00\xff\xff\x00\x00\xa3\xa9\x3c\x00\xab\xbb\x00\x00\xc1\xb7\x04\x00\x31\xa1\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\x9f"
        res1 = '{"43427": {"value": 60.0, "Title": "Compressor State EP14"}, "41265": {"value": 0.0, "Title": "Smart Home Mode"}, "40072": {"value": 14.8, "Title": "BF1 EP14 Flow"}, "45001": {"value": 0.0, "Title": "Alarm"}, "47041": {"value": 4.0, "Title": "Hot water comfort mode"}, "42035": {"value": 0.0, "Title": "AA23-BE5 EME20 Total Power"}, "40012": {"value": 31.6, "Title": "EB100-EP14-BT3 Return temp"}, "40016": {"value": 5.6, "Title": "EB100-EP14-BT11 Brine Out Temp"}, "40004": {"value": -5.4, "Title": "BT1 Outdoor Temperature"}, "40014": {"value": 39.9, "Title": "BT6 HW Load"}, "40015": {"value": 10.1, "Title": "EB100-EP14-BT10 Brine In Temp"}, "48043": {"value": 0.0, "Title": "Holiday - Activated"}, "40008": {"value": 42.7, "Title": "BT2 Supply temp S1"}, "42075": {"value": 3276.8, "Title": "AA23-BE5 EME20 Total Energy"}, "40071": {"value": 31.1, "Title": "BT25 Ext. Supply"}}'        
        
        datafile = open("export.csv", 'r')
        tst.parseExport(datafile)
        ret1 = tst.parseData(bytearray(msg1))
        self.assertEqual(res1, ret1)

    def test_parseData_x6a(self):
        tst = NibeWP_14107_14107()
        tst.g_bigendian = False
        #msg1 = "\x5c\x00\x20\x6a\x06\xab\xbb\x00\x00\x8d\x10\xc1"
        msg1 = "\x00\x20\x6a\x06\xab\xbb\x00\x00\x8d\x10\xc1"
        res1 = '{"48043": {"value": 0.0, "Title": "Holiday - Activated"}}'

        datafile = open("export.csv", 'r')
        tst.parseExport(datafile)
        ret1 = tst.parseData(bytearray(msg1))
        self.assertEqual(res1, ret1)



if __name__ == '__main__':
    unittest.main()



