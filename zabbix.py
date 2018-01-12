#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import requests
import sys
from ConfigParser import RawConfigParser


# login zabbix
def login(username, password):

    data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
                },
            "id": 0
            }

    token = result(data)
    return token


def get_hostgroups(token):

    data = {
            "jsonrpc":"2.0",
            "method":"hostgroup.get",
            "params":{
                "output":["groupid","name"],
                },
            "auth":token, 
            "id":1,
            }

    host_group = {}
    for i in result(data):
        key = i['name']
        value = i['groupid']
        host_group[key] = value
    return host_group


def get_hosts(token, groupid):

    data = {
            "jsonrpc":"2.0",
            "method":"host.get",
            "params":{
                "output":["hostid","name"],
                "groupids":groupid,
                },
            "auth":token, 
            "id":1,
            }

    hosts = {}
    for i in result(data):
        key = i['name'].replace("e", ".")
        value = i['hostid']
        hosts[key] = value
    return hosts


def get_items(token, hostid):

    data = {
            "jsonrpc":"2.0",
            "method":"item.get",
            "params":{
                "output":["itemids","key_"],
                "hostids":hostid,
                },
            "auth":token, 
            "id":1,
            }

    items = {}
    for i in result(data):
        key = i['key_']
        value = i['itemid']
        items[key] = value
    return items


def get_history_data(token, itemid, time_from, history=3, limit=1):

    data = {
            "jsonrpc":"2.0",
            "method":"history.get",
            "params":{
                "output":"extend",
                "history":history,
                "itemids":itemid,
                "time_from":time_from,
                "limit":limit,
                "sortfield": "clock",
                "sortorder": "DESC",
                },
            "auth":token,
            "id":1,
            }

    history_data = {}
    for i in result(data):
        key = i['clock']
        value = float(i['value'])
        history_data[key] = value
    return history_data



def result(data):

    config = RawConfigParser()
    config.read('conf.cfg')

    headers = {'Content-Type': 'application/json-rpc'}
    url = 'http://%s/zabbix/api_jsonrpc.php' %config.get('zabbix', 'ip')
    request = requests.post(url=url,headers=headers,data=json.dumps(data))

    try:
        result = json.loads(request.text)
        return result['result']
    except Exception as e:
        print result['error']['message']
        print result['error']['data'], "\n"
        sys.exit(1)
