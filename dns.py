#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/23 8:38
# @Author  : Marion

from pypsexec.client import Client
import logging

SPLIT_LINE = '--------                  ---------- ---------            ----------      ----------'

logging.basicConfig(format="%(asctime)s %(threadName)s %(thread)d %(message)s", level=logging.INFO)

class DnsResolve:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.passwd = password

    def con_win(self):
        '''连接windows'''
        conn = Client(self.ip, username=self.user, password=self.passwd)
        return conn

    def do_cmd(self):
        '''执行命令，查询dns 所有类型'''
        c = self.con_win()
        c.connect()
        arg = "Get-DnsServerResourceRecord -ZoneName 'glodon.com'"

        try:
            c.create_service()
            stdout, stderr, rc = c.run_executable("powershell.exe", arguments=arg, timeout_seconds=600)

            if len(stderr.decode('gbk')) > 0:
                logging.error(stderr.decode('gbk'))
            else:
                tmp_result = stdout.decode('gbk')

                return tmp_result.split(SPLIT_LINE)[-1]
        except Exception as e:
            logging.error(e)

        finally:
            c.remove_service()
            # c.cleanup()
            c.disconnect()

    def parse_result(self):
        '''将命令执行的结果，解析A、CNAME并生成字典'''
        result_d = {}
        tmp_result = self.do_cmd()
        for lines in tmp_result.split('\r\n'):
            ips = set()
            record = {}
            line = lines.split()
            if len(line) == 5 and ('A' in line or 'CNAME' in line):
                domain, rcd_type, _, _, recordData = line
                domain = "{}.glodon.com".format(domain)
                if result_d.get(domain, None):
                    result_d[domain][rcd_type].add(recordData)
                ips.add(recordData)
                record[rcd_type] = ips
                result_d[domain] = record
        return result_d

if __name__ == '__main__':
    try:
        ins = DnsResolve('x.x.x.x', user='xxx', password='xxx')
        print(ins.parse_result())
    except Exception as e:
        logging.error(e)