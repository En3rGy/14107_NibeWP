# coding: UTF-8

# Copyright 2021 T. Paul</p>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.


import json
import socket
import threading
import urllib2


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class NibeWP_14107_14107(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "14107_NibeWP")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_S_GWIP=1
        self.PIN_I_N_GWPORTGET=2
        self.PIN_I_N_GWPORTSET=3
        self.PIN_I_N_HSPORT=4
        self.PIN_I_S_CMDSET=5
        self.PIN_I_S_CMDGET=6
        self.PIN_I_S_REG01=7
        self.PIN_I_S_REG02=8
        self.PIN_I_S_REG03=9
        self.PIN_I_S_REG04=10
        self.PIN_I_S_REG05=11
        self.PIN_I_S_REG06=12
        self.PIN_I_S_REG07=13
        self.PIN_I_S_REG08=14
        self.PIN_I_S_REG09=15
        self.PIN_I_S_REG10=16
        self.PIN_I_S_REG11=17
        self.PIN_I_S_REG12=18
        self.PIN_I_S_REG13=19
        self.PIN_I_S_REG14=20
        self.PIN_I_S_REG15=21
        self.PIN_I_S_REG16=22
        self.PIN_I_S_REG17=23
        self.PIN_I_S_REG18=24
        self.PIN_I_S_REG19=25
        self.PIN_I_S_REG20=26
        self.PIN_O_S_VALUES=1
        self.PIN_O_S_MODEL=2
        self.PIN_O_N_VER=3
        self.PIN_O_N_GETREG=4
        self.PIN_O_N_REG01=5
        self.PIN_O_N_REG02=6
        self.PIN_O_N_REG03=7
        self.PIN_O_N_REG04=8
        self.PIN_O_N_REG05=9
        self.PIN_O_N_REG06=10
        self.PIN_O_N_REG07=11
        self.PIN_O_N_REG08=12
        self.PIN_O_N_REG09=13
        self.PIN_O_N_REG10=14
        self.PIN_O_N_REG11=15
        self.PIN_O_N_REG12=16
        self.PIN_O_N_REG13=17
        self.PIN_O_N_REG14=18
        self.PIN_O_N_REG15=19
        self.PIN_O_N_REG16=20
        self.PIN_O_N_REG17=21
        self.PIN_O_N_REG18=22
        self.PIN_O_N_REG19=23
        self.PIN_O_N_REG20=24
        self.PIN_O_N_ALIVE=25
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    g_msg = 0
    g_register = {}
    g_out = {}
    g_out_sbc = {}

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

                if ("out" in self.g_register[reg]):
                    outPin = self.g_register[reg]["out"]

                    if (outPin != 0):
                        self.set_output_value_sbc(outPin, val)

            return True, res

        except Exception as e:
            self.DEBUG.add_message("ERROR parseRegister: " + str(e))
            return False, None


    def set_output_value_sbc(self, pin, val):
        if (pin in self.g_out_sbc):
            pass
        else:
            self.g_out_sbc[pin] = val
        
        if (self.g_out_sbc[pin] != val):
            self._set_output_value(pin, val)

        self.g_out_sbc[pin] = val


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
                self._set_output_value(self.PIN_O_N_ALIVE, 1)
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
            self.DEBUG.self.DEBUG.add_message("sendData: Sending write register")
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
