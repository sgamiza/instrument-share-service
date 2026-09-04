# -*- coding: utf-8 -*-
"""
:Author: YOUR_NAME
:Contact Mail: YOUR_EMAIL
:Description: This is for TopYoung TA lib
:Version: 0.2
:Modified: 2021-10-26
:Modified: 2022-3-22 for voltage value
"""
import telnetlib
import socket
import time


class TopYoung_TA:
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
        print ("telnet connected")

    def telnet_command(self, command, UntilContent='\n', timeout=30):
        """
        The default UntilContent is '\n'.
        The timeout has default value 30s.
        """
        self.__write(command)
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
        print (command)
        #self.session.write(("\r\n").encode())

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
        print (command)
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
        print ("telnet closed!")
        
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
        if response=='ON':
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

    def get_current(self, pb_ip, port, list_a, power):
        set_str = 'RESETM:OK'
        self.open_telnet_connection(pb_ip, port)
        list_b = []
        list_val = []
        for i in range(1,len(list_a)+1):
            list_b.append(i)
        for j in range(len(list_a)):
            list_val.append((int(list_a[j])-1)*4+list_b[j])
        #print("get value : ", list_val)
        for val in list_val:
            response = self.telnet_command("SETM:%s,%s\n" % (val, power))
        time.sleep(1)
        #response = self.telnet_command("SETM:1,20:6,20:19,20:24,20\n")
        #set_value = self.telnet_command("READM:1:2:3:4:5:6:7:8:9:10\n")
        #print('Get current value: %s' % set_value)
        if set_str in response:
            print("set success!")
        else:
            print("set failed!")
        for k in range(1,33):
            get_value = self.telnet_command("READM:%s\n" %k)
            print('get_value: %s' % get_value)
        self.telnet_close()

    def get_current_special(self, pb_ip, port, list_a, power):
        set_str = 'RESETM:OK'
        self.open_telnet_connection(pb_ip, port)
        #print("get value : ", list_val)
        for val in list_a:
            response = self.telnet_command("SETM:%s,%s\n" % (int(val), power))
            time.sleep(1)
        #response = self.telnet_command("SETM:1,20:6,20:19,20:24,20\n")
        #set_value = self.telnet_command("READM:1:2:3:4:5:6:7:8:9:10\n")
        #print('Get current value: %s' % set_value)
        if set_str in response:
            print("set success!")
        else:
            print("set failed!")
        for k in range(1,33):
            get_value = self.telnet_command("READM:%s\n" %k)
            print('get_value: %s' % get_value)
        self.telnet_close()

    def restore_current(self, pb_ip, port):
        res_str = 'RESETM:OK'
        self.open_telnet_connection(pb_ip, port)
        for i in range(1,33):
            response = self.telnet_command("SETM:%s,180\n" % i)
        if res_str in response:
            print("restore set success!")
        else:
            print("restore set failed!")
        print('Get current value: %s' % response)
        self.telnet_close()


    def set_one_PA_port_close_32x16(self, pb_ip, portA, portB):
        # set_str = 'RESETM:OK'
        self.open_telnet_connection(pb_ip, 3000)

        import re

        A_num = int(re.findall(r"\d+", str(portA))[0])
        B_num = int(re.findall(r"\d+", str(portB))[0])
        num_to_close = A_num * 16 - (16 - B_num)

        for i in range(1, 33):
            num_to_open = i * 16 - (16 - B_num)
            response = self.telnet_command("SET:%s:0\n" % num_to_open)
            print(num_to_open)
            print(response)

        response = self.telnet_command("SET:%s:0\n" % num_to_close)
        print(response)

        self.telnet_close()


if __name__ == "__main__":
    test = TopYoung_TA()
    list_a = [1,2,5,6]
    power = 0
    test.get_current('127.0.0.1','3000',list_a,power)
    #test.restore_current('127.0.0.1','3000')

