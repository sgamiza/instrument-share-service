# -*- coding: utf-8 -*-
"""
:Author: YOUR_NAME
:Contact Mail: YOUR_EMAIL
:Description: This is for TopYoung TA lib
:Version: 0.21
:Modified: 2021-10-26
:Modified: 2022-3-22 for voltage value
:Modified: 2023-3-10 add TSS32T1 control
"""
import telnetlib
import socket
import time


class TopYoung:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        pass

    def open_telnet_connection(self, ip_address, port):
        """
        Telnet Connection: Opens connection to the given ip address and port
        """
        socket.setdefaulttimeout(10)
        self.session = telnetlib.Telnet(ip_address, int(port))
        # self.session.read_until(">".encode())
        print("telnet connected")

    def telnet_command(self, command, UntilContent='\n', timeout=30):
        """
        The default UntilContent is '\n'.
        The timeout has default value 30s.
        """
        self.__write(command)
        # print(self.session.read_eager())
        return self.read_buff(UntilContent, timeout)

    def telnet_command_utf8(self, command, UntilContent='\n', timeout=30):
        """
        The default UntilContent is '\n'.
        The timeout has default value 30s.
        Commands for utf-8
        """
        self.__write_utf8(command)
        return self.read_buff_utf8(UntilContent, timeout)

    def telnet_cmd_no_resp(self, command):
        """
        write a command to telnet port and no response needed
        input: command, string
        return: response in string
        """
        self.__write(command)

    def __write(self, command):
        self.session.write(command.encode() + "\n".encode())
        print(command)
        # self.session.write(("\r\n").encode())

    def read_buff(self, UntilContent, timeout=30):
        """
        The timeout has default value 30.
        """
        response = self.session.read_until((UntilContent).encode(), timeout)
        response = response.decode()
        return response

    def __write_utf8(self, command):
        """
        Suitable for utf-8
        """
        self.session.write(command.encode('utf-8'))
        print(command)
        self.session.write(("\r\n").encode('utf-8'))

    def read_buff_utf8(self, UntilContent, timeout=30):
        """
        Suitable for utf-8
        The timeout has default value 30.
        """
        response = self.session.read_until((UntilContent).encode('utf-8'), timeout)
        response = response.decode('utf-8')
        return response

    def __is_number(self, s):
        try:
            f = float(s)
            if f != f or f == float('inf') or f == float('-inf'):
                return False
            return True
        except ValueError:
            return False

    def telnet_close(self):
        self.session.close()
        print("telnet closed!")

    def power_on(self, pb_ip, port):
        self.open_telnet_connection(pb_ip, 3000)
        response = self.telnet_command("SET:%s:ON" % port).split(":")[2].strip("\r\n")
        self.telnet_close()
        if response == "OK":
            return response
        else:
            raise Exception('power on failled!')

    def power_off(self, pb_ip, port):
        self.open_telnet_connection(pb_ip, 3000)
        response = self.telnet_command("SET:%s:OFF" % port).split(":")[2].strip("\r\n")
        self.telnet_close()
        if response == "OK":
            return response
        else:
            raise Exception('power off failled!')

    def port_reset(self, pb_ip, port):
        self.open_telnet_connection(pb_ip, 3000)
        response = self.telnet_command("READ:%s" % port).split(":")[2].strip("\r\n")
        print(response)
        if response == 'ON':
            self.power_off(pb_ip, port)
            self.power_on(pb_ip, port)
        elif response == "OFF":
            self.power_on(pb_ip, port)
            self.power_off(pb_ip, port)
        else:
            print("PB STATUS ERROR!")

    def get_voltage(self, pb_ip, port):
        self.open_telnet_connection(pb_ip, 3000)
        response = self.telnet_command("READVOLTAGE:%s" % port).split(":")[2].strip("\r\n")
        print('Get voltage value: %s' % response)
        self.telnet_close()
        if self.__is_number(response):
            return response
        else:
            raise Exception('get voltage value failed!')

    def get_current(self, pb_ip, port):
        self.open_telnet_connection(pb_ip, 3000)
        response = self.telnet_command("READCURRENT:%s" % port).split(":")[2].strip("\r\n")
        print('Get current value: %s' % response)
        self.telnet_close()
        if self.__is_number(response):
            return response
        else:
            raise Exception('get current value failed!')

    def rf_switch_TSS32T1_close_port(self, rf_switch_mgt_ip, *port_num):
        """
        this function only suport 32 port rf switch ,others need refer to xxx Manual.pdf
        please refer to XUM30200215-C-32T1-User Manual.pdf's Appendix 3 RF SCHEMATIC for switch1 to switch5

        exp:
            rf_switch_TSS32T1_close_port("127.0.0.1",32) to close port 32

        """
        # 适配工作
        port_num = port_num[0]
        print("rf_switch_TSS32T1_close_port: %s" % port_num)


        SWITCH5_ID = 5
        port_num = int(port_num)

        if 1 <= port_num <= 32:
            switchx_id, remain = divmod(port_num + 8 - 1, 8)
            switchx_pin_id = remain + 1
            switch5_pin_id = switchx_id if switchx_id < 3 else switchx_id + 1
            # commands
            close_switchx = f'SWITch:CLOSe {switchx_id},{switchx_pin_id}'
            close_switch5 = f'SWITch:CLOSe {SWITCH5_ID},{switch5_pin_id}'
            status_switchx = 'SWITch:STATus?' + ' ' + str(switchx_id)
            status_switch5 = 'SWITch:STATus?' + ' ' + str(SWITCH5_ID)
            self.open_telnet_connection(rf_switch_mgt_ip, 3000)
            self.telnet_command(close_switchx, timeout=1)
            self.telnet_command(close_switch5, timeout=1)
            # check status
            response_for_switchx_pin = self.telnet_command(status_switchx, timeout=1)
            response_for_switch5_pin = self.telnet_command(status_switch5, timeout=1)
            if switchx_pin_id == int(response_for_switchx_pin) and \
                    switch5_pin_id == int(response_for_switch5_pin):
                print('Set Switch port_num %s successfully' % str(port_num))
            else:
                print('Switch port_num %s is fail')
        else:
            raise ValueError("wrong RFswitch port number, need 1 to 32 !")

    def set_one_PA_port_close_32x16(self, pb_ip, *ports):
        """
        this function only suport 32x16 PA to close one port

        exp:
            set_one_PA_port_close_32x16("127.0.0.1", "A20", "B9")

        """
        # 适配工作
        portA, portB = ports
        print("set_one_PA_port_close_32x16: %s %s" % (portA, portB))

        # set_str = 'RESETM:OK'
        self.open_telnet_connection(pb_ip, 3000)

        import re
        A_num = int(re.findall(r"\d+", str(portA))[0])
        B_num = int(re.findall(r"\d+", str(portB))[0])
        num_to_close = A_num * 16 - (16 - B_num)

        # 横向设置
        for i in range(1, 33):
            # num_to_open = i * 16 - (16 - B_num)
            # response = self.telnet_command("SET:%s:120\n" % num_to_open, timeout=1)
            # print(num_to_open)

            response = self.telnet_command("SET:%s:120\n" % (i * 16 - (16 - B_num)), timeout=1)
            print(response)

        # 纵向设置
        for i in range(16):
            # num_to_open = A_num * 16 - i
            # response = self.telnet_command("SET:%s:120\n" % num_to_open, timeout=1)
            # print(num_to_open)

            response = self.telnet_command("SET:%s:120\n" % (A_num * 16 - i), timeout=1)
            print(response)


        response = self.telnet_command("SET:%s:0\n" % num_to_close, timeout=1)
        print(response)

        self.telnet_close()



# TODO 删除 __main__
if __name__ == '__main__':


    s = time.time()





    tp = TopYoung()


    # rf switch
    # tp.rf_switch_TSS32T1_close_port("127.0.0.1", 31)
    # '''SWITch:CLOSe 1,2'''


    # PB
    # print(tp.power_on('127.0.0.1', 1))


    # PA
    tp.set_one_PA_port_close_32x16("127.0.0.1", "A1", "B1")
    # tp.set_one_PA_port_close_32x16("127.0.0.1", "A1", "B2")
    # tp.set_one_PA_port_close_32x16("127.0.0.1", "A2", "B2")
    # tp.set_one_PA_port_close_32x16("127.0.0.1", "A3", "B3")

    e = time.time()
    print(e - s)
