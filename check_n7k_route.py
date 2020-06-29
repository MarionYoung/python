#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/27 15:44
# @Author  : Marion

import paramiko
import re

class CheckN7kRoute:
    def __init__(self, ip, username, passwd, port=22):
        self.ip = ip
        self.user = username
        self.passwd = passwd
        self.port = port

    def conn(self):
        '''创建ssh连接'''
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, port=self.port, username=self.user, password=self.passwd, look_for_keys=False,
                        timeout=None, )
            return ssh
        except Exception as e:
            return e

    def get_resutl(self, command):
        '''执行命令获取结果'''
        ssh = self.conn()
        if isinstance(ssh, paramiko.SSHClient):
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read()
            ssh.close()
            return result
        else:
            print(type(ssh), ssh)

    def parse_result(self):
        '''从命令中获取的结果，解析 *via 10.0.7.121, '''
        pattern = '(?<=via\s)(?:\d+.){3}\d+'
        regx = re.compile(pattern)
        cmd = 'show ip route 0.0.0.0'
        tmp_result = self.get_resutl(cmd).strip().decode()
        result = regx.search(tmp_result)
        if result:
            return result.group()

if __name__ == '__main__':
    a = CheckN7kRoute('x.x.x.x', username='xxx', passwd='xxx')
    print(a.parse_result())
