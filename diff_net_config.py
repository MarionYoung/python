#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/28 11:19
# @Author  : Marion

import datetime
import difflib
import paramiko
import logging
import re
import telnetlib
import sys
import subprocess
import traceback
import filecmp

logging.basicConfig(format="%(asctime)s %(threadName)s %(thread)d %(message)s", level=logging.INFO)

class CheckNetConfig:
    def __init__(self, ip, username='', passwd='', port=22):
        self.ip = ip
        self.user = username
        self.passwd = passwd
        self.port = port
        self.end_symbol = '>'
        self.before_symbol = '<'

    def ssh_conn(self):
        '''创建ssh连接'''
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, port=self.port, username=self.user, password=self.passwd, look_for_keys=False,
                        timeout=None, )
            return ssh
        except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException):
        	# ssh 连接不成功时，则使用telnet
            vendor = self.check_vendor()
            if vendor == 'H3C':
                cmd = 'display current-configuration'
            else:
                cmd = 'show running-config'
            print(cmd)
            tn = telnetlib.Telnet(self.ip, timeout=10)
            tn.set_debuglevel(2)  # 设置日志级别
            tn.read_until(b'Username:')
            tn.write(self.user.encode('ascii') + b'\n')
            tn.read_until(b'Password:')
            tn.write(self.passwd.encode('ascii') + b'\n')
            output = tn.read_until(b'failed', timeout=2)
            if b'failed' in output:
                tn.close()
                logging.error('{} Authentication failed'.format(self.ip))
                sys.exit(4)
            tn.read_until(self.end_symbol.encode('ascii'), timeout=5)
            tn.write(cmd.encode('ascii') + b'\n')
            result = tn.read_until(self.before_symbol.encode('ascii'))
            tn.close()
            return result
        except Exception as e:
            print(traceback.format_exc()) # 调试
            ssh.close()
            logging.error(e)
            sys.exit(4)

    def check_vendor(self):
        '''判断网络设备供应商'''
        h3c_pattern = 'H3C'
        h3c_regx = re.compile(h3c_pattern)
        cisco_pattern = 'Cisco'
        cisco_regx = re.compile(cisco_pattern)
        tmp_result = subprocess.Popen('snmpwalk -v2c -c {} {} 1.3.6.1.2.1.1.1'.format('yygtbudp,.', self.ip),
                                      shell=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        stdout, stderr = tmp_result.communicate()
        if stderr is None:
            tmp_result = subprocess.Popen('snmpwalk -v2c -c {} {} 1.3.6.1.2.1.1.1'.format('public.', self.ip),
                                          shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            stdout, stderr = tmp_result.communicate()
            if stderr is None:
                logging.error('Command snmpwalk run faild {}'.format(stderr))
                sys.exit(4)

        stdout = stdout.decode()
        h3c_result = h3c_regx.search(stdout)
        cisco_result = cisco_regx.search(stdout)

        if h3c_result:
            return 'H3C'
        elif cisco_result:
            return 'Cisco'

    def do_cmmd(self, cmd):
        '''执行命令获取结果'''
        remote_tool = self.ssh_conn()
        if isinstance(remote_tool, paramiko.SSHClient):
            stdin, stdout, stderr = remote_tool.exec_command(cmd)
            result = stdout.read()
            remote_tool.close()
            return result
        else:
            result = remote_tool
            return result

    def save_file(self):
        '''将命令执行的结果保存在一个文件'''
        name = '{}_{:%F}.txt'.format(self.ip, datetime.datetime.now())
        vendor = self.check_vendor()
        if vendor == 'H3C':
            cmd = 'display current-configuration'
        else:
            cmd = 'show running-config'

        tmp_result = self.do_cmmd(cmd).decode()
        tmp_result = tmp_result.splitlines()
        for i, v in enumerate(tmp_result):
            if 'version' in v:
                tmp_result = tmp_result[i:]
                break

        for idx, v in enumerate(tmp_result[::-1]):
            if 'clock-period' in v:
                tmp_result.pop(-idx - 1)
                break

        tmp_result = '\r\n'.join(tmp_result)
        if tmp_result is not None:
            with open(r'/root/python3/{}'.format(name), 'w') as f:
                f.write(tmp_result)
            return name
        else:
            logging.error(tmp_result)

    def readfile(self, filename):
        '''读取文件内容，并按行分隔'''
        try:
            with open(filename, 'r') as f:
                text = f.read().splitlines()
                return text
        except IOError as error:
            logging.error('Read {} file Error: {}'.format(filename, error))

    def files_compare(self):
        '''比较两个文件的差异性'''
        file1 = r'/root/python3/tt.txt'
        file2 = r'/root/python3/{}'.format(self.save_file())
        if not filecmp.cmp(file1, file2):
            text1_lines = self.readfile(file1)
            text2_lines = self.readfile(file2)
            d = difflib.HtmlDiff()
            compare_result = d.make_file(text1_lines, text2_lines)
            return compare_result
        filecmp.clear_cache()

    def save_compare_result(self):
        '''将比较的结果保存在一个html 文件中'''
        result = self.files_compare()
        if result is not None:
            with open(r'/root/python3/result.html', 'w') as f:
                f.write(result)
        else:
            logging.info('files equal.')

if __name__ == '__main__':
    a = CheckNetConfig('x.x.x.x', username='xxxx', passwd='xxx')
    a.save_compare_result()