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
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    g_msg = 0
    g_register = {}
    g_out = {}

    # HS und Modbus arbeiten mit bigendian, Windows mit littleendian
    g_bigendian = True

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

        try:
            
            serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
            data = ""

            while True:
                data = data + serverSock.recv(1024)
                msg, ret = self.chkMsg(data)
                if ret:
                    self.parseData(msg)
                    data = ""
        except Exception as e:
            self.DEBUG.add_message("14107 listen: " + str(e))

        finally:
            serverSock.close()


    # Reads the Modbus Manager export file which is provided to the HS, 
    # see HS help for "hsupload"
    def readExport(self):
        try:
            target_url = 'http://127.0.0.1:65000/logic/14107/export.csv'
            datafile = urllib2.urlopen(target_url)
            self.DEBUG.add_message("14107 readExport: Load Modbus Manager file with " + str(len(datafile.readlines())) + " lines.")
            self.parseExport(datafile)
        except Exception as e:
            self.DEBUG.add_message("ERROR 14107 readExport: " + str(e))


    # Parses the Modbus Manager export file and stores the content to self.g_register
    def parseExport(self, datafile):
        #print("Running parseExport")
        self.g_register = {}

        for row in datafile:
            row = row.replace('"', '')
            data = row.split(';')
            if (len(data) < 10):
                continue

            # Title;Info;ID;Unit;Size;Factor;Min;Max;Default;Mode
            # 0     1    2  3    4    5      6   7   8       9
            try:
                self.g_register[int(data[2])] = {"Title": data[0], "Size": data[4], "Factor": float(data[5]), "Mode": data[9]}
            except Exception as e:
                self.DEBUG.add_message("14107 parseExport: " + str(e) + " with '" + str(data) + "'")

    # Checks the integrity of a received message
    def chkMsg(self, msg):
        #print("Running chkMsg")
        inMsg = bytearray(msg)
        outMsg = []

        #print("- " + self.printHex(msg))

        for i in range(len(inMsg)):
            if (inMsg[i] == 0x5c) and (i < len(inMsg) - 1):
                outMsg = inMsg[i+1:]
                break

        if(len(outMsg) < 4):
            self.DEBUG.add_message("chkMsg: Msg too short")
            return inMsg, False

        msgLen = int(outMsg[3])
        cntLen = len(outMsg[4:-1])

        if (cntLen < msgLen):
            self.DEBUG.add_message("chkMsg: Length error")
            return inMsg, False

        msgChkSm = outMsg[msgLen + 4]
        chksm = self.calcChkSm(outMsg[:-1])
        if (chksm != msgChkSm):
            self.DEBUG.add_message("chkMsg: Checksum error")
            return inMsg, False

        return outMsg, True


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
                self.DEBUG.set_value("Last register received", reg)
    
                # reg = 0xffff -> skip and following data
                if (reg == 65535 or reg == 0):
                    #print("- Next register 0xffff or 0x0, skipping 4 byte")
                    i = i + 4
                    continue
    
                i = i + 2
    
                if reg not in self.g_register:
                    self.DEBUG.add_message("Register not known. Abort parse.")
                    continue
    
                # value
                size = self.g_register[reg]["Size"]
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
                self.DEBUG.set_value(str(reg), str(val))

                if ("out" in self.g_register[reg]):
                    outPin = self.g_register[reg]["out"]
                    if (outPin != 0):
                        self._set_output_value(outPin, val)

            return res

        except Exception as e:
            self.DEBUG.add_message("ERROR 14107 parseRegister: " + str(e))


    def parseData(self, msg):
        try:
            #print("Running parseData")
    
            #sender = msg[0]
            #addr = msg[1]
            cmd = msg[2]
            #length = msg[3]
            data = msg[4:-2]
            #crc = msg[-1]
            
            self.DEBUG.set_value("14107 raw msg " + str(hex(cmd)), 
                           str(hex(0x5c)) + self.printByteArray(msg))

            # remove escaping of startbyte 0x5c
            i = 0
            while i < len(data) - 1:
                if (data[i] == 0x5c) and (data[i + 1] == 0x5c):
                    data.pop(i)
                    print("- Removed 0x5c escaping")
                i = i + 1

            # 20 value register msg
            if (cmd == 0x68):
                ret = self.parseRegister(data)
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
    
            # response for single register request
            elif(cmd == 0x6a):
                # @todo value always 32bit!
                ret = self.parseRegister(data)
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
    
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

            # 0x5c 0x0 0x20 0xee 0x0 0xce
            elif (cmd == 0xee):
                pass
                #print("- Msg 0xee not implemented")

            else:
                pass
                #print("- unknown msg")

        except Exception as e:
            self.DEBUG.add_message("ERROR 14107 parseData: " + str(e))


    def printHex(self, data):
        byte = bytearray(data)
        s = ""
        for i in byte:
            s = s + str(hex(i)) + " "
        return s


    def getHexValue(self, value, size):
        if (size=="s8" or size=="u8"):
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8
            val = chr(val1) + chr(val2)

        elif (size=="s16" or size=="u16"):
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8
            val = chr(val1) + chr(val2)

        elif (size=="s32" or size=="u32"):
            val1 = value & 0x000000FF
            val2 = value & 0x0000FF00
            val3 = value & 0x00FF0000
            val4 = value & 0xFF000000
            val2 = val2 >> 8
            val3 = val3 >> 16
            val4 = val4 >> 32

            val = chr(val1) + chr(val2) + chr(val3) + chr(val4)

        return val

    def sendData(self, port, data):
        ipaddr = str(self._get_input_value(self.PIN_I_S_GWIP))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # connect the socket, think of it as connecting the cable to the address location
        s.connect((ipaddr, port))
        self.DEBUG.set_value("14107 last send", "Sending " + self.printHex(data) + "to " + ipaddr + ":" + str(port))
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
            self.DEBUG.add_message("ERROR 14107 readRegister: " + str(e))


    def writeRegister(self, register, value):
        try:
            msg = "\xc0\x6b\x06"

            reg = self.getHexValue(register, "u8")
            msg = msg + reg

            mode = self.g_register[register]["Mode"]
            if ("W" not in mode) and ("w" not in mode):
                self.DEBUG.add_message("14107 writeRegister: Register " + str(register) + " is read only. Aborting send.")
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
            self.DEBUG.add_message("14107 writeRegister: " + str(e))


    def printByteArray(self, data):
        s = ""
        for i in range(len(data)):
            s = s + " " + str(hex(data[i]))
        return s


    def hex2int(self, msg):
        if (not self.g_bigendian):
            msg = self.shiftBytes(msg)

        val = 0
        self.DEBUG.set_value("hex2int input", self.printByteArray(msg))
        val = val | msg[-1]
        msg = msg[0:-1]
        for byte in msg:
            #print(hex(byte))
            val = val << 8
            val = val | byte

        self.DEBUG.set_value("hex2int output", int(val))

        return int(val)


    # data shall not yet be re-ordered (use orig byte order)
    def complement2(self, data):
        for i in range(len(data)):
            data[i] ^= 0xFF

        res = []
        for x in data[::-1]:
            res.append(x)

        val = self.hex2int(res)
        val = val + 1
        return -val


    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.DEBUG.set_value(self.printByteArray(bytearray("\x9c\x44")), self.hex2int(bytearray("\x9c\x44")))
        self.readExport()

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
