#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/8 10:21
# @Author  : Marion

import requests
import lxml
from bs4 import BeautifulSoup
from bs4.element import Tag
rsps1 = requests.get('https://github.com/login')
soup = BeautifulSoup(rsps1.text,features='lxml')
tag = soup.find(name='input',attrs={'name':'authenticity_token'})
authenticity_token = tag.get('value')
cookies1 = rsps1.cookies.get_dict()
rsps1.close()

form_data = {
    'authenticity_token':authenticity_token,
    'utf8':'',
    'login':'jzmb',
    'password':'www.zx.c0m',
    'commit':'Sign in'
}
rsps2 = requests.post(
    url='https://github.com/session',
    data=form_data,
    cookies=cookies1

)
cookies2 = rsps2.cookies.get_dict()
cookies1.update(cookies2)
rsps3 = requests.get('https://github.com/settings/repositories', cookies=cookies1)
soup = BeautifulSoup(rsps3.text,features='lxml')
list_group = soup.find(name='div',class_='listgroup')
print(type(list_group)
for child in list_group.children:
    if isinstance(child,Tag):
        project_tag = child.find(name='a',class_='mr-1')
        size_tag = child.find(name='small')
        temp = 'Project:{}({}) path:{}'.format(project_tag.get('href'),size_tag.string,project_tag.string)
        print(temp)
