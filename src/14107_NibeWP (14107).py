# coding: UTF-8

import json
import socket
import threading

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
        self.PIN_O_S_VALUES=1
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    g_msg = 0
    g_register = {}


    def listen(self):
        ## declare our serverSocket upon which
        ## we will be listening for UDP messages
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ## One difference is that we will have to bind our declared IP address
        ## and port number to our newly declared serverSock
        UDP_IP_ADDRESS = self.FRAMEWORK.get_homeserver_private_ip()
        UDP_PORT_NO = self._get_input_value(self.PIN_I_N_HSPORT)
        serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

        print("Waiting for data")
        data = ""
        while True:
            data = data + serverSock.recv(1024)
            msg, ret = self.chkMsg(data)
            if ret:
                pass # process msg

        serverSock.close()


    def readExport(self):
        # Daten-Ablage in einem 'hsupload'-Unterverzeichnis
        
        # Im Unterverzeichnis _logic des Ordners hsupload können Dateien 
        # abgelegt werden, die über die URL 
        # "http://127.0.0.1:65000/logic/[namespace]/[dateiname]" erreicht 
        # werden, ein Zugriff über LAN ist nicht möglich!
        # Es wird empfohlen, unterhalb von _logic ein weiteres Verzeichnis als 
        # "Namespace" anzulegen, damit sich bei zukünftiger Verwendung keine 
        # Probleme durch Nutzung von verschiedenen Stellen aus ergeben. Der 
        # "Namespace" könnte z.B. die Baustein-ID oder ein beliebiger Schlüssel 
        # sein.
        # Als Anwendungsmöglichkeit bietet sich z.B. die Ablage von 
        # Konfigurationsdaten für den jeweiligen Logikbaustein an.

        target_url = 'http://127.0.0.1:65000/logic/14107/export.csv'
        datafile = urllib2.urlopen(target_url)


    def parseExport(self, datafile):
        print("Running parseExport")
        g_register = {}

        # @todo convert to jason  id -> other keyes: values
        for row in datafile:
            row = row.replace('"', '')
            data = row.split(';')
            if (len(data) < 6):
                continue

            # Title;Info;ID;Unit;Size;Factor;Min;Max;Default;Mode
            # 0     1    2  3    4    5      6   7   8       9
            try:
                self.g_register[int(data[2])] = {"Title": data[0], "Size": data[4], "Factor": float(data[5])}
            except:
                pass

    def chkMsg(self, msg):
        print("Running chkMsg")
        inMsg = bytearray(msg)
        outMsg = []
        chksm = 0

        for i in range(len(inMsg)):
            if (inMsg[i] == 0x5c) and (i < len(inMsg) - 1):
                outMsg = inMsg[i+1:]
                break

        if(len(outMsg) < 4):
            print("- Msg too short")
            return inMsg, False

        msgLen = int(outMsg[3])
        cntLen = len(outMsg[4:-1])
        print("- Msg length is said with " + str(msgLen) + " bytes and counted with " + str(cntLen))

        if (cntLen < msgLen):
            print("- Length error, counted " + str(cntLen))
            return inMsg, False

        msgChkSm = outMsg[msgLen + 4]
        print("- Msg chksm= " + str(hex(msgChkSm)))
        chkSm = self.calcChkSm(outMsg[:-1])
        if (chkSm != msgChkSm):
            print("Checksum error, calculated: " + str(hex(chkSm)))
            return inMsg, False

        print("- Msg is OK!")

        return outMsg, True


    def calcChkSm(self, msg):
        chkSm = 0
        for x in msg:
            chkSm = chkSm ^ x
        return chkSm


    def parseRegister(self, data):
        reg = 0
        res = {}
        i = 0
        while i < len(data):

            # register
            reg = self.hex2int(data[i: i + 2])

            # reg = 0xffff -> skip and following data
            if (reg == 65535 or reg == 0):
                #print("- Next register 0xffff or 0x0, skipping 4 byte")
                i = i + 4
                continue

            i = i + 2

            if reg not in self.g_register:
                print("- Register " + str(reg) + " not known. Abort parse")
                continue

            # value
            size = self.g_register[reg]["Size"]
            factor = self.g_register[reg]["Factor"]

            #print("- Register: " + str(reg) + "; size: " + size + "; factor: " + str(factor))

            if (size == "s8") or (size == "u8"):

                val = self.hex2int(data[i:i + 2]) / factor
                #print("- Value: " + str(val))
                i = i + 2

            elif (size == "s16") or (size == "u16"):
                val = self.hex2int(data[i:i + 2]) / factor
                #print("- Value: " + str(val))
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
                print("- Unknown size")

            # write value
            res[reg] = self.g_register[reg]
            res[reg]["value"] = val

        return res


    def parseData(self, msg):
        print("Running parseData")

        sender = msg[0]
        addr = msg[1]
        cmd = msg[2]
        length = msg[3]
        crc = msg[-1]
        data = msg[4:-2]

        # remove escaping of startbyte 0x5c
        i = 0
        while i < len(data) - 1:
            if (data[i] == 0x5c) and (data[i + 1] == 0x5c):
                data.pop(i)
                print("- Removed 0x5c escaping")
            i = i + 1

        # 20 value register msg
        if (cmd == 0x68):
            return self.parseRegister(data)

        # response for single register request
        elif(cmd == 0x6a):
            return self.parseRegister(data)

        # ignore, seems to be a confirmation of an executed command
        elif (cmd == 0x6c): # and $msg eq "5c00206c01014c") {
            print("- Msg 0x6c not implemented")

        # readingsBulkUpdate
        elif (cmd == 0x6d): #and substr($msg, 10, 2*$length) =~ m/(.{2})(.{4})(.*)/) {
            print(self.printByteArray(data))

            ver = data[0:3]
            prod = data[3:]
            print(self.printByteArray(ver))
            print(prod)
            print("- Msg 0x6d not implemented")

        else:
            print("- unknown msg")


    def printByteArray(self, data):
        s = ""
        for i in range(len(data)):
            s = s + " " + str(hex(data[i]))
        return s


    def hex2int(self, msg):
        val = 0
        #print(hex(msg[-1]))
        val = val | msg[-1]
        msg = msg[0:-1]
        for byte in msg[::-1]:
            #print(hex(byte))
            val = val << 8
            val = val | byte

        return val


    def on_init(self):
        print("Running on_init")
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        x = threading.Thread(target=self.listen)
        x.start()


    def on_input_value(self, index, value):
        pass