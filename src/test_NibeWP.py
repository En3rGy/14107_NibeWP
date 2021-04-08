# coding: UTF-8

import unittest

import json
import socket
import threading
import urllib2

import time


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: float
        debug_set_remanent = {}  # type: float
        debug_input_value = {}

        def __init__(self, a, b):
            pass

        def _get_framework(self):
            f = hsl20_4.Framework()
            return f

        def _get_logger(self, a, b):
            return 0

        def _get_remanent(self, key):
            return 0

        def _set_remanent(self, key, val):
            self.debug_set_remanent = val

        def _set_output_value(self, pin, value):
            self.debug_output_value[int(pin)] = value
            print "# Out: " + str(value) + " @ pin " + str(pin)

        def _get_input_value(self, pin):
            if pin in self.debug_input_value:
                return self.debug_input_value[pin]
            else:
                return 0

    class Framework:
        def __init__(self):
            pass

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_4.DebugHelper()
            return d

        def get_homeserver_private_ip(self):
            return "192.168.143.30"

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print("DEBUG value\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print("Debug Msg\t" + str(msg))

    ############################################

class NibeWP_14107_14107(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14107_NibeWP")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
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

    ############################################

    g_msg = 0
    g_register = {}
    g_out = {}
    debug_only = False

    g_bigendian = False

    # Re-ordering / inversing the byte order
    def shift_bytes(self, msg):
        res = []
        for x in msg[::-1]:
            res.append(x)
        return res

    # Main server loop, listening for incomming messages
    def listen(self):
        # declare our serverSocket upon which
        # we will be listening for UDP messages
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # One difference is that we will have to bind our declared IP address
        # and port number to our newly declared server_sock
        UDP_IP_ADDRESS = self.FRAMEWORK.get_homeserver_private_ip()
        UDP_PORT_NO = self._get_input_value(self.PIN_I_N_HSPORT)

        self.DEBUG.add_message("listen: Start listening for incoming msgs at "
                               + str(UDP_IP_ADDRESS) + ":" + str(UDP_PORT_NO))

        try:
            server_sock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
            data = ""

            while True:
                data = data + server_sock.recv(1024)
                msg, ret = self.chk_msg(data)
                if ret:
                    self.parse_data(msg)
                    data = ""
                else:
                    if msg is None:
                        data = ""

        except Exception as e:
            self.DEBUG.add_message("ERROR listen: " + str(e) + " (abort)")
        finally:
            server_sock.close()

    # Reads the Modbus Manager export file which is provided to the HS,
    # see HS help for "hsupload"
    def read_export(self):
        try:
            target_url = 'http://127.0.0.1:65000/logic/14107/export.csv'
            datafile = urllib2.urlopen(target_url)
            self.parse_export(datafile)
        except Exception as e:
            self.DEBUG.add_message("ERROR readExport: " + str(e))

    # Parses the Modbus Manager export file and stores the content to self.g_register
    def parse_export(self, datafile):
        # print("Running parseExport")
        self.g_register = {}
        i = 0

        for row in datafile:
            row = row.replace('"', '')
            data = row.split(';')
            if len(data) < 10:
                continue

            # Title;Info;ID;Unit;Size;Factor;Min;Max;Default;Mode
            # 0     1    2  3    4    5      6   7   8       9
            try:
                self.g_register[int(data[2])] = {"Title": data[0], "Size": data[4], "Factor": float(data[5]),
                                                 "Mode": data[9]}
                i = i + 1
            except Exception as e:
                self.DEBUG.add_message("parseExport: " + str(e) + " with '" + str(data) + "'")

        self.DEBUG.add_message("parseExport: Read Modbus Manager file with " + str(i) + " entries.")

    # Checks the integrity of a received message
    # Example:
    # 5c 00 20 6d 0e 01 24 18 46 31 31 34 35 2d 31 30 20 44 45 34
    #                |---------- Bytes vor len count --------| 
    #    |------------ Bytes for checksum calculation -------|
    def chk_msg(self, msg):
        try:
            # print("Running chkMsg")
            in_msg = bytearray(msg)
            out_msg = []

            # check for start byte
            for i in range(len(in_msg)):
                if (in_msg[i] == 0x5c) and (i < len(in_msg) - 1):
                    out_msg = in_msg[i + 1:]
                    break

            # check if msg is complete
            if len(out_msg) < 4:
                return out_msg, False

            msg_len = int(out_msg[3])
            cnt_len = len(out_msg[4:-1])

            if cnt_len < msg_len:
                return out_msg, False

            out_msg = out_msg[:4 + msg_len + 1]

            # check checksum
            msg_chk_sm = out_msg[msg_len + 4]
            chksm = self.calc_chk_sm(out_msg[:-1])
            if chksm != msg_chk_sm:
                self.DEBUG.add_message("chkMsg: Checksum error")
                self.DEBUG.set_value("Last failed msg", self.print_byte_array(in_msg))
                return None, False

            return out_msg, True

        except Exception as e:
            self.DEBUG.add_message("ERROR chkMsg: " + str(e))

    # Calculates XOR checksum
    def calc_chk_sm(self, msg):
        chk_sm = 0x00
        for x in msg:
            chk_sm = chk_sm ^ x
        return chk_sm

    # Parses the data block of an incoming message
    def parse_register(self, data, cmd6a=False):
        try:
            reg = 0
            res = {}
            i = 0
            while i < len(data):

                # register
                reg = self.hex2int(data[i: i + 2])
                # self.DEBUG.add_message("Register received: " + str(self.printByteArray(data[i: i + 2]) + " ~ " + str(reg)))

                # reg = 0xffff -> skip and following data
                if reg == 65535 or reg == 0:
                    # print("- Next register 0xffff or 0x0, skipping 4 byte")
                    i = i + 4
                    continue

                i = i + 2

                if reg not in self.g_register:
                    self.DEBUG.add_message("Register " + str(reg) + " not known. Abort parse.")
                    return False, res

                # value
                size = self.g_register[reg]["Size"]
                if cmd6a:
                    size = size[0] + "32"

                factor = self.g_register[reg]["Factor"]

                if (size == "s8") or (size == "u8"):
                    if (data[i + 1] & 0x80 == 0x80) and (size == "s8"):
                        val = self.complement2(data[i:i + 2]) / factor
                    else:
                        val = self.hex2int(data[i:i + 2]) / factor
                    i = i + 2

                elif (size == "s16") or (size == "u16"):
                    if (data[i + 1] & 0x80 == 0x80) and (size == "s16"):
                        val = self.complement2(data[i:i + 2]) / factor
                    else:
                        val = self.hex2int(data[i:i + 2]) / factor
                    i = i + 2

                elif (size == "s32") or (size == "u32"):
                    # check next register
                    reg_next = self.hex2int(data[i + 2:i + 4])

                    if reg_next - reg == 1:
                        # print("- next register is split register")
                        # x32 uses next register for full value
                        val1 = data[i:i + 2]
                        i = i + 4

                        val2 = data[i:i + 2]
                        data32 = val1.append(val2)

                        val = self.hex2int(data32) / factor
                        # print("- Value: " + str(val))
                        i = i + 2
                    else:
                        # print("- next register is 0xffff, skip")
                        val = self.hex2int(data[i:i + 2]) / factor
                        # print("- Value: " + str(val))
                        i = i + 6

                else:
                    self.DEBUG.add_message("ERROR parseRegister: size of value unknown.")

                # write value
                res[str(reg)] = {}
                res[str(reg)]["Title"] = self.g_register[reg]["Title"]
                res[str(reg)]["value"] = val

                if "out" in self.g_register[reg]:
                    out_pin = self.g_register[reg]["out"]

                    if out_pin != 0:
                        if "Value" in self.g_register[reg]:
                            if self.g_register[reg]["Value"] != val:
                                self._set_output_value(out_pin, val)
                                self.g_register[reg]["Value"] = val
                        else:
                            self._set_output_value(out_pin, val)
                            self.g_register[reg]["Value"] = val

            return True, res

        except Exception as e:
            self.DEBUG.add_message("ERROR parseRegister: " + str(e))
            return False, None

    def parse_data(self, msg):
        try:
            # sender = msg[0]
            # addr = msg[1]
            cmd = msg[2]
            # length = msg[3]
            data = msg[4:-2]
            # crc = msg[-1]

            self.DEBUG.set_value("last raw msg " + str(hex(cmd)),
                                 str(hex(0x5c)) + " " + self.print_byte_array(msg))

            # remove escaping of startbyte 0x5c
            i = 0
            while i < len(data) - 1:
                if (data[i] == 0x5c) and (data[i + 1] == 0x5c):
                    data.pop(i)
                    print("- Removed 0x5c escaping")
                i = i + 1

            # 20 value register msg
            if cmd == 0x68:
                ok, ret = self.parse_register(data)
                if not ok:
                    self.DEBUG.add_message("Error reading msg " + str(hex(0x5c)) + " " + self.print_byte_array(msg))
                    return None
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
                self._set_output_value(self.PIN_O_N_ALIVE, 1)
                self.DEBUG.add_message("parse_data: Received 0x68 Nibe data")
                return jsn

            # response for single register request
            elif cmd == 0x6a:
                # @todo value always 32bit!
                ok, ret = self.parse_register(data, True)
                if not ok:
                    self.DEBUG.add_message("Error reading msg " + str(hex(0x5c)) + " " + self.print_byte_array(msg))
                    return None
                jsn = str(ret).replace("'", '"')  # exchange ' by "
                self._set_output_value(self.PIN_O_S_VALUES, jsn)
                self.DEBUG.add_message("parse_data: Received 0x6a Nibe data")
                return jsn

            # ignore, seems to be a confirmation of an executed command
            # 5c00206c01014c
            elif cmd == 0x6c:  # and $msg eq "5c00206c01014c") {
                pass
            # print("- Msg 0x6c not implemented")

            # readingsBulkUpdate
            elif cmd == 0x6d:  # and substr($msg, 10, 2*$length) =~ m/(.{2})(.{4})(.*)/) {
                # ver = self.hex2int(data[0:3])
                ver = self.hex2int(data[1:3])
                prod = data[3:]
                self._set_output_value(self.PIN_O_N_VER, ver)
                self._set_output_value(self.PIN_O_S_MODEL, prod)
                self.DEBUG.add_message("parse_data: Received 0x6d Nibe data")
                return str(str(prod) + " / " + str(ver))

            # 0x5c 0x0 0x20 0xee 0x0 0xce
            elif cmd == 0xee:
                self.DEBUG.add_message("parse_data: Received 0xee Nibe data")

            else:
                pass
                self.DEBUG.add_message("parse_data: Received unknown Nibe data")

        except Exception as e:
            self.DEBUG.add_message("ERROR parse_data: " + str(e) + " with msg " + self.print_byte_array(msg))

    def int2hex(self, value, size):
        if size == "s8" or size == "u8":
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8

            val = chr(val1) + chr(val2)

        elif size == "s16" or size == "u16":
            val1 = value & 0x00FF
            val2 = value & 0xFF00
            val2 = val2 >> 8

            val = chr(val1) + chr(val2)

        elif size == "s32" or size == "u32":
            val1 = value & 0x000000FF
            val2 = value & 0x0000FF00
            val3 = value & 0x00FF0000
            val4 = value & 0xFF000000
            val2 = val2 >> 8
            val3 = val3 >> 16
            val4 = val4 >> 24

            val = chr(val1) + chr(val2) + chr(val3) + chr(val4)

        return val

    def send_data(self, port, data):
        ipaddr = str(self._get_input_value(self.PIN_I_S_GWIP))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # connect the socket, think of it as connecting the cable to the address location
        s.connect((ipaddr, port))
        len_send = s.send(data)
        s.close()
        # print("len_send = " + str(len_send) + "; len(data) = " + str(len(data)))
        self.DEBUG.add_message("Msg. send to Nibe")
        if len_send != len(data):
            self.DEBUG.add_message("ERROR Size of data send != size of data provided in send_data")

        self.DEBUG.set_value("Last send",
                             self.print_byte_array(bytearray(data)) + " to " + ipaddr + ":" + str(port))

    def read_register(self, register):
        try:
            msg = "\xc0\x69\x02"
            reg = self.int2hex(register, "u16")
            msg = msg + reg
            chksm = self.calc_chk_sm(bytearray(msg))
            msg = msg + chr(chksm)

            port = int(self._get_input_value(self.PIN_I_N_GWPORTGET))
            self.send_data(port, msg)
        except Exception as e:
            self.DEBUG.add_message("ERROR readRegister: " + str(e))

    def write_register(self, register, value):
        try:
            msg = "\xc0\x6b\x06"

            reg = self.int2hex(int(register), "u16")
            msg = msg + reg

            mode = self.g_register[register]["Mode"]
            if ("W" not in mode) and ("w" not in mode):
                self.DEBUG.add_message("write_register: Register " + str(register) + " is read only. Aborting send.")
                return

            factor = self.g_register[register]["Factor"]
            value = int(value * factor)
            # size = self.g_register[register]["Size"]
            value = self.int2hex(value, "u32")  # u32
            while len(value) < 4:
                value = "\x00" + value
            msg = msg + value

            chksm = self.calc_chk_sm(bytearray(msg))
            msg = msg + chr(chksm)

            port = int(self._get_input_value(self.PIN_I_N_GWPORTSET))
            self.send_data(port, msg)
        except Exception as e:
            self.DEBUG.add_message("ERROR write_register: " + str(e))

    def print_byte_array(self, data):
        s = ""
        for i in range(len(data)):
            s = s + " " + str(hex(data[i]))
        s = s[1:]
        return s

    def hex2int(self, msg):
        if not self.g_bigendian:
            msg = self.shift_bytes(msg)

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

    def test_endian(self):
        data = bytearray("\x80\x00")
        val = 0
        val = val | data[0]
        for byte in data[1:]:
            val = val << 8
            val = val | byte

        self.DEBUG.add_message(self.print_byte_array(data) + " -> " + str(val) +
                               " (32768 little endian, 8 big endian)")

    def init_export_csv(self):
        self.read_export()

        for i in range(self.PIN_I_S_REG20 - self.PIN_I_S_REG01):
            out_id = self.PIN_O_N_REG01 + i
            reg = self._get_input_value(self.PIN_I_S_REG01 + i)
            if reg == 0:
                continue
            if reg in self.g_register:
                self.g_register[reg]["out"] = out_id
            else:
                self.DEBUG.add_message("initExportCsv: Register " + str(reg) + " at EW" +
                                       str(self.PIN_I_S_REG01 + i) +
                                       " not defined in Mobus Manager Export.")

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_msg = 0
        self.g_register = {}
        self.g_out = {}
        self.g_bigendian = False

        self.test_endian()
        self.init_export_csv()
        x = threading.Thread(target=self.listen)
        if not self.debug_only:
            x.start()

    def on_input_value(self, index, value):
        if index == self.PIN_I_S_CMDGET:
            self.read_register(value)

        elif index == self.PIN_I_S_CMDSET:
            val = value.split(':')
            register = int(val[0])
            val = float(val[1])
            self.write_register(register, val)

        elif index >= self.PIN_I_S_REG01:
            out_id = index - self.PIN_I_S_REG01 + self.PIN_O_N_REG01
            self.g_register[value]["out"] = out_id
            old_reg = 0

            if out_id in self.g_out:
                old_reg = self.g_out[out_id]
                self.g_register[old_reg]["out"] = 0
                self.g_out[out_id] = value


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
        print("\n### test_cmpBytearray")
        tst = NibeWP_14107_14107(0)
        data1 = tst.shift_bytes(bytearray("\x9c\x44\x56"))
        data2 = bytearray("\x56\x44\x9c")
        self.assertTrue(self.cmpBytearray(data1, data2))

    def test_hex2int_bigEndian(self):
        print("\n### test_hex2int_bigEndian")
        tst = NibeWP_14107_14107(0)
        tst.g_bigendian = True
        val1 = tst.hex2int(bytearray("\x9c\x44\x56"))
        self.assertEqual(val1, 10241110)

    def test_hex2int_littleEndian(self):
        print("\n### test_hex2int_littleEndian")
        tst = NibeWP_14107_14107(0)
        tst.g_bigendian = False
        val1 = tst.hex2int(bytearray("\x9c\x44\x56"))
        self.assertEqual(val1, 5653660)

    def test_complement2(self):
        print("\n### test_complement2")
        tst = NibeWP_14107_14107(0)
        tst.g_bigendian = False
        data1 = bytearray("\x76\x85\x81")
        val1 = tst.complement2(data1)
        self.assertEqual(val1, -8288906)

    def test_printByteArray(self):
        print("\n### test_printByteArray")
        tst = NibeWP_14107_14107(0)
        data1 = bytearray("\xab\xcd\xef")
        res = tst.print_byte_array(data1)
        self.assertEqual(res, "0xab 0xcd 0xef")

    def test_getHexValue(self):
        print("\n### test_getHexValue")
        tst = NibeWP_14107_14107(0)
        tst.g_bigendian = True

        tst.g_bigendian = False
        data1 = tst.int2hex(156, 'u8') # 9C
        self.assertEqual(data1, "\x9c\x00")
        data1 = tst.int2hex(40004, 'u16') #9c 44
        self.assertEqual(data1, "\x44\x9c")
        data1 = tst.int2hex(2621733731, 'u32')
        # self.assertEqual(data1, "\x9c\x44\x7b\x63")
        self.assertEqual(data1, "\x63\x7b\x44\x9C")

    def test_parseData_x68(self):
        print("\n### test_parseData_x68")
        tst = NibeWP_14107_14107(0)
        tst.debug_only = True
        tst.on_init()
        tst.g_bigendian = False
        datafile = open("export.csv", 'r')
        tst.parse_export(datafile)

        tst.on_input_value(tst.PIN_I_S_REG01, 43427)
        tst.on_input_value(tst.PIN_I_S_REG02, 41265)
        tst.on_input_value(tst.PIN_I_S_REG03, 40072)
        tst.on_input_value(tst.PIN_I_S_REG04, 45001)
        tst.on_input_value(tst.PIN_I_S_REG05, 47041)
        tst.on_input_value(tst.PIN_I_S_REG06, 42035)
        tst.on_input_value(tst.PIN_I_S_REG07, 40012)
        tst.on_input_value(tst.PIN_I_S_REG08, 40016)
        tst.on_input_value(tst.PIN_I_S_REG09, 40004)
        tst.on_input_value(tst.PIN_I_S_REG10, 40014)
        tst.on_input_value(tst.PIN_I_S_REG11, 40015)
        tst.on_input_value(tst.PIN_I_S_REG12, 48043)
        tst.on_input_value(tst.PIN_I_S_REG13, 40008)
        tst.on_input_value(tst.PIN_I_S_REG14, 42075)
        tst.on_input_value(tst.PIN_I_S_REG15, 40071)

        # msg1 = "\x5c\x00\x20\x68\x50\x44\x9c\xca\xff\x48\x9c\xab\x01\x4c\x9c\x3c\x01\x4e\x9c\x8f\x01\x87\x9c\x37\x01\x4f\x9c\x65\x00\x50\x9c\x38\x00\x88\x9c\x94\x00\xc9\xaf\x00\x00\x5b\xa4\x00\x80\xff\xff\x00\x00\x33\xa4\x00\x00\xff\xff\x00\x00\xa3\xa9\x3c\x00\xab\xbb\x00\x00\xc1\xb7\x04\x00\x31\xa1\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\x9f"
        msg1 = "\x00\x20\x68\x50\x44\x9c\xca\xff\x48\x9c\xab\x01\x4c\x9c\x3c\x01\x4e\x9c\x8f\x01\x87\x9c\x37\x01\x4f\x9c\x65\x00\x50\x9c\x38\x00\x88\x9c\x94\x00\xc9\xaf\x00\x00\x5b\xa4\x00\x80\xff\xff\x00\x00\x33\xa4\x00\x00\xff\xff\x00\x00\xa3\xa9\x3c\x00\xab\xbb\x00\x00\xc1\xb7\x04\x00\x31\xa1\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\x9f"
        res1 = '{"43427": {"value": 60.0, "Title": "Compressor State EP14"}, "41265": {"value": 0.0, "Title": "Smart Home Mode"}, "40072": {"value": 14.8, "Title": "BF1 EP14 Flow"}, "45001": {"value": 0.0, "Title": "Alarm"}, "47041": {"value": 4.0, "Title": "Hot water comfort mode"}, "42035": {"value": 0.0, "Title": "AA23-BE5 EME20 Total Power"}, "40012": {"value": 31.6, "Title": "EB100-EP14-BT3 Return temp"}, "40016": {"value": 5.6, "Title": "EB100-EP14-BT11 Brine Out Temp"}, "40004": {"value": -5.4, "Title": "BT1 Outdoor Temperature"}, "40014": {"value": 39.9, "Title": "BT6 HW Load"}, "40015": {"value": 10.1, "Title": "EB100-EP14-BT10 Brine In Temp"}, "48043": {"value": 0.0, "Title": "Holiday - Activated"}, "40008": {"value": 42.7, "Title": "BT2 Supply temp S1"}, "42075": {"value": 3276.8, "Title": "AA23-BE5 EME20 Total Energy"}, "40071": {"value": 31.1, "Title": "BT25 Ext. Supply"}}'

        ret1 = tst.parse_data(bytearray(msg1))
        self.assertEqual(res1, ret1, "a")

        self.assertEqual(60, tst.debug_output_value[tst.PIN_O_N_REG01], "b1")
        self.assertEqual(0, tst.debug_output_value[tst.PIN_O_N_REG02], "b2")
        self.assertEqual(14.8, tst.debug_output_value[tst.PIN_O_N_REG03], "b3")
        self.assertEqual(0, tst.debug_output_value[tst.PIN_O_N_REG04], "b4")
        self.assertEqual(4, tst.debug_output_value[tst.PIN_O_N_REG05], "b5")
        self.assertEqual(0, tst.debug_output_value[tst.PIN_O_N_REG06], "b6")
        self.assertEqual(31.6, tst.debug_output_value[tst.PIN_O_N_REG07], "b7")
        self.assertEqual(5.6, tst.debug_output_value[tst.PIN_O_N_REG08], "b8")
        self.assertEqual(-5.4, tst.debug_output_value[tst.PIN_O_N_REG09], "b9")
        self.assertEqual(39.9, tst.debug_output_value[tst.PIN_O_N_REG10], "b10")
        self.assertEqual(10.1, tst.debug_output_value[tst.PIN_O_N_REG11], "b11")
        self.assertEqual(0, tst.debug_output_value[tst.PIN_O_N_REG12], "b12")
        self.assertEqual(42.7, tst.debug_output_value[tst.PIN_O_N_REG13], "b13")
        self.assertEqual(3276.8, tst.debug_output_value[tst.PIN_O_N_REG14], "b14")
        self.assertEqual(31.1, tst.debug_output_value[tst.PIN_O_N_REG15], "b15")

    def test_parseData_x6a(self):
        print("\n### test_parseData_x6a")
        tst = NibeWP_14107_14107(0)
        tst.on_init()
        tst.g_bigendian = False
        # msg1 = "\x5c\x00\x20\x6a\x06\xab\xbb\x00\x00\x8d\x10\xc1"
        msg1 = "\x00\x20\x6a\x06\xab\xbb\x00\x00\x8d\x10\xc1"
        res1 = '{"48043": {"value": 0.0, "Title": "Holiday - Activated"}}'

        datafile = open("export.csv", 'r')
        tst.parse_export(datafile)
        ret1 = tst.parse_data(bytearray(msg1))
        self.assertEqual(res1, ret1)

    def test_write(self):
        print("\n### test_write")
        tst = NibeWP_14107_14107(0)
        tst.debug_input_value[tst.PIN_I_S_GWIP] = "192.168.143.18"
        tst.debug_input_value[tst.PIN_I_N_HSPORT] = 9999
        tst.debug_input_value[tst.PIN_I_N_GWPORTGET] = 9999
        tst.debug_input_value[tst.PIN_I_N_GWPORTSET] = 10000
        tst.on_init()
        datafile = open("export.csv", 'r')
        tst.parse_export(datafile)

        tst.g_bigendian = False
        cmd = "47041:4" # ist: B7C1 = 47041 wird in WP angezeigt als -> 49591 = C1B7

        tst.on_input_value(tst.PIN_I_S_CMDSET, cmd)
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
