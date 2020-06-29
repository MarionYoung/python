#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-05-08 15:20
# @Author  : Marion

import paramiko
import re
import time
import logging

logging.basicConfig(format="%(asctime)s %(name)s %(message)s", level=logging.INFO)

'''
新机上架后，在安装系统时，无需设置port Chanel
'''

class PortChannel:
    def __init__(self, ip, username, passwd, tport, port=22):
        self.user = username
        self.passwd = passwd
        self.ip = ip
        self.ssh_port = port
        self.tport = tport
        self.cport = tport.split('/')[-1]

    def ssh_conn(self):
        '''创建ssh连接'''
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, port=self.ssh_port, username=self.user, password=self.passwd, look_for_keys=False,
                        timeout=None, )
            return ssh
        except Exception as e:
            return e

    def multi_cmd(self, command):
        '''批量命令执行'''
        ssh = self.ssh_conn()
        ssh_shell = ssh.invoke_shell()
        for cmd in command:
            ssh_shell.sendall("%s  %s" % (cmd, "\n"))
            time.sleep(float(0.2))
        recv_data = ssh_shell.recv(65535)
        ssh.close()
        pattern = "\'\^\'\s+marker"
        if re.search(pattern, recv_data.decode()):
            logging.error(recv_data.decode())
        return recv_data

    def single_cmd(self, command):
        '''单个命令执行'''
        ssh = self.ssh_conn()
        if isinstance(ssh, paramiko.SSHClient):
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read()
            ssh.close()
            return result
        else:
            print(type(ssh), ssh)

    def check_channel(self):
        '''检查对应交换机物理口是否存在port channel'''
        channel_pattern = '(?<=channel-group\s)\d+'
        regx_channel = re.compile(channel_pattern)
        cmd = 'show running-config interface {}'.format(self.tport)
        tmp_result = self.single_cmd(cmd).strip()
        channel_result = regx_channel.search(tmp_result.decode())
        if channel_result:
            channelid = channel_result.group()
        else:
            channelid = None
        return channelid

    def del_channel(self):
        '''根据需要删除port channel'''
        channel_port = self.check_channel()
        if channel_port is not None:
            cmd = ['configure t', 'default interface {}'.format(self.tport), 'no channel-group {}'.format(channel_port), 'end']
            self.multi_cmd(cmd)

    def add_channel(self):
        '''根据需要增加port channel'''
        channel_port = self.check_channel()
        if channel_port is None:
            cmd = ['configure t', 'interface port-channel {}'.format(self.cport), 'switchport', 
                   'vpc {}'.format(self.cport), 'interface {}'.format(tport), 'channel-group {} force'.format(self.cport), 'end']
            self.multi_cmd(cmd)


if __name__ == '__main__':
    a = PortChannel(ip="x.x.x.x", username="", passwd="", tport='Ethernet1/36')
    a.del_channel()
