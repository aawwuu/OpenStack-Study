#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import requests
import sys
from ConfigParser import RawConfigParser

class Zabbix():
    def __init__(self):
        config = RawConfigParser()
        config.read('conf.cfg')
        self.username = config.get('zabbix', 'username')
        self.password = config.get('zabbix', 'password')
        self.headers = {'Content-Type': 'application/json-rpc'}
        self.url = 'http://%s/zabbix/api_jsonrpc.php' %config.get('zabbix', 'ip')
        self.token = self.login()
    
    def login(self):
        # login zabbix
        data = {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.username,
                    "password": self.password
                    },
                "id": 0
                }

        token = self.result(data)
        return token


    def get_hostgroups(self):

        data = {
                "jsonrpc":"2.0",
                "method":"hostgroup.get",
                "params":{
                    "output":["groupid","name"],
                    },
                "auth":self.token, 
                "id":1,
                }

        host_group = {}
        for i in self.result(data):
            key = i['name']
            value = i['groupid']
            host_group[key] = value
        return host_group

    def get_hosts(self, groupid):

        data = {
                "jsonrpc":"2.0",
                "method":"host.get",
                "params":{
                    "output":["hostid","name"],
                    "groupids":groupid,
                    },
                "auth":self.token, 
                "id":1,
                }

        hosts = {}
        for i in self.result(data):
            key = i['name'].replace("e", ".")
            value = i['hostid']
            hosts[key] = value
        return hosts


    def get_items(self, hostid):

        data = {
                "jsonrpc":"2.0",
                "method":"item.get",
                "params":{
                    "output":["itemids","key_"],
                    "hostids":hostid,
                    },
                "auth":self.token, 
                "id":1,
                }

        items = {}
        for i in self.result(data):
            key = i['key_']
            value = i['itemid']
            items[key] = value
        return items


    def get_history_data(self, itemid, time_from, history=3, limit=1):

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
                "auth":self.token,
                "id":1,
                }

        history_data = {}
        for i in self.result(data):
            key = i['clock']
            value = float(i['value'])
            history_data[key] = value
        return history_data


    def get_template(self):

        data = {
                    "jsonrpc": "2.0",
                    "method": "template.get",
                    "params": {
                        "output": ["name", "templateids"],
                        },
                    "auth": self.token,
                    "id": 1
                }


        return self.result(data)

    def get_graph(self, hostids, itemids):
        data = {
                    "jsonrpc": "2.0",
                    "method": "graph.get",
                    "params": {
                        "output": "extend",
                        "hostids": hostids,
                        "itemids": itemids,
                        "sortfield": "name"
                    },
                    "auth": self.token,
                    "id": 1
                }

        return self.result(data)[0]['graphid']


    def create_screen(self,name,hsize,vsize, screenitems):
        data = {
                    "jsonrpc": "2.0",
                    "method": "screen.create",
                    "params": {
                        "name": name,
                        "hsize": hsize,
                        "vsize": vsize,
                        "screenitems": screenitems
                        
                    },
                    "auth": self.token,
                    "id": 1
        }
        return self.result(data)['screenids']

    def create_screen_item(self, screenid, resourceid, x, y):
        data = {
                    "jsonrpc": "2.0",
                    "method": "screenitem.create",
                    "params": {
                        "screenid": screenid,
                        "resourcetype": 0,
                        "resourceid": resourceid,
                        "x": x,
                        "y": y
                    },
                    "auth": self.token,
                    "id": 1
                }
        return self.result(data)


    def result(self, data):
        request = requests.post(url=self.url,headers=self.headers,data=json.dumps(data))

        try:
            result = json.loads(request.text)
            return result['result']
        except Exception as e:
            print result['error']['message']
            print result['error']['data'], "\n"
            sys.exit(1)